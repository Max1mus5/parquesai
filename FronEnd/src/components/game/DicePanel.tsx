import React, { useState } from 'react';
import { gameService } from '../../services/gameService';
import type { GameState } from '../../types/game';
import styles from './GameBoard.module.css';

export const DicePanel: React.FC<{ gameState: GameState; onRefresh: () => Promise<void> }> = ({ gameState, onRefresh }) => {
  const [rollingDice, setRollingDice] = useState(false);
  const [validMoves, setValidMoves] = useState<any>(null);

  const rollDice = async () => {
    if (!gameState?.id) return;
    setRollingDice(true);
    try {
      const diceValue = await gameService.rollDice(String(gameState.id));
      await onRefresh();
      const moves = await gameService.getValidMoves(String(gameState.id), diceValue);
      setValidMoves(moves);
    } catch (err) {
      setValidMoves({ error: err instanceof Error ? err.message : 'Error desconocido' });
    } finally {
      setRollingDice(false);
    }
  };

  const handlePassTurn = async () => {
    if (!gameState?.id) return;
    try {
      await gameService.passTurn(String(gameState.id));
      setValidMoves(null);
      await onRefresh();
    } catch {
      // noop
    }
  };

  return (
    <div className={`card ${styles.diceCard}`}>
      <h2 className={styles.detailsTitle}>Control de Dado</h2>
      <div className={styles.dicePanelRow}>
        <button className={styles.diceButton} onClick={rollDice} disabled={rollingDice}>
          {rollingDice ? 'Tirando...' : 'Tirar dados'}
        </button>
        <div className={styles.diceInfo}>Dado: {gameState.last_dice_value ?? '—'}</div>
        <button className={styles.diceButton} onClick={handlePassTurn} disabled={rollingDice}>
          Pasar turno
        </button>
      </div>
      {validMoves && (
        <div className={styles.validMovesBox}>
          <div className={styles.validMovesTitle}>Movimientos válidos:</div>
          <pre className={styles.validMovesPre}>{JSON.stringify(validMoves, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default DicePanel;