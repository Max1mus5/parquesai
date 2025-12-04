import React, { useState } from 'react';
import { LogIn, Eye, EyeOff, User, Lock } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import type { LoginRequest } from '../../types/auth';
import styles from './LoginForm.module.css';

interface LoginFormProps {
  onSwitchToRegister: () => void;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onSwitchToRegister }) => {
  const { login, isLoading, error } = useAuth();
  const [formData, setFormData] = useState<LoginRequest>({
    email: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
    // Limpiar errores cuando el usuario empiece a escribir
    if (localError) setLocalError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    // Validaciones básicas
    if (!formData.email.trim()) {
      setLocalError('El correo electrónico es requerido');
      return;
    }
    if (!formData.password) {
      setLocalError('La contraseña es requerida');
      return;
    }

    try {
      await login(formData);
    } catch (error) {
      setLocalError(error instanceof Error ? error.message : 'Error al iniciar sesión');
    }
  };

  const displayError = localError || error;

  return (
    <div className={styles.card}>
      <div className={styles.headerBlock}>
        <div className={styles.headerIconWrap}>
          <LogIn className={styles.headerIcon} />
        </div>
        <h2 className={styles.headerTitle}>Iniciar Sesión</h2>
        <p className={styles.headerSubtitle}>Bienvenido de vuelta al Parqués</p>
      </div>

      {displayError && (
        <div className={styles.errorBox}>
          <p className={styles.errorText}>{displayError}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className={styles.form}>
        <div>
          <label htmlFor="username" className="block text-sm font-medium text-text-secondary mb-2">
            Nombre de Usuario
          </label>
          <div className="relative">
            <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-text-muted" />
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Ingresa tu correo electrónico"
              className={styles.input}
              disabled={isLoading}
            />
          </div>
        </div>

        <div>
          <label htmlFor="password" className={styles.label}>Contraseña</label>
          <div className={styles.inputWrap}>
            <Lock className={styles.inputIconLeft} />
            <input
              type={showPassword ? 'text' : 'password'}
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Ingresa tu contraseña"
              className={styles.inputWithToggle}
              disabled={isLoading}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className={styles.inputToggle}
              disabled={isLoading}
            >
              {showPassword ? <EyeOff className={styles.toggleIcon} /> : <Eye className={styles.toggleIcon} />}
            </button>
          </div>
        </div>

        <button type="submit" disabled={isLoading} className={styles.submitBtn}>
          {isLoading ? (
            <div className={styles.spinnerRow}>
              <div className={styles.spinner}></div>
              Iniciando sesión...
            </div>
          ) : (
            <>
              <LogIn className={styles.submitIcon} />
              Iniciar Sesión
            </>
          )}
        </button>
      </form>

      <div className={styles.footer}>
        <p className={styles.footerText}>
          ¿No tienes una cuenta?{' '}
          <button onClick={onSwitchToRegister} className={styles.footerLink} disabled={isLoading}>
            Regístrate aquí
          </button>
        </p>
      </div>
    </div>
  );
};