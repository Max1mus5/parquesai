import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, RefreshCw, Users, Crown, Plus, Play } from 'lucide-react';
import { gameService} from '../../services/gameService';
import { iaService } from '../../services/IAService';
// removed unused imports
import { type GameState, type DiceResult } from '../../types/game';
import { PlayersSidebar } from './PlayersSidebar';
import { GameDetails } from './GameDetails';
import { DicePanel } from './DicePanel';
import { Loading } from '../common/Loading';
import { ParquesBoard } from './ParquesBoard';
import { AddBotModal } from './AddBotModal';
import { RecommendationsPanel } from './RecommendationsPanel';
import { DiceSelectionMenu } from './DiceSelectionMenu';
import styles from './GameBoard.module.css';

export const GameBoard: React.FC = () => {
  const navigate = useNavigate();
  const { gameId } = useParams<{ gameId: string }>();
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [startingGame, setStartingGame] = useState(false);
  const [showAddBotModal, setShowAddBotModal] = useState(false);
  const [showDiceMenu, setShowDiceMenu] = useState(false);
  const [currentDiceResult, setCurrentDiceResult] = useState<DiceResult | null>(null);

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

  const [availableDiceValues, setAvailableDiceValues] = useState<number[]>([]);
  const [selectedPieceForMenu, setSelectedPieceForMenu] = useState<string | null>(null);

  const handleDiceRolled = (diceResult: DiceResult) => {
    setCurrentDiceResult(diceResult);
    // Guardar todas las opciones de dados disponibles
    setAvailableDiceValues([diceResult.dice1, diceResult.dice2, diceResult.total]);
    // NO mostramos el menú aquí, esperamos a que seleccione una ficha
  };

  const handlePieceSelected = (pieceId: string) => {
    // Cuando selecciona una ficha, mostramos el menú con las opciones
    setSelectedPieceForMenu(pieceId);
    setShowDiceMenu(true);
  };

  const handleDiceSelection = async (diceValue: number) => {
    if (!gameId || !gameState || !selectedPieceForMenu || !currentDiceResult) return;
    
    setShowDiceMenu(false);
    
    try {
      // Calcular nuevos valores disponibles ANTES de mover
      const newValues = (() => {
        // Si usó el total, se acaban todos los valores
        if (diceValue === currentDiceResult.total) {
          return [];
        }
        
        // Si usó dice1, remover dice1 y total, dejar dice2
        if (diceValue === currentDiceResult.dice1) {
          return availableDiceValues.filter(v => v === currentDiceResult.dice2);
        }
        
        // Si usó dice2, remover dice2 y total, dejar dice1
        if (diceValue === currentDiceResult.dice2) {
          return availableDiceValues.filter(v => v === currentDiceResult.dice1);
        }
        
        return availableDiceValues;
      })();
      
      // Es el último movimiento si después de este no quedan valores
      // O si solo queda un valor individual (no el total)
      const willBeLastMove = newValues.length === 0;
      
      // Ejecutar el movimiento
      await gameService.movePiece(gameId, selectedPieceForMenu, diceValue, undefined, willBeLastMove);
      
      setAvailableDiceValues(newValues);
      
      // Limpiar la ficha seleccionada
      setSelectedPieceForMenu(null);
      
      // Actualizar el estado del juego
      await fetchGameState();
      
    } catch (error) {
      console.error('Error al mover ficha:', error);
      setError(error instanceof Error ? error.message : 'Error al mover ficha');
      // Restaurar el menú si hubo error
      setShowDiceMenu(true);
    }
  };

  useEffect(() => {
    fetchGameState();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [gameId]);

  // Auto-ejecutar turno del bot cada 3 segundos
  useEffect(() => {
    const interval = setInterval(() => {
      if (gameId && gameState && gameState.status === 'active') {
        const currentPlayer = gameState.players.find(p => p.id === gameState.current_player_id);
        
        // Si es turno de un bot (el nombre empieza con "Bot_"), ejecutar su turno
        if (currentPlayer && currentPlayer.name.startsWith('Bot_')) {
          iaService.executeBotTurn(gameId)
            .then(() => {
              // Actualiza el estado del juego después de ejecutar el turno del bot
              gameService.getGameState(gameId)
                .then((state) => setGameState(state))
                .catch((err) => console.error('Error updating game state after bot turn:', err));
            })
            .catch((err) => {
              // Si hay error (ej: bot ya jugó), continúa sin hacer nada
              console.log('Bot turn already processed or error:', err.message);
            });
        }
      }
    }, 3000); // Cada 3 segundos

    return () => clearInterval(interval);
  }, [gameId, gameState]);

  // Actualización periódica del estado del juego
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
              
              {/* Botón para forzar turno del bot */}
              {gameState && gameState.status === 'active' && (() => {
                const currentPlayer = gameState.players.find(p => p.id === gameState.current_player_id);
                return currentPlayer && currentPlayer.name.startsWith('Bot_') ? (
                  <button
                    onClick={async () => {
                      try {
                        await iaService.executeBotTurn(String(gameState.id));
                        await fetchGameState();
                      } catch (err) {
                        console.error('Error forzando turno del bot:', err);
                        setError(err instanceof Error ? err.message : 'Error al ejecutar turno del bot');
                      }
                    }}
                    className={styles.addBotButton}
                    title="Forzar al bot a jugar su turno"
                  >
                    <Play className="w-4 h-4" />
                    <span>Jugar Bot</span>
                  </button>
                ) : null;
              })()}
              
              {gameState && gameState.status === 'waiting' && (
                <>
                  <button
                    onClick={() => setShowAddBotModal(true)}
                    className={styles.addBotButton}
                  >
                    <Plus className="w-4 h-4" />
                    <span>Agregar Bot</span>
                  </button>
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
                      Últimos dados: {gameState.last_dice1 !== null && gameState.last_dice1 !== undefined &&
                                       gameState.last_dice2 !== null && gameState.last_dice2 !== undefined
                        ? `${Number(gameState.last_dice1)} + ${Number(gameState.last_dice2)}`
                        : 'Aún no lanzados'}
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

                <ParquesBoard 
                  gameState={gameState} 
                  onRefresh={fetchGameState}
                  onPieceSelected={handlePieceSelected}
                  diceMenuComponent={
                    showDiceMenu && currentDiceResult && availableDiceValues.length > 0 ? (
                      <DiceSelectionMenu
                        dice1={availableDiceValues.includes(currentDiceResult.dice1) ? currentDiceResult.dice1 : 0}
                        dice2={availableDiceValues.includes(currentDiceResult.dice2) ? currentDiceResult.dice2 : 0}
                        total={availableDiceValues.includes(currentDiceResult.total) ? currentDiceResult.total : 0}
                        isPair={currentDiceResult.is_pair}
                        onSelectDice1={() => availableDiceValues.includes(currentDiceResult.dice1) && handleDiceSelection(currentDiceResult.dice1)}
                        onSelectDice2={() => availableDiceValues.includes(currentDiceResult.dice2) && handleDiceSelection(currentDiceResult.dice2)}
                        onSelectTotal={() => availableDiceValues.includes(currentDiceResult.total) && handleDiceSelection(currentDiceResult.total)}
                        onClose={() => {
                          setShowDiceMenu(false);
                          setSelectedPieceForMenu(null);
                        }}
                      />
                    ) : null
                  }
                />
              </div>

              <div className={styles.sidebar}>
                <DicePanel 
                  gameState={gameState} 
                  onRefresh={fetchGameState}
                  onDiceRolled={handleDiceRolled}
                />
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

