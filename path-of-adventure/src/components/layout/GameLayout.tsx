import React, { ReactNode } from 'react';
import '../../styles/parchment-theme.css';

interface GameLayoutProps {
  children: ReactNode;
}

const GameLayout: React.FC<GameLayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 opacity-30">
        <div className="torch-light" style={{ top: '10%', left: '5%' }} />
        <div className="torch-light" style={{ top: '20%', right: '10%' }} />
        <div className="torch-light" style={{ bottom: '15%', left: '8%' }} />
        <div className="torch-light" style={{ bottom: '25%', right: '5%' }} />
      </div>
      
      {/* Subtle texture overlay */}
      <div className="absolute inset-0 opacity-10" style={{
        backgroundImage: `
          repeating-linear-gradient(
            45deg,
            transparent,
            transparent 2px,
            rgba(255, 255, 255, 0.03) 2px,
            rgba(255, 255, 255, 0.03) 4px
          )
        `
      }} />
      
      {/* Main content container - unified middle column */}
      <div className="relative z-10 min-h-screen flex items-center justify-center p-4">
        <div className="w-full max-w-4xl mx-auto">
          <div className="bg-gradient-to-br from-parchment-light/95 to-parchment/90 backdrop-blur-sm rounded-2xl shadow-2xl border-4 border-parchment-shadow/50 p-8 relative overflow-hidden">
            {/* Decorative corners */}
            <div className="absolute top-4 left-4 w-8 h-8 border-l-4 border-t-4 border-gold/60 rounded-tl-lg" />
            <div className="absolute top-4 right-4 w-8 h-8 border-r-4 border-t-4 border-gold/60 rounded-tr-lg" />
            <div className="absolute bottom-4 left-4 w-8 h-8 border-l-4 border-b-4 border-gold/60 rounded-bl-lg" />
            <div className="absolute bottom-4 right-4 w-8 h-8 border-r-4 border-b-4 border-gold/60 rounded-br-lg" />
            
            {/* Content */}
            <div className="relative z-10">
              {children}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GameLayout;