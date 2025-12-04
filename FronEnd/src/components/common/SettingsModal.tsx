import React, { useState } from 'react';
import { X, Eye, EyeOff } from 'lucide-react';
import { authService } from '../../services/authService';
import styles from './SettingsModal.module.css';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  user: any;
  onProfileUpdated: (updatedUser: any) => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  user,
  onProfileUpdated,
}) => {
  const [activeTab, setActiveTab] = useState<'profile' | 'password'>('profile');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false,
  });

  // Profile form state
  const [profileData, setProfileData] = useState({
    username: user?.username || '',
    email: user?.email || '',
  });

  // Password form state
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });

  const handleProfileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setProfileData(prev => ({ ...prev, [name]: value }));
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setPasswordData(prev => ({ ...prev, [name]: value }));
  };

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const token = authService.getToken();
      if (!token) throw new Error('No token found');

      const response = await fetch(`http://localhost:8000/api/v1/auth/me`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(profileData),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Error al actualizar perfil');
      }

      const updatedUser = await response.json();
      authService.saveUser(updatedUser);
      onProfileUpdated(updatedUser);
      setSuccess('Perfil actualizado exitosamente');
      setTimeout(() => {
        setSuccess(null);
      }, 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al actualizar perfil');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (passwordData.new_password !== passwordData.confirm_password) {
      setError('Las contraseñas no coinciden');
      return;
    }

    if (passwordData.new_password.length < 8) {
      setError('La contraseña debe tener al menos 8 caracteres');
      return;
    }

    setLoading(true);

    try {
      const token = authService.getToken();
      if (!token) throw new Error('No token found');

      const response = await fetch(`http://localhost:8000/api/v1/auth/change-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          current_password: passwordData.current_password,
          new_password: passwordData.new_password,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Error al cambiar contraseña');
      }

      setSuccess('Contraseña cambiada exitosamente');
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: '',
      });
      setTimeout(() => {
        setSuccess(null);
      }, 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cambiar contraseña');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const togglePasswordVisibility = (field: 'current' | 'new' | 'confirm') => {
    setShowPasswords(prev => ({
      ...prev,
      [field]: !prev[field],
    }));
  };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <h2 className={styles.title}>Configuración</h2>
          <button onClick={onClose} className={styles.closeButton}>
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className={styles.tabs}>
          <button
            onClick={() => setActiveTab('profile')}
            className={`${styles.tab} ${activeTab === 'profile' ? styles.tabActive : ''}`}
          >
            Perfil
          </button>
          <button
            onClick={() => setActiveTab('password')}
            className={`${styles.tab} ${activeTab === 'password' ? styles.tabActive : ''}`}
          >
            Contraseña
          </button>
        </div>

        <div className={styles.content}>
          {error && (
            <div className={styles.errorBox}>
              <p className={styles.errorText}>{error}</p>
            </div>
          )}

          {success && (
            <div className={styles.successBox}>
              <p className={styles.successText}>{success}</p>
            </div>
          )}

          {activeTab === 'profile' && (
            <form onSubmit={handleProfileSubmit} className={styles.form}>
              <div className={styles.formGroup}>
                <label className={styles.label}>Nombre de Usuario</label>
                <input
                  type="text"
                  name="username"
                  value={profileData.username}
                  onChange={handleProfileChange}
                  className={styles.input}
                  placeholder="Tu nombre de usuario"
                />
              </div>

              <div className={styles.formGroup}>
                <label className={styles.label}>Correo Electrónico</label>
                <input
                  type="email"
                  name="email"
                  value={profileData.email}
                  onChange={handleProfileChange}
                  className={styles.input}
                  placeholder="Tu correo electrónico"
                />
              </div>

              <div className={styles.formActions}>
                <button
                  type="button"
                  onClick={onClose}
                  className={styles.cancelButton}
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className={styles.submitButton}
                >
                  {loading ? 'Guardando...' : 'Guardar Cambios'}
                </button>
              </div>
            </form>
          )}

          {activeTab === 'password' && (
            <form onSubmit={handlePasswordSubmit} className={styles.form}>
              <div className={styles.formGroup}>
                <label className={styles.label}>Contraseña Actual</label>
                <div className={styles.passwordInputWrapper}>
                  <input
                    type={showPasswords.current ? 'text' : 'password'}
                    name="current_password"
                    value={passwordData.current_password}
                    onChange={handlePasswordChange}
                    className={styles.input}
                    placeholder="Tu contraseña actual"
                  />
                  <button
                    type="button"
                    onClick={() => togglePasswordVisibility('current')}
                    className={styles.togglePassword}
                  >
                    {showPasswords.current ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>

              <div className={styles.formGroup}>
                <label className={styles.label}>Nueva Contraseña</label>
                <div className={styles.passwordInputWrapper}>
                  <input
                    type={showPasswords.new ? 'text' : 'password'}
                    name="new_password"
                    value={passwordData.new_password}
                    onChange={handlePasswordChange}
                    className={styles.input}
                    placeholder="Nueva contraseña (mín. 8 caracteres)"
                  />
                  <button
                    type="button"
                    onClick={() => togglePasswordVisibility('new')}
                    className={styles.togglePassword}
                  >
                    {showPasswords.new ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>

              <div className={styles.formGroup}>
                <label className={styles.label}>Confirmar Nueva Contraseña</label>
                <div className={styles.passwordInputWrapper}>
                  <input
                    type={showPasswords.confirm ? 'text' : 'password'}
                    name="confirm_password"
                    value={passwordData.confirm_password}
                    onChange={handlePasswordChange}
                    className={styles.input}
                    placeholder="Confirma tu nueva contraseña"
                  />
                  <button
                    type="button"
                    onClick={() => togglePasswordVisibility('confirm')}
                    className={styles.togglePassword}
                  >
                    {showPasswords.confirm ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>

              <div className={styles.passwordHint}>
                <p>La contraseña debe tener al menos 8 caracteres</p>
              </div>

              <div className={styles.formActions}>
                <button
                  type="button"
                  onClick={onClose}
                  className={styles.cancelButton}
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className={styles.submitButton}
                >
                  {loading ? 'Cambiando...' : 'Cambiar Contraseña'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};
