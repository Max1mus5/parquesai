import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './hooks/useAuth';
import { AuthPage } from './components/auth/AuthPage';
import { Dashboard } from './components/common/Dashboard';
import { GameList } from './components/game/GameList';
import { CreateGame } from './components/game/CreateGame';
import { GameBoard } from './components/game/GameBoard';
import { Loading } from './components/common/Loading';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <Loading />;
  }

  return user ? <>{children}</> : <Navigate to="/" replace />;
};

const AppContent: React.FC = () => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <Loading />;
  }

  return (
    <BrowserRouter>
      <Routes>
        {/* Rutas Públicas */}
        <Route 
          path="/" 
          element={user ? <Navigate to="/dashboard" replace /> : <AuthPage />} 
        />

        {/* Rutas Protegidas */}
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } 
        />

        <Route 
          path="/games" 
          element={
            <ProtectedRoute>
              <GameList />
            </ProtectedRoute>
          } 
        />

        <Route 
          path="/create-game" 
          element={
            <ProtectedRoute>
              <CreateGame />
            </ProtectedRoute>
          } 
        />

        <Route
          path="/game/:gameId"
          element={
            <ProtectedRoute>
              <GameBoard />
            </ProtectedRoute>
          }
        />

        {/* Redirección por defecto */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
