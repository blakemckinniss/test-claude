import React, { createContext, useContext, useReducer, useCallback, ReactNode } from 'react'
import { Character, Location, CombatState, Quest, SaveGame } from '@types/game.types'
import { gameReducer, GameAction } from '../reducers/gameReducer'
import { createInitialGameState } from '../utils/gameInitializer'

export interface GameState {
  character: Character | null
  currentLocation: Location | null
  combat: CombatState | null
  activeQuests: Quest[]
  completedQuests: Quest[]
  isLoading: boolean
  error: string | null
}

interface GameContextType {
  state: GameState
  dispatch: React.Dispatch<GameAction>
  
  // Character actions
  createCharacter: (name: string, characterClass: string) => void
  levelUp: () => void
  
  // Location actions
  moveToLocation: (locationId: string) => void
  
  // Combat actions
  startCombat: (enemyIds: string[]) => void
  performAction: (skillId: string, targetId?: string) => void
  endCombat: () => void
  
  // Quest actions
  acceptQuest: (questId: string) => void
  updateQuestProgress: (questId: string, objectiveId: string, progress: number) => void
  completeQuest: (questId: string) => void
  
  // Save/Load
  saveGame: () => SaveGame
  loadGame: (saveData: SaveGame) => void
}

const GameContext = createContext<GameContextType | undefined>(undefined)

export const useGame = () => {
  const context = useContext(GameContext)
  if (!context) {
    throw new Error('useGame must be used within a GameProvider')
  }
  return context
}

interface GameProviderProps {
  children: ReactNode
}

export const GameProvider: React.FC<GameProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(gameReducer, createInitialGameState())

  // Character actions
  const createCharacter = useCallback((name: string, characterClass: string) => {
    dispatch({ type: 'CREATE_CHARACTER', payload: { name, characterClass } })
  }, [])

  const levelUp = useCallback(() => {
    dispatch({ type: 'LEVEL_UP' })
  }, [])

  // Location actions
  const moveToLocation = useCallback((locationId: string) => {
    dispatch({ type: 'MOVE_TO_LOCATION', payload: locationId })
  }, [])

  // Combat actions
  const startCombat = useCallback((enemyIds: string[]) => {
    dispatch({ type: 'START_COMBAT', payload: enemyIds })
  }, [])

  const performAction = useCallback((skillId: string, targetId?: string) => {
    dispatch({ type: 'PERFORM_ACTION', payload: { skillId, targetId } })
  }, [])

  const endCombat = useCallback(() => {
    dispatch({ type: 'END_COMBAT' })
  }, [])

  // Quest actions
  const acceptQuest = useCallback((questId: string) => {
    dispatch({ type: 'ACCEPT_QUEST', payload: questId })
  }, [])

  const updateQuestProgress = useCallback(
    (questId: string, objectiveId: string, progress: number) => {
      dispatch({
        type: 'UPDATE_QUEST_PROGRESS',
        payload: { questId, objectiveId, progress }
      })
    },
    []
  )

  const completeQuest = useCallback((questId: string) => {
    dispatch({ type: 'COMPLETE_QUEST', payload: questId })
  }, [])

  // Save/Load
  const saveGame = useCallback((): SaveGame => {
    // Implementation would serialize current state
    const saveData: SaveGame = {
      id: Date.now().toString(),
      timestamp: Date.now(),
      character: state.character!,
      world: {
        currentLocation: state.currentLocation?.id || '',
        visitedLocations: [],
        completedEvents: [],
        npcStates: {},
        globalFlags: {}
      },
      playtime: 0,
      version: '1.0.0'
    }
    return saveData
  }, [state])

  const loadGame = useCallback((saveData: SaveGame) => {
    dispatch({ type: 'LOAD_GAME', payload: saveData })
  }, [])

  const value: GameContextType = {
    state,
    dispatch,
    createCharacter,
    levelUp,
    moveToLocation,
    startCombat,
    performAction,
    endCombat,
    acceptQuest,
    updateQuestProgress,
    completeQuest,
    saveGame,
    loadGame
  }

  return <GameContext.Provider value={value}>{children}</GameContext.Provider>
}