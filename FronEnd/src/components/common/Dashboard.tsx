import React from 'react';
import { LogOut, User, Gamepad2, Trophy, Settings } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';

export const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="min-h-screen bg-bg-primary">
      {/* Header */}
      <header className="bg-bg-secondary border-b border-surface">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-parques-blue to-info rounded-lg flex items-center justify-center">
                <Gamepad2 className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-xl font-bold text-text-primary">Parqués Distribuido IA</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-text-secondary">
                <User className="w-5 h-5" />
                <span>Hola, {user?.username}</span>
              </div>
              <button
                onClick={handleLogout}
                className="btn-secondary flex items-center space-x-2 px-4 py-2"
              >
                <LogOut className="w-4 h-4" />
                <span>Cerrar Sesión</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-text-primary mb-2">
            ¡Bienvenido de vuelta, {user?.username}!
          </h2>
          <p className="text-text-secondary">
            Listo para jugar una partida de Parqués?
          </p>
        </div>

        {/* Cards de opciones */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Nueva Partida */}
          <div className="card hover:shadow-lg transition-shadow cursor-pointer">
            <div className="flex items-center space-x-4 mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-parques-green to-success rounded-lg flex items-center justify-center">
                <Gamepad2 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-text-primary">Nueva Partida</h3>
                <p className="text-text-muted text-sm">Crear o unirse a una partida</p>
              </div>
            </div>
            <button className="btn-success w-full">
              Jugar Ahora
            </button>
          </div>

          {/* Estadísticas */}
          <div className="card hover:shadow-lg transition-shadow cursor-pointer">
            <div className="flex items-center space-x-4 mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-parques-yellow to-warning rounded-lg flex items-center justify-center">
                <Trophy className="w-6 h-6 text-bg-primary" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-text-primary">Estadísticas</h3>
                <p className="text-text-muted text-sm">Ver tu progreso y logros</p>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-text-secondary">Partidas jugadas:</span>
                <span className="text-text-primary font-medium">0</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-text-secondary">Victorias:</span>
                <span className="text-success font-medium">0</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-text-secondary">Nivel:</span>
                <span className="text-accent-gold font-medium">Principiante</span>
              </div>
            </div>
          </div>

          {/* Configuración */}
          <div className="card hover:shadow-lg transition-shadow cursor-pointer">
            <div className="flex items-center space-x-4 mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-parques-red to-error rounded-lg flex items-center justify-center">
                <Settings className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-text-primary">Configuración</h3>
                <p className="text-text-muted text-sm">Personalizar tu experiencia</p>
              </div>
            </div>
            <button className="btn-secondary w-full">
              Configurar
            </button>
          </div>
        </div>

        {/* Información del usuario */}
        <div className="mt-8 card">
          <h3 className="text-xl font-semibold text-text-primary mb-4">Información de la Cuenta</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Nombre de Usuario
              </label>
              <p className="text-text-primary">{user?.username}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Correo Electrónico
              </label>
              <p className="text-text-primary">{user?.email}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Fecha de Registro
              </label>
              <p className="text-text-primary">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString('es-ES') : 'N/A'}
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1">
                Estado
              </label>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                user?.is_active 
                  ? 'bg-success/10 text-success' 
                  : 'bg-error/10 text-error'
              }`}>
                {user?.is_active ? 'Activo' : 'Inactivo'}
              </span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};