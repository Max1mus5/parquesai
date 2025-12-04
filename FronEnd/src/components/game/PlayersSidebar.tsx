import React from 'react';
import type { GameState } from '../../types/game';
import styles from './GameBoard.module.css';

export const PlayersSidebar: React.FC<{ gameState: GameState }> = ({ gameState }) => {
  return (
    <div className={`card ${styles.playersCard}`}>
      <h2 className={styles.playersTitle}>Jugadores</h2>
      <div className={styles.playersList}>
        {gameState.players.map((player) => (
          <div
            key={player.id}
            className={`${styles.playerItem} ${
              gameState.current_player_id === player.id ? styles.currentTurn : ''
            }`}
          >
            <div className={styles.playerHeader}>
              <div>
                <p className={styles.playerName}>{player.name}</p>
                <span className={styles.playerColor}>Color: {player.color}</span>
              </div>
              {gameState.current_player_id === player.id && (
                <span className={styles.turnBadge}>En turno</span>
              )}
            </div>
            <p className={styles.playerPieces}>
              Piezas activas: {
                player.pieces.filter((p) => p.status === 'board' || p.status === 'safe_zone').length
              }
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PlayersSidebar;