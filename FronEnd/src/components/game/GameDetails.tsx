import React from 'react';
import type { GameState } from '../../types/game';
import { Dice5 } from 'lucide-react';
import styles from './GameBoard.module.css';

export const GameDetails: React.FC<{ gameState: GameState }> = ({ gameState }) => {
  return (
    <div className={`card ${styles.detailsCard}`}>
      <h2 className={styles.detailsTitle}>Detalles del Juego</h2>
      <div className={styles.detailsList}>
        <div className={styles.detailItem}>
          <span className={styles.detailLabel}>Estado:</span>
          <span className={styles.detailValue}>{gameState.status.replace('_', ' ')}</span>
        </div>
        <div className={styles.detailItem}>
          <span className={styles.detailLabel}>Último turno:</span>
          <span>
            {gameState.current_player_id
              ? gameState.players.find((p) => p.id === gameState.current_player_id)?.name
              : 'Sin turno activo'}
          </span>
        </div>
        <div className={styles.detailItem}>
          <span className={styles.detailLabel}>Último dado lanzado:</span>
          <div className={styles.diceValue}>
            <Dice5 className="w-4 h-4 text-text-secondary" />
            <span>{gameState.last_dice_value ?? '—'}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GameDetails;