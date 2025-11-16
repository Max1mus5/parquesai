import React from 'react';
import { AuthProvider, useAuth } from './hooks/useAuth';
import { AuthPage } from './components/auth/AuthPage';
import { Dashboard } from './components/common/Dashboard';
import { Loading } from './components/common/Loading';

const AppContent: React.FC = () => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <Loading />;
  }

  return user ? <Dashboard /> : <AuthPage />;
};

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
