import type { LoginRequest, RegisterRequest, AuthResponse, User } from '../types/auth';
import { API_BASE_URL } from '../types/api';

class AuthService {
  private baseUrl = `${API_BASE_URL}/api/v1/auth`;

  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await fetch(`${this.baseUrl}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: credentials.email,
        password: credentials.password,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error en el login');
    }

    return response.json();
  }

  async register(userData: RegisterRequest): Promise<AuthResponse> {
    const response = await fetch(`${this.baseUrl}/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error en el registro');
    }

    return response.json();
  }

  async getProfile(token: string): Promise<User> {
    const response = await fetch(`${this.baseUrl}/profile`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error al obtener el perfil');
    }

    return response.json();
  }

  // Métodos para manejar el token en localStorage
  saveToken(token: string): void {
    localStorage.setItem('auth_token', token);
  }

  getToken(): string | null {
    return localStorage.getItem('auth_token');
  }

  removeToken(): void {
    localStorage.removeItem('auth_token');
  }

  saveUser(user: User): void {
    localStorage.setItem('user_data', JSON.stringify(user));
  }

  getUser(): User | null {
    const userData = localStorage.getItem('user_data');
    return userData ? JSON.parse(userData) : null;
  }

  removeUser(): void {
    localStorage.removeItem('user_data');
  }
}

export const authService = new AuthService();