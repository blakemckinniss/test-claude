import { GameState, GameAction, Character, CharacterClass } from '../../types/game.types';
import { STORY_NODES } from '../../data/story-nodes';

export const gameReducer = (state: GameState, action: GameAction): GameState => {
  switch (action.type) {
    case 'CREATE_CHARACTER':
      const newCharacter: Character = {
        id: Date.now().toString(),
        name: action.payload.name,
        class: action.payload.characterClass as CharacterClass,
        level: 1,
        experience: 0,
        experienceToNext: 100,
        health: 100,
        maxHealth: 100,
        attack: 10,
        defense: 5,
        speed: 8,
        gold: 0,
        inventory: [null, null, null, null],
        equipped: {
          weapon: null,
          armor: null
        },
        statusEffects: []
      };
      
      return {
        ...state,
        character: newCharacter,
        currentNode: STORY_NODES['tutorial-start']
      };

    case 'MAKE_CHOICE':
      const choice = action.payload;
      const nextNode = STORY_NODES[choice.nextNodeId];
      
      let newState = {
        ...state,
        currentNode: nextNode,
        previousTexts: [
          ...state.previousTexts,
          {
            text: state.currentNode?.text || '',
            type: 'narration' as const
          }
        ]
      };

      // Apply consequences
      if (choice.consequences) {
        if (choice.consequences.stepCount) {
          newState.stepCount += choice.consequences.stepCount;
        }
        
        if (choice.consequences.gold && newState.character) {
          newState.character.gold += choice.consequences.gold;
        }
        
        if (choice.consequences.health && newState.character) {
          newState.character.health = Math.min(
            newState.character.maxHealth,
            newState.character.health + choice.consequences.health
          );
        }
      }

      return newState;

    case 'APPLY_STATUS_EFFECTS':
      if (!state.character) return state;
      
      let updatedCharacter = { ...state.character };
      updatedCharacter.statusEffects = updatedCharacter.statusEffects.filter(effect => {
        effect.duration -= 1;
        
        // Apply effect
        if (effect.type === 'poison') {
          updatedCharacter.health = Math.max(0, updatedCharacter.health - 1);
        } else if (effect.type === 'regeneration') {
          updatedCharacter.health = Math.min(
            updatedCharacter.maxHealth,
            updatedCharacter.health + 1
          );
        }
        
        return effect.duration > 0;
      });

      return {
        ...state,
        character: updatedCharacter
      };

    case 'NEW_GAME':
      return {
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

    default:
      return state;
  }
};