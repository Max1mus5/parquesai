import React, { useState } from 'react';
import { UserPlus, Eye, EyeOff, User, Mail, Lock } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import type { RegisterRequest } from '../../types/auth';
import styles from './RegisterForm.module.css';

interface RegisterFormProps {
  onSwitchToLogin: () => void;
}

export const RegisterForm: React.FC<RegisterFormProps> = ({ onSwitchToLogin }) => {
  const { register, isLoading, error } = useAuth();
  const [formData, setFormData] = useState<RegisterRequest>({
    username: '',
    email: '',
    password: '',
  });
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    if (name === 'confirmPassword') {
      setConfirmPassword(value);
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value,
      }));
    }
    // Limpiar errores cuando el usuario empiece a escribir
    if (localError) setLocalError(null);
  };

  const validateForm = (): boolean => {
    if (!formData.username.trim()) {
      setLocalError('El nombre de usuario es requerido');
      return false;
    }
    if (formData.username.length < 3) {
      setLocalError('El nombre de usuario debe tener al menos 3 caracteres');
      return false;
    }
    if (!formData.email.trim()) {
      setLocalError('El email es requerido');
      return false;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      setLocalError('El email no tiene un formato válido');
      return false;
    }
    if (!formData.password) {
      setLocalError('La contraseña es requerida');
      return false;
    }
    if (formData.password.length < 6) {
      setLocalError('La contraseña debe tener al menos 6 caracteres');
      return false;
    }
    if (formData.password !== confirmPassword) {
      setLocalError('Las contraseñas no coinciden');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    if (!validateForm()) {
      return;
    }

    try {
      await register(formData);
    } catch (error) {
      setLocalError(error instanceof Error ? error.message : 'Error al registrarse');
    }
  };

  const displayError = localError || error;

  return (
    <div className={styles.card}>
      <div className={styles.headerBlock}>
        <div className={styles.headerIconWrap}>
          <UserPlus className={styles.headerIcon} />
        </div>
        <h2 className={styles.headerTitle}>Crear Cuenta</h2>
        <p className={styles.headerSubtitle}>Únete a la comunidad del Parqués</p>
      </div>

      {displayError && (
        <div className={styles.errorBox}>
          <p className={styles.errorText}>{displayError}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className={styles.form}>
        <div>
          <label htmlFor="username" className={styles.label}>Nombre de Usuario</label>
          <div className={styles.inputWrap}>
            <User className={styles.inputIconLeft} />
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Elige un nombre de usuario"
              className={styles.input}
              disabled={isLoading}
            />
          </div>
        </div>

        <div>
          <label htmlFor="email" className={styles.label}>Correo Electrónico</label>
          <div className={styles.inputWrap}>
            <Mail className={styles.inputIconLeft} />
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="tu@email.com"
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
              placeholder="Crea una contraseña segura"
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

        <div>
          <label htmlFor="confirmPassword" className={styles.label}>Confirmar Contraseña</label>
          <div className={styles.inputWrap}>
            <Lock className={styles.inputIconLeft} />
            <input
              type={showConfirmPassword ? 'text' : 'password'}
              id="confirmPassword"
              name="confirmPassword"
              value={confirmPassword}
              onChange={handleChange}
              placeholder="Confirma tu contraseña"
              className={styles.inputWithToggle}
              disabled={isLoading}
            />
            <button
              type="button"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              className={styles.inputToggle}
              disabled={isLoading}
            >
              {showConfirmPassword ? <EyeOff className={styles.toggleIcon} /> : <Eye className={styles.toggleIcon} />}
            </button>
          </div>
        </div>

        <button type="submit" disabled={isLoading} className={styles.submitBtnSuccess}>
          {isLoading ? (
            <div className={styles.spinnerRow}>
              <div className={styles.spinner}></div>
              Creando cuenta...
            </div>
          ) : (
            <>
              <UserPlus className={styles.submitIcon} />
              Crear Cuenta
            </>
          )}
        </button>
      </form>

      <div className={styles.footer}>
        <p className={styles.footerText}>
          ¿Ya tienes una cuenta?{' '}
          <button onClick={onSwitchToLogin} className={styles.footerLink} disabled={isLoading}>
            Inicia sesión aquí
          </button>
        </p>
      </div>
    </div>
  );
};