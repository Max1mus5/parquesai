import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, RefreshCw, Users, Crown, Plus } from 'lucide-react';
import { gameService} from '../../services/gameService';
import { iaService } from '../../services/IAService';
// removed unused imports
import { type GameState } from '../../types/game';
import { PlayersSidebar } from './PlayersSidebar';
import { GameDetails } from './GameDetails';
import { DicePanel } from './DicePanel';
import { Loading } from '../common/Loading';
import { ParquesBoard } from './ParquesBoard';
import { AddBotModal } from './AddBotModal';
import { RecommendationsPanel } from './RecommendationsPanel';
import styles from './GameBoard.module.css';

export const GameBoard: React.FC = () => {
  const navigate = useNavigate();
  const { gameId } = useParams<{ gameId: string }>();
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [startingGame, setStartingGame] = useState(false);
  const [showAddBotModal, setShowAddBotModal] = useState(false);

  const fetchGameState = async () => {
    if (!gameId) {
      setError('Juego no encontrado');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const state = await gameService.getGameState(gameId);
      setGameState(state);
      console.log(gameState)
      // Metadata fetch removed; not used in UI
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar el juego');
      console.error('Error fetching game state:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGameState();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [gameId]);

 /* useEffect(() => {
    const interval = setInterval(() => {
      if (gameId && gameState) {
        // Intenta ejecutar turno del bot cada 5 segundos
        iaService.executeBotTurn(gameId)
          .then(() => {
            // Actualiza el estado del juego después de ejecutar el turno del bot
            gameService.getGameState(gameId)
              .then((state) => setGameState(state))
              .catch((err) => console.error('Error updating game state after bot turn:', err));
          })
          .catch((err) => {
            // Si hay error (ej: no es turno del bot), continúa sin hacer nada
            console.error('Error executing bot turn:', err);
          });
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [gameId, gameState]);*/

  useEffect(() => {
    const interval = setInterval(() => {
      if (gameId) {
        // Fetch sin mostrar loading cada 10 segundos
        gameService.getGameState(gameId)
          .then((state) => setGameState(state))
          .catch((err) => console.error('Error updating game state:', err));
      }
    }, 10000);

    return () => clearInterval(interval);
  }, [gameId]);


  if (loading) {
    return <Loading />;
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.headerContent}>
          <div className={styles.headerInner}>
            <div className={styles.headerLeft}>
              <button onClick={() => navigate('/games')} className={styles.backButton}>
                <ArrowLeft className="w-5 h-5 text-text-primary" />
              </button>
              <div>
                <h1 className={styles.headerTitle}>Tablero de Juego</h1>
                {gameState && (
                  <p className={styles.headerSubtitle}>Juego #{gameState.id}</p>
                )}
              </div>
            </div>
            <div className={styles.headerActions}>
              <button onClick={fetchGameState} className={styles.refreshButton}>
                <RefreshCw className="w-4 h-4" />
                <span>Actualizar</span>
              </button>
              {gameState && gameState.status === 'waiting' && (
                <>
                  {/* <button
                    onClick={() => setShowAddBotModal(true)}
                    className={styles.addBotButton}
                  >
                    <Plus className="w-4 h-4" />
                    <span>Agregar Bot</span>
                  </button>*/}
                  <button
                    onClick={async () => {
                      if (!gameState) return;
                      setStartingGame(true);
                      try {
                        await gameService.startGame(String(gameState.id));
                        await fetchGameState();
                      } catch (err) {
                        setError(err instanceof Error ? err.message : 'Error al iniciar el juego');
                      } finally {
                        setStartingGame(false);
                      }
                    }}
                    className={styles.startButton}
                    disabled={startingGame}
                  >
                    {startingGame ? 'Iniciando...' : 'Iniciar juego'}
                  </button>
                </>
              )}
              {gameState && (
                <button
                  onClick={async () => {
                    try {
                      await gameService.leaveGame(String(gameState.id));
                      navigate('/games');
                    } catch (err) {
                      console.error('Error al abandonar el juego:', err);
                    }
                  }}
                  className={styles.leaveButton}
                >
                  Abandonar juego
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className={styles.main}>
        {error && (
          <div className={styles.errorAlert}>{error}</div>
        )}

        {gameState ? (
          <div className={styles.mainContent}>
            <section className={styles.gridSection}>
              <div className={`card ${styles.boardCard}`}>
                <div className={styles.boardHeader}>
                  <div>
                    <h2 className={styles.boardTitle}>Estado Actual</h2>
                    <p className={styles.boardSubtitle}>
                      Último dado: {gameState.last_dice_value ?? 'Aún no lanzado'}
                    </p>
                  </div>
                  <div className={styles.boardStats}>
                    <div className={styles.statItem}>
                      <Users className="w-4 h-4 text-text-secondary" />
                      <span className={styles.statText}>
                        {gameState.players.length} jugadores
                      </span>
                    </div>
                    {gameState.winner_id && (
                      <div className={styles.winnerBadge}>
                        <Crown className="w-4 h-4" />
                        <span className={styles.winnerText}>
                          Ganador:{' '}
                          {gameState.players.find((p) => p.id === gameState.winner_id)?.name ??
                            'Desconocido'}
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                <ParquesBoard gameState={gameState} onRefresh={fetchGameState} />
              </div>

              <div className={styles.sidebar}>
                <DicePanel gameState={gameState} onRefresh={fetchGameState} />
                <PlayersSidebar gameState={gameState} />
                <GameDetails gameState={gameState} />
                <RecommendationsPanel />

                {/* Estado (JSON) para depuración */}
                {/* <div className={`card ${styles.detailsCard}`}>
                  <h2 className={styles.detailsTitle}>Estado (JSON)</h2>
                  <pre className={styles.jsonBlock}>
                    {JSON.stringify(gameState, null, 2)}
                  </pre>
                </div> */}
              </div>
            </section>

            {/* <section className={`card ${styles.piecesSection}`}>
              <h2 className={styles.piecesTitle}>Piezas por Jugador</h2>
              <div className={styles.piecesGrid}>
                {gameState.players.map((player) => renderPlayerCard(player))}
              </div>
            </section> */}
          </div>
        ) : (
          <div className={styles.emptyState}>
            No se pudo cargar el estado del juego. Intenta nuevamente.
          </div>
        )}
      </main>

      {gameState && (
        <AddBotModal
          gameId={gameState.id}
          isOpen={showAddBotModal}
          onClose={() => setShowAddBotModal(false)}
          onBotAdded={fetchGameState}
        />
      )}
    </div>
  );
};

export default GameBoard;

