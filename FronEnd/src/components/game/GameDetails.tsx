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
          <span className={styles.detailLabel}>Últimos dados lanzados:</span>
          <div className={styles.diceValue}>
            <Dice5 className="w-4 h-4 text-text-secondary" />
            <span>
              {gameState.last_dice1 !== null && gameState.last_dice1 !== undefined && 
               gameState.last_dice2 !== null && gameState.last_dice2 !== undefined
                ? `${Number(gameState.last_dice1)} + ${Number(gameState.last_dice2)} = ${Number(gameState.last_dice1) + Number(gameState.last_dice2)}${gameState.is_pair ? ' (PAR ✓)' : ''}`
                : '—'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GameDetails;