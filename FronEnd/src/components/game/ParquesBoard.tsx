import React, { useState } from 'react';
import { authService } from '../../services/authService';
import type { GameState } from '../../types/game';
import GameTokens from './GameTokens';
import tableroImage from './tablero.jpeg';
import styles from './GameBoard.module.css';
import { useBoardDimensions } from '../../hooks/useBoardDimensions';

export const ParquesBoard: React.FC<{ gameState: GameState; onRefresh: () => Promise<void> }> = ({ gameState, onRefresh }) => {
  const boardRef = React.useRef<HTMLDivElement>(null!);
  const [selectedPieceId, setSelectedPieceId] = useState<string | null>(null);
  const myPlayerId = authService.getUser() ? String(authService.getUser()!.id) : null;
  const boardDimensions = useBoardDimensions(boardRef, tableroImage);

  const handlePieceClick = (pieceId: string) => {
    setSelectedPieceId(pieceId === selectedPieceId ? null : pieceId);
  };

  const handlePositionClick = async (position: number) => {
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
          diceValues={gameState?.last_dice_value ? [gameState.last_dice_value] : []}
          activePlayerId={gameState.current_player_id}
        />
      </div>
    </div>
  );
};

export default ParquesBoard;