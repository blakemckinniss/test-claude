import React from 'react'

export const LoadingScreen: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-game-dark">
      <div className="text-center">
        <div className="mb-8">
          <div className="w-16 h-16 border-4 border-game-primary border-t-transparent rounded-full animate-spin mx-auto"></div>
        </div>
        <h2 className="text-2xl font-bold text-game-primary mb-2">Loading Adventure...</h2>
        <p className="text-gray-400">Preparing your journey</p>
      </div>
    </div>
  )
}