import React, { useState } from 'react';
import { Gamepad2, Sparkles } from 'lucide-react';
import { LoginForm } from './LoginForm';
import { RegisterForm } from './RegisterForm';

type AuthMode = 'login' | 'register';

export const AuthPage: React.FC = () => {
  const [mode, setMode] = useState<AuthMode>('login');

  return (
    <div className="min-h-screen flex">
      {/* Panel izquierdo - Información del juego */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-parques-blue via-info to-parques-green relative overflow-hidden">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="relative z-10 flex flex-col justify-center items-center p-12 text-white">
          <div className="text-center max-w-md">
            <div className="w-24 h-24 mx-auto mb-8 bg-white/10 backdrop-blur-sm rounded-full flex items-center justify-center">
              <Gamepad2 className="w-12 h-12" />
            </div>
            
            <h1 className="text-4xl font-bold mb-4">
              Parqués Distribuido IA
            </h1>
            
            <p className="text-xl mb-8 text-white/90">
              El juego tradicional colombiano con inteligencia artificial avanzada
            </p>
            
            <div className="space-y-4 text-left">
              <div className="flex items-center space-x-3">
                <Sparkles className="w-5 h-5 text-accent-gold" />
                <span>Juega contra IA con diferentes niveles</span>
              </div>
              <div className="flex items-center space-x-3">
                <Sparkles className="w-5 h-5 text-accent-gold" />
                <span>Multijugador en tiempo real</span>
              </div>
              <div className="flex items-center space-x-3">
                <Sparkles className="w-5 h-5 text-accent-gold" />
                <span>Sistema de recomendaciones inteligente</span>
              </div>
              <div className="flex items-center space-x-3">
                <Sparkles className="w-5 h-5 text-accent-gold" />
                <span>Sincronización distribuida</span>
              </div>
            </div>
          </div>
        </div>
        
        {/* Elementos decorativos */}
        <div className="absolute top-10 left-10 w-20 h-20 bg-parques-yellow/20 rounded-full blur-xl"></div>
        <div className="absolute bottom-20 right-20 w-32 h-32 bg-parques-red/20 rounded-full blur-xl"></div>
        <div className="absolute top-1/2 right-10 w-16 h-16 bg-parques-green/20 rounded-full blur-xl"></div>
      </div>

      {/* Panel derecho - Formularios */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-bg-primary">
        <div className="w-full max-w-md">
          {/* Logo móvil */}
          <div className="lg:hidden text-center mb-8">
            <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-parques-blue to-info rounded-full flex items-center justify-center">
              <Gamepad2 className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-text-primary">Parqués Distribuido IA</h1>
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