import React, { useState } from 'react';
import { gameService } from '../../services/gameService';
import type { GameState, DiceResult } from '../../types/game';
import { useAuth } from '../../hooks/useAuth';
import styles from './GameBoard.module.css';

interface DicePanelProps {
  gameState: GameState;
  onRefresh: () => Promise<void>;
  onDiceRolled?: (diceResult: DiceResult) => void;
}

export const DicePanel: React.FC<DicePanelProps> = ({ gameState, onRefresh, onDiceRolled }) => {
  const { user } = useAuth();
  const [rollingDice, setRollingDice] = useState(false);
  const [validMoves, setValidMoves] = useState<any>(null);

  // Encontrar el player_id del usuario actual en este juego
  // Los players tienen un 'id' que es el player_id del game_engine
  const currentPlayer = gameState.players.find(p => p.id === gameState.current_player_id);
  const isBot = currentPlayer?.name.startsWith('Bot_') || false;
  
  // Verificar si es el turno del usuario actual
  // Comparamos el current_player_id con el id del jugador (no con user.id)
  const myPlayer = gameState.players.find(p => !p.is_ai && p.name === user?.username);
  const isMyTurn = myPlayer && gameState.current_player_id === myPlayer.id;

  const rollDice = async () => {
    if (!gameState?.id) return;
    setRollingDice(true);
    try {
      const diceResult = await gameService.rollDice(String(gameState.id));
      await onRefresh();
      
      // Llamar callback para que el padre maneje el menú
      if (onDiceRolled) {
        onDiceRolled(diceResult);
      }
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
    <>
      <div className={`card ${styles.diceCard}`}>
        <h2 className={styles.detailsTitle}>Control de Dado</h2>
        
        {!isMyTurn && (
          <div className={styles.turnWarning}>
            {isBot ? '🤖 Turno del Bot...' : `⏳ Turno de ${currentPlayer?.name || 'otro jugador'}`}
          </div>
        )}
        
        <div className={styles.dicePanelRow}>
          <button 
            className={styles.diceButton} 
            onClick={rollDice} 
            disabled={rollingDice || !isMyTurn || gameState.status !== 'active'}
            title={!isMyTurn ? 'No es tu turno' : 'Lanzar dados'}
          >
            {rollingDice ? 'Tirando...' : 'Tirar dados'}
          </button>
          <div className={styles.diceInfo}>
            Dados: {gameState.last_dice1 !== null && gameState.last_dice1 !== undefined &&
                    gameState.last_dice2 !== null && gameState.last_dice2 !== undefined
              ? `${Number(gameState.last_dice1)} + ${Number(gameState.last_dice2)}${gameState.is_pair ? ' (PAR)' : ''}` 
              : '—'}
          </div>
          <button 
            className={styles.diceButton} 
            onClick={handlePassTurn} 
            disabled={rollingDice || !isMyTurn || gameState.status !== 'active'}
            title={!isMyTurn ? 'No es tu turno' : 'Pasar turno'}
          >
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
    </>
  );
};

export default DicePanel;