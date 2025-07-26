import { GameState } from '../context/GameContext'

export const createInitialGameState = (): GameState => {
  return {
    character: null,
    currentLocation: null,
    combat: null,
    activeQuests: [],
    completedQuests: [],
    isLoading: false,
    error: null
  }
}