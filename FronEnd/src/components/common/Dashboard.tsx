import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut, User, Gamepad2, Trophy, Settings } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { SettingsModal } from './SettingsModal';
import styles from './Dashboard.module.css';
export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [currentUser, setCurrentUser] = useState(user);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handlePlayNow = () => {
    navigate('/games');
  };

  const handleProfileUpdated = (updatedUser: any) => {
    setCurrentUser(updatedUser);
  };

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.headerInner}>
          <div className={styles.brandRow}>
            <div className={styles.brandIcon}>
              <Gamepad2 className={styles.brandIconSvg} />
            </div>
            <h1 className={styles.title}>Parqués Distribuido IA</h1>
          </div>

          <div className={styles.userRow}>
            <div className={styles.userInfo}>
              <User className={styles.userIcon} />
              <span>Hola, {user?.username}</span>
            </div>
            <button onClick={handleLogout} className={styles.logoutBtn}>
              <LogOut className={styles.logoutIcon} />
              <span>Cerrar Sesión</span>
            </button>
          </div>
        </div>
      </header>

      <main className={styles.main}>
        <div className={styles.welcomeBlock}>
          <h2 className={styles.sectionTitle}>¡Bienvenido de vuelta, {user?.username}!</h2>
          <p className={styles.sectionSubtitle}>Listo para jugar una partida de Parqués?</p>
        </div>

        <div className={styles.cardGrid}>
          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <div className={`${styles.cardIcon} ${styles.cardIconGreen}`}>
                <Gamepad2 className={styles.cardIconSvg} />
              </div>
              <div>
                <h3 className={styles.cardTitle}>Nueva Partida</h3>
                <p className={styles.cardSubtitle}>Crear o unirse a una partida</p>
              </div>
            </div>
            <button onClick={handlePlayNow} className={styles.playButton}>Jugar Ahora</button>
          </div>

          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <div className={`${styles.cardIcon} ${styles.cardIconYellow}`}>
                <Trophy className={styles.cardIconSvgAlt} />
              </div>
              <div>
                <h3 className={styles.cardTitle}>Estadísticas</h3>
                <p className={styles.cardSubtitle}>Ver tu progreso y logros</p>
              </div>
            </div>
            <div className={styles.statsBlock}>
              <div className={styles.statsRow}>
                <span className={styles.statsLabel}>Partidas jugadas:</span>
                <span className={styles.statsValue}>0</span>
              </div>
              <div className={styles.statsRow}>
                <span className={styles.statsLabel}>Victorias:</span>
                <span className={styles.statsValueSuccess}>0</span>
              </div>
              <div className={styles.statsRow}>
                <span className={styles.statsLabel}>Nivel:</span>
                <span className={styles.statsValueAccent}>Principiante</span>
              </div>
            </div>
          </div>

          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <div className={`${styles.cardIcon} ${styles.cardIconRed}`}>
                <Settings className={styles.cardIconSvg} />
              </div>
              <div>
                <h3 className={styles.cardTitle}>Configuración</h3>
                <p className={styles.cardSubtitle}>Personalizar tu experiencia</p>
              </div>
            </div>
            <button onClick={() => setShowSettingsModal(true)} className={styles.settingsButton}>Configurar</button>
          </div>
        </div>

        <div className={styles.accountCard}>
          <h3 className={styles.accountTitle}>Información de la Cuenta</h3>
          <div className={styles.accountGrid}>
            <div>
              <label className={styles.label}>Nombre de Usuario</label>
              <p className={styles.value}>{user?.username}</p>
            </div>
            <div>
              <label className={styles.label}>Correo Electrónico</label>
              <p className={styles.value}>{user?.email}</p>
            </div>
            <div>
              <label className={styles.label}>Fecha de Registro</label>
              <p className={styles.value}>{user?.created_at ? new Date(user.created_at).toLocaleDateString('es-ES') : 'N/A'}</p>
            </div>
            <div>
              <label className={styles.label}>Estado</label>
              <span className={user?.is_active ? styles.badgeActive : styles.badgeInactive}>
                {user?.is_active ? 'Activo' : 'Inactivo'}
              </span>
            </div>
          </div>
        </div>
      </main>

      <SettingsModal
        isOpen={showSettingsModal}
        onClose={() => setShowSettingsModal(false)}
        user={currentUser}
        onProfileUpdated={handleProfileUpdated}
      />
    </div>
  );
};
