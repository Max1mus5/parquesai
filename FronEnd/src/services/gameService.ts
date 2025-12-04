import { API_BASE_URL } from '../types/api';
import { authService } from './authService';
import type { Game, GameCreateRequest, GameJoinRequest, GameState, Player } from '../types/game';


class GameService {
  private baseUrl = `${API_BASE_URL}/api/v1/game`;

  private getHeaders(): HeadersInit {
    const token = authService.getToken();
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    return headers;
  }

  async getAvailableGames(): Promise<Game[]> {
    try {
      const response = await fetch(`${this.baseUrl}/available`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        throw new Error('Error al obtener juegos disponibles');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching available games:', error);
      throw error;
    }
  }

  async createGame(request: GameCreateRequest): Promise<Game> {
    try {
      const response = await fetch(`${this.baseUrl}/create`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(request),
        
      });

      if (!response.ok) {
        let errorMessage = 'Error al crear juego';
        try {
          const error = await response.json();
          errorMessage = error.detail || error.message || errorMessage;
        } catch {
          errorMessage = `Error ${response.status}: ${response.statusText}`;
        }
        throw new Error(errorMessage);
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating game:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Error desconocido al crear juego');
    }
  }

  async joinGame(gameId: string, request: GameJoinRequest): Promise<Player> {
    try {
      const response = await fetch(`${this.baseUrl}/${gameId}/join`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        let errorMessage = 'Error al unirse al juego';
        try {
          const error = await response.json();
          errorMessage = error.detail || error.message || errorMessage;
        } catch {
          errorMessage = `Error ${response.status}: ${response.statusText}`;
        }
        throw new Error(errorMessage);
      }

      return await response.json();
    } catch (error) {
      console.error('Error joining game:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Error desconocido al unirse al juego');
    }
  }

  async getGameState(gameId: string): Promise<GameState> {
    try {
      const response = await fetch(`${this.baseUrl}/${gameId}/state`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        let errorMessage = 'Error al obtener estado del juego';
        try {
          const error = await response.json();
          errorMessage = error.detail || error.message || errorMessage;
        } catch {
          errorMessage = `Error ${response.status}: ${response.statusText}`;
        }
        throw new Error(errorMessage);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching game state:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Error desconocido al obtener estado del juego');
    }
  }

  async startGame(gameId: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/${gameId}/start`, {
        method: 'POST',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        let errorMessage = 'Error al iniciar juego';
        try {
          const error = await response.json();
          errorMessage = error.detail || error.message || errorMessage;
        } catch {
          errorMessage = `Error ${response.status}: ${response.statusText}`;
        }
        throw new Error(errorMessage);
      }
    } catch (error) {
      console.error('Error starting game:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Error desconocido al iniciar juego');
    }
  }

  async leaveGame(gameId: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/${gameId}/leave`, {
        method: 'POST',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        let errorMessage = 'Error al abandonar juego';
        try {
          const error = await response.json();
          errorMessage = error.detail || error.message || errorMessage;
        } catch {
          errorMessage = `Error ${response.status}: ${response.statusText}`;
        }
        throw new Error(errorMessage);
      }
    } catch (error) {
      console.error('Error leaving game:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Error desconocido al abandonar juego');
    }
  }

  async rollDice(gameId: string): Promise<import('../types/game').DiceResult> {
    try {
      const response = await fetch(`${this.baseUrl}/${gameId}/roll-dice`, {
        method: 'POST',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        let errorMessage = 'Error al lanzar dados';
        try {
          const error = await response.json();
          errorMessage = error.detail || error.message || errorMessage;
        } catch {
          errorMessage = `Error ${response.status}: ${response.statusText}`;
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error rolling dice:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Error desconocido al lanzar dado');
    }
  }

  async getValidMoves(gameId: string, diceValue: number): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/${gameId}/valid-moves/${diceValue}`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        let errorMessage = 'Error al obtener movimientos válidos';
        try {
          const error = await response.json();
          errorMessage = error.detail || error.message || errorMessage;
        } catch {
          errorMessage = `Error ${response.status}: ${response.statusText}`;
        }
        throw new Error(errorMessage);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching valid moves:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Error desconocido al obtener movimientos válidos');
    }
  }

  async movePiece(gameId: string, pieceId: string, diceValue: number, toPosition?: number, isLastMove: boolean = false): Promise<any> {
    try {
      // Si no se proporciona toPosition, obtener movimientos válidos primero
      let targetPosition = toPosition;
      if (targetPosition === undefined) {
        const validMoves = await this.getValidMoves(gameId, diceValue);
        const moveForPiece = validMoves.moves.find((m: any) => m.piece_id === pieceId);
        if (!moveForPiece) {
          throw new Error('No hay movimientos válidos para esta ficha');
        }
        targetPosition = moveForPiece.to_position;
      }
      
      const response = await fetch(`${this.baseUrl}/${gameId}/move`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({
          piece_id: pieceId,
          to_position: targetPosition,
          dice_value: diceValue,
          is_last_move: isLastMove
        }),
      });

      if (!response.ok) {
        let errorMessage = 'Error al mover ficha';
        try {
          const error = await response.json();
          errorMessage = error.detail || error.message || errorMessage;
        } catch {
          errorMessage = `Error ${response.status}: ${response.statusText}`;
        }
        throw new Error(errorMessage);
      }

      return await response.json();
    } catch (error) {
      console.error('Error moving piece:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Error desconocido al mover ficha');
    }
  }

  async passTurn(gameId: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/${gameId}/pass-turn`, {
        method: 'POST',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        let errorMessage = 'Error al pasar turno';
        try {
          const error = await response.json();
          errorMessage = error.detail || error.message || errorMessage;
        } catch {
          errorMessage = `Error ${response.status}: ${response.statusText}`;
        }
        throw new Error(errorMessage);
      }
    } catch (error) {
      console.error('Error passing turn:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Error desconocido al pasar turno');
    }
  }

  async makeMove(gameId: string, request: { piece_id: string; to_position: number; dice_value: number }): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/${gameId}/move`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        let errorMessage = 'Error al mover ficha';
        try {
          const error = await response.json();
          errorMessage = error.detail || error.message || errorMessage;
        } catch {
          errorMessage = `Error ${response.status}: ${response.statusText}`;
        }
        throw new Error(errorMessage);
      }

      return await response.json();
    } catch (error) {
      console.error('Error making move:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Error desconocido al realizar movimiento');
    }
  }

}

export const gameService = new GameService();
