import { API_BASE_URL } from '../types/api';
import { authService } from './authService';

class RecommendationsService {
  private baseUrl = `${API_BASE_URL}/api/v1/recommendations`;

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

  async getUserRecommendations(forceRefresh: boolean = false): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/?force_refresh=${forceRefresh}`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        let errorMessage = 'Error al obtener recomendaciones';
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
      console.error('Error fetching recommendations:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Error desconocido al obtener recomendaciones');
    }
  }

  async getStrategyRecommendations(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/strategy`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        let errorMessage = 'Error al obtener recomendaciones de estrategia';
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
      console.error('Error fetching strategy recommendations:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Error desconocido al obtener recomendaciones de estrategia');
    }
  }

  async getOpponentRecommendations(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/opponents`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        let errorMessage = 'Error al obtener recomendaciones de oponentes';
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
      console.error('Error fetching opponent recommendations:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Error desconocido al obtener recomendaciones de oponentes');
    }
  }

  async getTrainingRecommendations(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/training`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        let errorMessage = 'Error al obtener recomendaciones de entrenamiento';
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
      console.error('Error fetching training recommendations:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Error desconocido al obtener recomendaciones de entrenamiento');
    }
  }

  async getGameAnalysis(gameId: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/game/${gameId}/analysis`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        let errorMessage = 'Error al analizar el juego';
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
      console.error('Error fetching game analysis:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Error desconocido al analizar el juego');
    }
  }

  async getImprovementSuggestions(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/improvement`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        let errorMessage = 'Error al obtener sugerencias de mejora';
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
      console.error('Error fetching improvement suggestions:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Error desconocido al obtener sugerencias de mejora');
    }
  }

  async getChallenges(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/challenges`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        let errorMessage = 'Error al obtener desafíos';
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
      console.error('Error fetching challenges:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Error desconocido al obtener desafíos');
    }
  }

  async getPlayerPattern(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/pattern`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        let errorMessage = 'Error al obtener patrón de juego';
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
      console.error('Error fetching player pattern:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Error desconocido al obtener patrón de juego');
    }
  }

  async getStats(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/stats`, {
        method: 'GET',
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        let errorMessage = 'Error al obtener estadísticas';
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
      console.error('Error fetching stats:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Error desconocido al obtener estadísticas');
    }
  }
}

export const recommendationsService = new RecommendationsService();
