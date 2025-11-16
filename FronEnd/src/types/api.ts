export interface ApiResponse<T> {
  data?: T;
  message?: string;
  error?: string;
  status: number;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';