import { GameState } from '../types/game.types';
import { STORY_NODES } from './story-nodes';

// Default initial game state (no character created yet)
export const INITIAL_GAME_STATE: GameState = {
  character: null,
  currentNode: STORY_NODES['character-creation'],
  previousTexts: [],
  combat: null,
  gameFlags: {
    tutorialComplete: false,
    firstCombatComplete: false,
    firstShopVisit: false,
    firstDungeonComplete: false
  },
  stepCount: 0,
  playTime: 0
};

// Create initial game state with character
export const createInitialGameState = (): GameState => ({
  ...INITIAL_GAME_STATE
});