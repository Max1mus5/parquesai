import React from 'react';
import { Gamepad2 } from 'lucide-react';

export const Loading: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-bg-primary">
      <div className="text-center">
        <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-parques-blue to-info rounded-full flex items-center justify-center animate-pulse">
          <Gamepad2 className="w-8 h-8 text-white" />
        </div>
        <div className="flex items-center justify-center space-x-2">
          <div className="w-2 h-2 bg-parques-blue rounded-full animate-bounce"></div>
          <div className="w-2 h-2 bg-parques-green rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
          <div className="w-2 h-2 bg-parques-yellow rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
          <div className="w-2 h-2 bg-parques-red rounded-full animate-bounce" style={{ animationDelay: '0.3s' }}></div>
        </div>
        <p className="text-text-secondary mt-4">Cargando Parqués...</p>
      </div>
    </div>
  );
};