import React from 'react'
import { useGame } from '@game/context/GameContext'
import { useUI } from '@game/context/UIContext'
import { CharacterCreation } from '@components/character/CharacterCreation'
import { MainGameView } from './MainGameView'
import { LoadingScreen } from '@components/ui/LoadingScreen'

export const GameContainer: React.FC = () => {
  const { state } = useGame()
  const { state: uiState } = useUI()

  if (state.isLoading) {
    return <LoadingScreen />
  }

  if (!state.character) {
    return <CharacterCreation />
  }

  return (
    <div className={`game-container ${uiState.theme}`}>
      <MainGameView />
    </div>
  )
}