import React, { createContext, useReducer, ReactNode } from 'react';
import { GameState, GameAction } from '../types/game.types';
import { gameReducer } from '../game/reducers/gameReducer';
import { INITIAL_GAME_STATE } from '../data/initial-state';

interface GameContextType {
  state: GameState;
  dispatch: React.Dispatch<GameAction>;
}

export const GameContext = createContext<GameContextType>({} as GameContextType);

interface GameProviderProps {
  children: ReactNode;
}

export const GameProvider: React.FC<GameProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(gameReducer, INITIAL_GAME_STATE);

  return (
    <GameContext.Provider value={{ state, dispatch }}>
      {children}
    </GameContext.Provider>
  );
};