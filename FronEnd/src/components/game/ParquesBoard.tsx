import React, { useState } from 'react';
import type { GameState } from '../../types/game';
import GameTokens from './GameTokens';
import tableroImage from './tablero.jpeg';
import styles from './GameBoard.module.css';
import { useBoardDimensions } from '../../hooks/useBoardDimensions';

interface ParquesBoardProps {
  gameState: GameState;
  onRefresh: () => Promise<void>;
  diceMenuComponent?: React.ReactNode;
  onPieceSelected?: (pieceId: string) => void;
}

export const ParquesBoard: React.FC<ParquesBoardProps> = ({ gameState, onRefresh, diceMenuComponent, onPieceSelected }) => {
  const boardRef = React.useRef<HTMLDivElement>(null!);
  const [selectedPieceId, setSelectedPieceId] = useState<string | null>(null);
  const boardDimensions = useBoardDimensions(boardRef, tableroImage);

  const handlePieceClick = (pieceId: string) => {
    setSelectedPieceId(pieceId === selectedPieceId ? null : pieceId);
    // Notificar al padre que se seleccionó una ficha
    if (onPieceSelected && pieceId !== selectedPieceId) {
      onPieceSelected(pieceId);
    }
  };

  const handlePositionClick = async (_position: number) => {
    if (!selectedPieceId) return;
    // Movement handled by API in GameBoard flow; just clear selection and refresh
    setSelectedPieceId(null);
    await onRefresh();
  };

  return (
    <div className={styles.boardWrapper}>
      <div
        ref={boardRef}
        className={styles.boardContainer}
        style={{
          backgroundImage: `url(${tableroImage})`,
        }}
      >
        {boardDimensions.imageWidth > 0 && (
          <div
            className={styles.imageOverlay}
            style={{
              left: `${boardDimensions.imageX}px`,
              top: `${boardDimensions.imageY}px`,
              width: `${boardDimensions.imageWidth}px`,
              height: `${boardDimensions.imageHeight}px`,
            }}
          />
        )}

        <GameTokens
          gameState={gameState}
          boardDimensions={boardDimensions}
          selectedPieceId={selectedPieceId}
          onPieceClick={handlePieceClick}
          onPositionClick={handlePositionClick}
          diceValues={gameState?.last_dice1 !== null && gameState?.last_dice1 !== undefined &&
                      gameState?.last_dice2 !== null && gameState?.last_dice2 !== undefined
            ? [Number(gameState.last_dice1) + Number(gameState.last_dice2)] 
            : []}
          activePlayerId={gameState.current_player_id}
        />
        
        {/* Menú de selección de dados - superpuesto en el centro */}
        {diceMenuComponent}
      </div>
    </div>
  );
};

export default ParquesBoard;