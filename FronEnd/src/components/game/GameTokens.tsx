import React from 'react';
import { type GameState, type Piece, type Player } from '../../types/game';
import { useAuth } from '../../hooks/useAuth';
import { gameService } from '../../services/gameService';
import styles from './GameTokens.module.css';

interface BoardDimensions {
  imageWidth: number;
  imageHeight: number;
  imageX: number;
  imageY: number;
}

interface GameTokensProps {
  gameState: GameState;
  boardDimensions: BoardDimensions;
  selectedPieceId: string | null;
  onPieceClick: (pieceId: string) => void;
  onPositionClick: (position: number) => void;
  diceValues: number[];
  activePlayerId: string | null;
}


const GameTokens: React.FC<GameTokensProps> = ({ 
  gameState, 
  boardDimensions, 
  selectedPieceId,
  onPieceClick,
  onPositionClick,
  diceValues,
}) => {
  const { user } = useAuth();
  const myPlayerName = user ? user.username : null;
  const BOARD_SIZE = 72;
  // Meta simplificada: no se usa conteo; la meta es la posición 71 del tablero

  const COLOR_THEME: Record<string, { bg: string; text: string; border: string }> = {
    RED: { bg: '#ef4444', text: '#ffffff', border: '#dc2626' },
    BLUE: { bg: '#3b82f6', text: '#ffffff', border: '#2563eb' },
    GREEN: { bg: '#22c55e', text: '#ffffff', border: '#16a34a' },
    YELLOW: { bg: '#eab308', text: '#1f2937', border: '#ca8a04' },
  };

  const GOAL_ENTRY_POSITIONS: Record<string, number> = {
    YELLOW: 0,   // Casa base amarilla (posiciones 63-67, 0-11)
    BLUE: 17,    // Rotación 90° CCW
    GREEN: 34,     // Rotación 180°
    RED: 51,   // Rotación 270° CCW
  };

  // Calcular coordenadas para posiciones del tablero principal (0-67)
  // El tablero es circular, así que mapeamos las posiciones a coordenadas porcentuales
  const getBoardPositionCoords = (position: number): { x: number; y: number } => {
    // Normalizar posición (0-67)
    const normalizedPos = position % BOARD_SIZE;
    // Coordenadas base (CASA AMARILLA): 63-67 y 0-11 manuales
    const baseMap: Record<number, { x: number; y: number }> = {
      17: { x: 3, y: 53 },
      18: { x: 3, y: 60 },
      19: { x: 7, y: 60 },
      20: { x: 11.2, y: 60 },
      21: { x: 15.3, y: 60 },
     
      69: { x: 27.5, y: 50 },
      70: { x: 31.5, y: 50 },
      71: { x: 40, y: 50 },
      22: { x: 19, y: 60 },
      23: { x: 23, y: 60 },
      24: { x: 28, y: 61 },
      25: { x: 33, y: 63 },
      26: { x: 36.5, y: 66 },
      27: { x: 38.5, y: 70.5 },
      28: { x: 40, y: 75.3 },
      29: { x: 40, y: 79.5 },
      30: { x: 40, y: 83.5 },
      31: { x: 40, y: 87.5 },
      32: { x: 40, y: 92 },
      33: { x: 40, y: 96 },
    };

    // Si la posición está en el mapa base, devolver directamente
    if (normalizedPos in baseMap) return baseMap[normalizedPos];
    // Coordenadas derivadas por rotación manual (explícitas) para 12-62
    // 12-28 (rotación 90° CCW de segmento base) CORREGIDO (casa base amarilla)
    if (normalizedPos === 34) return { x: 53, y: 96 };
    if (normalizedPos === 35) return { x: 60, y: 96 };
    if (normalizedPos === 36) return { x: 60, y: 91.8 };
    if (normalizedPos === 37) return { x: 60, y: 87.8 };
    if (normalizedPos === 38) return { x: 60, y: 83.8 };
    if (normalizedPos === 39) return { x: 60, y: 80 };
    if (normalizedPos === 40) return { x: 60, y: 76 };
    if (normalizedPos === 41) return { x: 61, y: 71 };
    if (normalizedPos === 42) return { x: 63, y: 67 };
    if (normalizedPos === 43) return { x: 66, y: 63.5 };
    if (normalizedPos === 44) return { x: 70.5, y: 61.5 };
    if (normalizedPos === 45) return { x: 75.3, y: 60 };
    if (normalizedPos === 46) return { x: 79.5, y: 60 };
    if (normalizedPos === 47) return { x: 84, y: 60 };
    if (normalizedPos === 48) return { x: 88, y: 60 };
    if (normalizedPos === 49) return { x: 92, y: 60 };
    if (normalizedPos === 50) return { x: 96, y: 60 };
    // 29-45 (rotación 180°)
    if (normalizedPos === 51) return { x: 96, y: 47 };
    if (normalizedPos === 52) return { x: 96, y: 40 };
    if (normalizedPos === 53) return { x: 91.8, y: 40 };
    if (normalizedPos === 54) return { x: 87.8, y: 40 };
    if (normalizedPos === 55) return { x: 83.8, y: 40 };
    if (normalizedPos === 56) return { x: 79.6, y: 40 };
    if (normalizedPos === 57) return { x: 75.5, y: 40 };
    if (normalizedPos === 58) return { x: 70.5, y: 39 };
    if (normalizedPos === 59) return { x: 65.5, y: 37 };
    if (normalizedPos === 60) return { x: 62, y: 33.5 };
    if (normalizedPos === 61) return { x: 60, y: 29 };
    if (normalizedPos === 62) return { x: 59, y: 23.7 };
    if (normalizedPos === 63) return { x: 59, y: 19.5 };
    if (normalizedPos === 64) return { x: 59, y: 15.5 };
    if (normalizedPos === 65) return { x: 59, y: 11.5 };
    if (normalizedPos === 66) return { x: 59, y: 7 };
    if (normalizedPos === 67) return { x: 59, y: 3 };
    // 46-62 (rotación 270° CCW = 90° CW del segmento base anterior)
    if (normalizedPos === 0) return { x: 47, y: 3 };
    if (normalizedPos === 1) return { x: 40, y: 3 };
    if (normalizedPos === 2) return { x: 40, y: 7.2 };
    if (normalizedPos === 3) return { x: 40, y: 11.2 };
    if (normalizedPos === 4) return { x: 40, y: 15.2 };
    if (normalizedPos === 5) return { x: 40, y: 19 };
    if (normalizedPos === 6) return { x: 40, y: 23.8 };
    if (normalizedPos === 7) return { x: 39, y: 29 };
    if (normalizedPos === 8) return { x: 37, y: 33 };
    if (normalizedPos === 9) return { x: 33.8, y: 36.8 };
    if (normalizedPos === 10) return { x: 29, y: 39 };
    if (normalizedPos === 11) return { x: 23.7, y: 40 };
    if (normalizedPos === 12) return { x: 19.3, y: 40 };
    if (normalizedPos === 13) return { x: 15, y: 40 };
    if (normalizedPos === 14) return { x: 11, y: 40 };
    if (normalizedPos === 15) return { x: 7, y: 40 };
    if (normalizedPos === 16) return { x: 3, y: 40 };
    // Fallback
    return { x: 50, y: 50 };
  };

  // Calcular coordenadas para fichas en casa (4 posiciones por jugador)
  const getHomePositionCoords = (color: string, pieceIndex: number): { x: number; y: number } => {
    const homePositions: Record<string, { x: number; y: number }[]> = {
      RED: [
        { x: 21, y: 21 },   // Top-left corner
        { x: 8, y: 21 },
        { x: 8, y: 8 },
        { x: 21, y: 8 },
      ],
      GREEN: [
        { x: 79, y: 7 },  // top-right corner
        { x: 79, y: 20 },
        { x: 93, y: 20 },
        { x: 93, y: 7 },
        
      ],
      YELLOW: [
        { x: 20, y: 79 },  // Bottom-left corner
        { x: 20, y: 92 },
        { x: 7, y: 92 },
        { x: 7, y: 79 },
      ],
      BLUE: [
        { x: 80, y: 80 },  // Bottom-right corner
        { x: 80, y: 93 },
        { x: 93, y: 93 },
        { x: 93, y: 80 },
        
      ],
    };

    const positions = homePositions[color.toUpperCase()] || homePositions.RED;
    return positions[pieceIndex % 4];
  };

  // Meta simplificada: usar posición 71 en tablero (no se calcula camino de meta)

  // Obtener todas las fichas con sus coordenadas y contar fichas por posición
  const getAllPiecesWithCoords = () => {
    const pieces: Array<{ piece: Piece; player: Player; x: number; y: number; positionKey: string }> = [];
    const positionCounts: Record<string, number> = {};

    gameState.players.forEach((player) => {
      player.pieces.forEach((piece, index) => {
        let coords: { x: number; y: number };
        let positionKey = '';

        // Solo dos estados: home o board. La meta es posición 71 en el tablero.
        if (piece.status === 'home') {
          coords = getHomePositionCoords(player.color, index);
          positionKey = `home-${player.color}-${index}`;
        } else {
          // Cualquier otro estado se considera tablero; meta es la 71
          const pos = piece.position === 71 ? 71 : piece.position;
          coords = getBoardPositionCoords(pos);
          positionKey = `board-${pos}`;
        }

        positionCounts[positionKey] = (positionCounts[positionKey] || 0) + 1;
        pieces.push({ piece, player, ...coords, positionKey });
      });
    });

    return { pieces, positionCounts };
  };

  // Función para loguear información relevante para mover fichas
  const movement = async (playerColor: string, selectedPieceId: string) => {
    const targetColor = playerColor.toUpperCase();
    const player = gameState.players.find(p => p.color.toUpperCase() === targetColor);
    if (!player) {
      console.log('No se encontró jugador con color:', playerColor);
      return;
    }
    // Información del usuario de la sesión actual
    if (user) {
      console.log('Jugador de la sesión actual:', user.username);
    } else {
      console.log('Jugador de la sesión actual: desconocido');
    }
    console.log('Color del jugador:', player.color);
    // Solo mostrar la ficha seleccionada
    const selectedPiece = player.pieces.find(p => p.id === selectedPieceId);
    if (selectedPiece) {
      const posLabel = selectedPiece.status === 'home' ? 'home' : String(selectedPiece.position);
      console.log(`Ficha ID: ${selectedPiece.id}`);
      console.log('Posición actual en tablero:', posLabel);
    }
    console.log('Valores actuales del dado:', diceValues);
    const currentDiceValue = diceValues[0];
    try {
      const validMovesResp = await gameService.getValidMoves(gameState.id, currentDiceValue);
      const moves = Array.isArray(validMovesResp?.moves) ? validMovesResp.moves : validMovesResp;
      const moveForPiece = moves.find((m: any) => m.piece_id === selectedPieceId);
      if (moveForPiece) {
        console.log('Movimiento válido para ficha', selectedPieceId, '- to_position:', moveForPiece.to_position);
      } else {
        console.log('No hay movimientos válidos para la ficha seleccionada.');
      }
      // Además, listar to_position de todos los movimientos devueltos
      moves.forEach((m: any) => {
        if (m && m.piece_id == selectedPieceId && m.move_type)
        {console.log('piece_id:', m.piece_id, '| to_position:', m.to_position, '| move_type:', m.move_type);}
      });
    } catch (err) {
      console.error('Error al obtener movimientos válidos:', err);
    }

  };

  // Renderizar una ficha
  const renderPiece = (piece: Piece, player: Player, x: number, y: number, count: number) => {
    const color = COLOR_THEME[player.color.toUpperCase()] || COLOR_THEME.RED;
    const isSelected = selectedPieceId === piece.id;
    const anotherSelected = selectedPieceId !== null && selectedPieceId !== piece.id;
    // Verificar si el jugador actual es dueño de la ficha
    const isNotOwner = myPlayerName ? player.name !== myPlayerName : true;
    const isDisabled = anotherSelected || isNotOwner;

    // Si no hay dimensiones calculadas aún, no renderizar
    if (!boardDimensions.imageWidth || !boardDimensions.imageHeight) return null;

    // Convertir coords porcentuales (0-100) a píxeles sobre el área de imagen ('contain')
    const absoluteX = boardDimensions.imageX + (x / 100) * boardDimensions.imageWidth;
    const absoluteY = boardDimensions.imageY + (y / 100) * boardDimensions.imageHeight;

    // Tamaño de ficha proporcional al tamaño de la imagen
    const baseSide = Math.min(boardDimensions.imageWidth, boardDimensions.imageHeight);
    const TOKEN_SIZE_PERCENT = 3.2; // porcentaje del lado menor de la imagen
    const tokenSize = Math.max(12, Math.round((baseSide * TOKEN_SIZE_PERCENT) / 100));
    const borderPx = Math.max(1, Math.round(tokenSize * 0.12));
    const fontPx = Math.max(8, Math.round(tokenSize * 0.42));

    const handleClick = (e: React.MouseEvent) => {
      if (isDisabled) return; // Ignorar clicks cuando otra ficha está seleccionada
      e.stopPropagation();
      movement(player.color, piece.id);
      onPieceClick(piece.id);
    };

    return (
      <div
        key={piece.id}
        className={`${styles.token} ${isSelected ? styles.selected : ''}`}
        style={{ left: `${absoluteX}px`, top: `${absoluteY}px` }}
        title={`${player.name} - Pos: ${piece.position}`}
        onClick={handleClick}
      >
        <div
          className={styles['token-inner']}
          style={{
            backgroundColor: color.bg,
            borderColor: color.border,
            color: color.text,
            width: `${tokenSize}px`,
            height: `${tokenSize}px`,
            borderWidth: `${borderPx}px`,
            fontSize: `${fontPx}px`,
            opacity: isDisabled ? 0.5 : 1,
            cursor: isDisabled ? 'not-allowed' : 'pointer',
          }}
        >
          {count > 1 ? count : ''}
        </div>
      </div>
    );
  };

  const { pieces: piecesWithCoords, positionCounts } = getAllPiecesWithCoords();

  // Renderizar posiciones del tablero (0-67)
  const renderBoardPositions = () => {
    if (!selectedPieceId) return null;
    if (!boardDimensions.imageWidth || !boardDimensions.imageHeight) return null;
    // Solo mostrar si es mi turno
    if (!myPlayerName) return null;
    const currentDiceValue = diceValues[0];
    if (!currentDiceValue || currentDiceValue < 1 || currentDiceValue > 6) return null;

    const positions = [];
    const baseSide = Math.min(boardDimensions.imageWidth, boardDimensions.imageHeight);
    const positionSize = Math.max(16, Math.round((baseSide * 4) / 100));

    // Determinar el color del jugador de la ficha seleccionada para rotar numeración
    let selectedColorEntry = 0;
    const selectedOwner = gameState.players.find(p => p.pieces.some(pc => pc.id === selectedPieceId));
    if (!selectedOwner || selectedOwner.name !== myPlayerName) return null;
    if (selectedOwner) {
      const colorKey = selectedOwner.color.toUpperCase();
      selectedColorEntry = GOAL_ENTRY_POSITIONS[colorKey] ?? 0;
    }

    // Solo mostrar posiciones alcanzables con los dados desde la posición actual de la ficha seleccionada
    const ownerForMoves = gameState.players.find(p => p.pieces.some(pc => pc.id === selectedPieceId));
    const selectedPiece = ownerForMoves?.pieces.find(pc => pc.id === selectedPieceId);
    const currentPos = selectedPiece ? selectedPiece.position : 0;
    const candidates = new Set<number>();
    diceValues.forEach(d => {
      if (d >= 1 && d <= 6) {
        candidates.add((currentPos + d) % BOARD_SIZE);
      }
    });

    for (let i = 0; i < BOARD_SIZE; i++) {
      if (!candidates.has(i)) continue;
      const coords = getBoardPositionCoords(i);
      const absoluteX = boardDimensions.imageX + (coords.x / 100) * boardDimensions.imageWidth;
      const absoluteY = boardDimensions.imageY + (coords.y / 100) * boardDimensions.imageHeight;

      const displayNumber = (i - selectedColorEntry + BOARD_SIZE) % BOARD_SIZE;
      positions.push(
        <div
          key={`pos-${i}`}
          className={styles['board-position']}
          style={{
            left: `${absoluteX}px`,
            top: `${absoluteY}px`,
            width: `${positionSize}px`,
            height: `${positionSize}px`,
          }}
          onClick={async (e) => {
            e.stopPropagation();
            const gameId = gameState.id;
            if (!gameId) {
              console.log('No gameId provided');
              return;
            }
            try {
              const validMovesResp = await gameService.getValidMoves(gameId, currentDiceValue);
              const moves = Array.isArray(validMovesResp?.moves) ? validMovesResp.moves : validMovesResp;
              const moveForPiece = moves.find((m: any) => m.piece_id === selectedPieceId);
              if (!moveForPiece) {
                console.log('No hay movimiento válido para la ficha seleccionada.');
                return;
              }
              const targetPos = moveForPiece.to_position;
              onPositionClick(targetPos);
              await gameService.makeMove(gameId, {
                piece_id: selectedPieceId!,
                to_position: targetPos,
                dice_value: currentDiceValue,
              });
            } catch (err) {
              console.error('Error al realizar movimiento:', err);
            }
          }}
          title={`Posición ${displayNumber}`}
        >
          <span className={styles['position-number']}>{displayNumber}</span>
        </div>
      );
    }

    return positions;
  };

  // Renderizar botón en la posición donde caería la ficha según el dado
  return (
    <div className={styles['tokens-overlay']}>
      {renderBoardPositions()}
      {/* Botón de dado eliminado - ahora se usa el menú central */}
      {piecesWithCoords.map(({ piece, player, x, y, positionKey }) =>
        renderPiece(piece, player, x, y, positionCounts[positionKey] || 1)
      )}
    </div>
  );
};

export default GameTokens;





