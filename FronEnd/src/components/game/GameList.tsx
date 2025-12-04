import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Play, Users, Calendar, Lock, Globe, X } from 'lucide-react';
import { gameService } from '../../services/gameService';
import type { Game } from '../../types/game';
import { Loading } from '../common/Loading';
import styles from './GameList.module.css';

type PlayerColor = 'red' | 'blue' | 'yellow' | 'green';

export const GameList: React.FC = () => {
  const navigate = useNavigate();
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [joiningGameId, setJoiningGameId] = useState<string | null>(null);
  const [showColorModal, setShowColorModal] = useState(false);
  const [selectedGame, setSelectedGame] = useState<{ id: string; isPrivate: boolean } | null>(null);
  const [selectedColor, setSelectedColor] = useState<PlayerColor | null>(null);

  useEffect(() => {
    fetchAvailableGames();
  }, []);

  const fetchAvailableGames = async () => {
    try {
      setLoading(true);
      setError(null);
      const availableGames = await gameService.getAvailableGames();
      setGames(availableGames);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar juegos');
      console.error('Error fetching games:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleJoinGame = async (gameId: string, isPrivate: boolean) => {
    setSelectedGame({ id: gameId, isPrivate });
    setShowColorModal(true);
  };

  const confirmJoinGame = async () => {
    if (!selectedGame || !selectedColor) return;

    try {
      setJoiningGameId(selectedGame.id);
      
      const joinRequest = {
        color: selectedColor,
        password: selectedGame.isPrivate ? prompt('Ingresa la contraseña del juego:') || undefined : undefined,
      };

      await gameService.joinGame(selectedGame.id, joinRequest);
      setShowColorModal(false);
      setSelectedGame(null);
      setSelectedColor(null);
      navigate(`/game/${selectedGame.id}`);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error al unirse al juego';
      
      // Si el error es que ya está unido al juego, navega al juego directamente
      if (errorMessage.toLowerCase().includes('already') || errorMessage.toLowerCase().includes('ya está')) {
        setShowColorModal(false);
        setSelectedGame(null);
        setSelectedColor(null);
        navigate(`/game/${selectedGame.id}`);
      } else {
        setError(errorMessage);
        console.error('Error joining game:', err);
      }
    } finally {
      setJoiningGameId(null);
    }
  };

  const cancelColorSelection = () => {
    setShowColorModal(false);
    setSelectedGame(null);
    setSelectedColor(null);
  };

  const handleCreateGame = () => {
    navigate('/create-game');
  };

  if (loading) {
    return <Loading />;
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.headerInner}>
          <div className={styles.headerLeft}>
            <button onClick={() => navigate('/dashboard')} className={styles.backButton}>
              <ArrowLeft className={styles.backIcon} />
            </button>
            <h1 className={styles.headerTitle}>Juegos Disponibles</h1>
          </div>
          <button onClick={handleCreateGame} className={styles.createButton}>
            <Play className={styles.createIcon} />
            <span>Crear Juego</span>
          </button>
        </div>
      </header>

      {/* Modal de Selección de Color */}
      {showColorModal && (
        <div className={styles.colorModal}>
          <div className={styles.modalContent}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>Selecciona tu color</h2>
              <button onClick={cancelColorSelection} className={styles.closeButton}>
                <X className="w-5 h-5 text-text-secondary" />
              </button>
            </div>

            <div className={styles.colorGrid}>
              {(['red', 'green', 'yellow', 'blue'] as PlayerColor[]).map((color) => {
                const colorStyles = {
                  red: { bg: '#ef4444', border: '#dc2626', text: '#ffffff' },
                  green: { bg: '#22c55e', border: '#16a34a', text: '#ffffff' },
                  yellow: { bg: '#eab308', border: '#ca8a04', text: '#1f2937' },
                  blue: { bg: '#3b82f6', border: '#2563eb', text: '#ffffff' },
                  
                };
                const colorNames = {
                  red: 'Rojo',
                  green: 'Verde',
                  yellow: 'Amarillo',
                  blue: 'Azul',
                };
                
                const style = colorStyles[color];
                const isSelected = selectedColor === color;

                return (
                  <button
                    key={color}
                    onClick={() => setSelectedColor(color)}
                    className={`${styles.colorButton} ${isSelected ? styles.selected : ''}`}
                    style={{
                      backgroundColor: style.bg,
                      borderColor: style.border,
                      color: style.text,
                    }}
                  >
                    <div className={styles.colorCircle}>
                      <div className={styles.colorDot}>●</div>
                      <div className={styles.colorName}>{colorNames[color]}</div>
                    </div>
                  </button>
                );
              })}
            </div>

            <div className={styles.modalActions}>
              <button onClick={cancelColorSelection} className={styles.cancelButton}>
                Cancelar
              </button>
              <button
                onClick={confirmJoinGame}
                disabled={!selectedColor || joiningGameId !== null}
                className={`btn-primary ${styles.confirmButton}`}
              >
                {joiningGameId ? 'Uniéndose...' : 'Confirmar'}
              </button>
            </div>
          </div>
        </div>
      )}

      <main className={styles.main}>
        {error && (
          <div className={styles.errorBox}>
            <p className={styles.errorText}>{error}</p>
          </div>
        )}

        {games.length === 0 ? (
          <div className={styles.emptyState}>
            <div className={styles.emptyEmoji}>🎮</div>
            <h2 className={styles.emptyTitle}>No hay juegos disponibles</h2>
            <p className={styles.emptySubtitle}>Sé el primero en crear una partida y espera a otros jugadores</p>
            <button onClick={handleCreateGame} className={styles.primaryButtonLg}>Crear Primer Juego</button>
          </div>
        ) : (
          <div className={styles.cardGrid}>
            {games.map((game) => (
              <div key={game.id} className={styles.card}>
                <div className={styles.cardHeader}>
                  <h3 className={styles.cardTitle}>{game.name}</h3>
                  <div className={styles.badgeRow}>
                    <span className={`${styles.badge} ${game.status === 'waiting' ? styles.badgeWaiting : game.status === 'in_progress' ? styles.badgeProgress : styles.badgeSuccess}`}>
                      {game.status === 'waiting' ? 'Esperando...' : game.status === 'in_progress' ? 'En Juego' : 'Finalizado'}
                    </span>
                  </div>
                </div>

                <div className={styles.infoList}>
                  <div className={styles.infoItem}>
                    <Users className={styles.infoIcon} />
                    <span className={styles.infoText}>{game.current_players}/{game.max_players} Jugadores</span>
                  </div>
                  <div className={styles.infoItem}>
                    <Calendar className={styles.infoIcon} />
                    <span className={styles.infoText}>
                      {new Date(game.created_at).toLocaleDateString('es-ES', { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                  <div className={styles.infoItem}>
                    {game.is_private ? (
                      <Lock className={styles.lockIcon} />
                    ) : (
                      <Globe className={styles.globeIcon} />
                    )}
                    <span className={styles.infoText}>{game.is_private ? 'Privado' : 'Público'}</span>
                  </div>
                </div>

                <div className={styles.progressWrap}>
                  <div className={styles.progressBg}>
                    <div className={styles.progressBar} style={{ width: `${(game.current_players / game.max_players) * 100}%` }} />
                  </div>
                </div>

                {game.status === 'waiting' && game.current_players < game.max_players ? (
                  <button onClick={() => handleJoinGame(game.id, game.is_private)} disabled={joiningGameId === game.id} className={styles.primaryButton}>
                    <Play className={styles.buttonIcon} />
                    <span>{joiningGameId === game.id ? 'Uniéndose...' : 'Unirse'}</span>
                  </button>
                ) : game.status === 'in_progress' ? (
                  <button onClick={() => handleJoinGame(game.id, game.is_private)} disabled={joiningGameId === game.id} className={styles.secondaryButton}>
                    <Play className={styles.buttonIcon} />
                    <span>{joiningGameId === game.id ? 'Uniéndose...' : 'Ver Juego'}</span>
                  </button>
                ) : (
                  <button disabled className={styles.secondaryButtonDisabled}>Juego Finalizado</button>
                )}
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};
