import { API_BASE_URL } from '../types/api';
import { authService } from './authService';

class IAService {
  private baseUrl = `${API_BASE_URL}/api/v1/ai`;

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

  async getDifficultyLevels(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/difficulties`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        throw new Error('Error al obtener niveles de dificultad');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching difficulty levels:', error);
      throw error;
    }
  }

  async addBot(gameId: string, difficulty: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/bot/add`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({ game_id: gameId, difficulty }),
      });

      if (!response.ok) {
        let errorMessage = 'Error al agregar bot';
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
      console.error('Error adding bot:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Error desconocido al agregar bot');
    }
  }

  async getBotInfo(gameId: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/bot/${gameId}/info`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        let errorMessage = 'Error al obtener información del bot';
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
      console.error('Error fetching bot info:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Error desconocido al obtener información del bot');
    }
  }

  async getBotMove(gameId: string, diceValue: number): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/bot/move`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({ game_id: gameId, dice_value: diceValue }),
      });

      if (!response.ok) {
        let errorMessage = 'Error al obtener movimiento del bot';
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
      console.error('Error fetching bot move:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Error desconocido al obtener movimiento del bot');
    }
  }

  async executeBotTurn(gameId: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/bot/${gameId}/execute-turn`, {
        method: 'POST',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        let errorMessage = 'Error al ejecutar turno del bot';
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
      console.error('Error executing bot turn:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Error desconocido al ejecutar turno del bot');
    }
  }

  async removeBotFromGame(gameId: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/bot/${gameId}`, {
        method: 'DELETE',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        let errorMessage = 'Error al remover bot del juego';
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
      console.error('Error removing bot from game:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Error desconocido al remover bot del juego');
    }
  }

  async isBotTurn(gameId: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/bot/${gameId}/is-turn`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        throw new Error('Error al verificar turno del bot');
      }

      const data = await response.json();
      return data.is_bot_turn;
    } catch (error) {
      console.error('Error checking bot turn:', error);
      return false;
    }
  }

  async getAIStats(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/stats`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        throw new Error('Error al obtener estadísticas de IA');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching AI stats:', error);
      throw error;
    }
  }
}

export const iaService = new IAService();
