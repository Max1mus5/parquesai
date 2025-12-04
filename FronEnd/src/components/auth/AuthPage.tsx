import React, { useState } from 'react';
import { Gamepad2, Sparkles } from 'lucide-react';
import { LoginForm } from './LoginForm';
import { RegisterForm } from './RegisterForm';
import styles from './AuthPage.module.css';

type AuthMode = 'login' | 'register';

export const AuthPage: React.FC = () => {
  const [mode, setMode] = useState<AuthMode>('login');

  return (
    <div className={styles.container}>
      {/* Panel izquierdo - Información del juego */}
      <div className={styles.leftPanel}>
        <div className={styles.leftOverlay} />
        <div className={styles.leftContent}>
          <div className={styles.leftInner}>
            <div className={styles.leftIconWrap}>
              <Gamepad2 className={styles.leftIcon} />
            </div>
            <h1 className={styles.leftTitle}>Parqués Distribuido IA</h1>
            <p className={styles.leftSubtitle}>El juego tradicional colombiano con inteligencia artificial avanzada</p>
            <div className={styles.featuresList}>
              <div className={styles.featureItem}>
                <Sparkles className={styles.featureIcon} />
                <span>Juega contra IA con diferentes niveles</span>
              </div>
              <div className={styles.featureItem}>
                <Sparkles className={styles.featureIcon} />
                <span>Multijugador en tiempo real</span>
              </div>
              <div className={styles.featureItem}>
                <Sparkles className={styles.featureIcon} />
                <span>Sistema de recomendaciones inteligente</span>
              </div>
              <div className={styles.featureItem}>
                <Sparkles className={styles.featureIcon} />
                <span>Sincronización distribuida</span>
              </div>
            </div>
          </div>
        </div>

        {/* Elementos decorativos */}
        <div className={styles.blobYellow}></div>
        <div className={styles.blobRed}></div>
        <div className={styles.blobGreen}></div>
      </div>

      {/* Panel derecho - Formularios */}
      <div className={styles.rightPanel}>
        <div className={styles.rightInner}>
          {/* Logo móvil */}
          <div className={styles.mobileLogo}>
            <div className={styles.mobileIconWrap}>
              <Gamepad2 className={styles.mobileIcon} />
            </div>
            <h1 className={styles.mobileTitle}>Parqués Distribuido IA</h1>
          </div>

          {/* Formularios */}
          {mode === 'login' ? (
            <LoginForm onSwitchToRegister={() => setMode('register')} />
          ) : (
            <RegisterForm onSwitchToLogin={() => setMode('login')} />
          )}
        </div>
      </div>
    </div>
  );
};