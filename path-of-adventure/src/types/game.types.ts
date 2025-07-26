// Basic game types for the Path of Adventure game
export type CharacterClass = 'warrior' | 'rogue' | 'mage';

export interface Character {
  id: string;
  name: string;
  class: CharacterClass;
  level: number;
  experience: number;
  experienceToNext: number;
  health: number;
  maxHealth: number;
  attack: number;
  defense: number;
  speed: number;
  gold: number;
  inventory: (Item | null)[];
  equipped: {
    weapon: Item | null;
    armor: Item | null;
  };
  statusEffects: StatusEffect[];
}

export interface Item {
  id: string;
  name: string;
  type: 'weapon' | 'armor' | 'consumable' | 'misc';
  rarity: 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary';
  description: string;
  value?: number;
  damage?: {
    min: number;
    max: number;
  };
  defense?: number;
  speed?: number;
  durability?: {
    current: number;
    max: number;
  };
  faded?: boolean;
  effect?: {
    type: string;
    value: number;
    description: string;
  };
}

export interface Weapon extends Item {
  type: 'weapon';
  damage: {
    min: number;
    max: number;
  };
}

export interface Armor extends Item {
  type: 'armor';
  defense: number;
}

export interface Consumable extends Item {
  type: 'consumable';
  effect: {
    type: string;
    value: number;
    description: string;
  };
}

export interface StatusEffect {
  type: 'poison' | 'regeneration' | 'attack_boost' | 'defense_boost' | 'speed_boost' | 'stun';
  duration: number;
  value?: number;
  description: string;
}

export interface StoryNode {
  id: string;
  type: 'narration' | 'dialogue' | 'event';
  text: string;
  speaker?: string;
  choices: StoryChoice[];
}

export interface StoryChoice {
  text: string;
  nextNodeId: string;
  consequences?: {
    stepCount?: number;
    health?: number;
    gold?: number;
    items?: string[];
    combat?: string;
  };
  requirements?: {
    level?: number;
    stat?: {
      type: 'attack' | 'defense' | 'speed';
      value: number;
    };
    item?: string;
  };
}

export interface Enemy {
  id: string;
  name: string;
  level: number;
  health: number;
  maxHealth: number;
  attack: {
    min: number;
    max: number;
  };
  defense: number;
  speed: number;
}

export interface CombatState {
  enemy: Enemy;
  turn: number;
  phase: 'player_turn' | 'enemy_turn' | 'victory' | 'defeat';
  log: string[];
  rewards?: {
    experience: number;
    gold: number;
    items?: Item[];
  };
}

export interface GameState {
  character: Character | null;
  currentNode: StoryNode | null;
  previousTexts: Array<{
    text: string;
    type: 'narration' | 'dialogue';
  }>;
  combat: CombatState | null;
  gameFlags: {
    tutorialComplete: boolean;
    firstCombatComplete: boolean;
    firstShopVisit: boolean;
    firstDungeonComplete: boolean;
  };
  stepCount: number;
  playTime: number;
}

export type GameAction =
  | { type: 'CREATE_CHARACTER'; payload: { name: string; characterClass: string } }
  | { type: 'MAKE_CHOICE'; payload: StoryChoice }
  | { type: 'APPLY_STATUS_EFFECTS' }
  | { type: 'NEW_GAME' }
  | { type: 'COMBAT_ACTION'; payload: any }
  | { type: 'FLEE_COMBAT' }
  | { type: 'END_COMBAT' }
  | { type: 'USE_ITEM'; payload: number }
  | { type: 'DROP_ITEM'; payload: number }
  | { type: 'EQUIP_WEAPON'; payload: number }
  | { type: 'EQUIP_ARMOR'; payload: number }
  | { type: 'GAME_OVER' };

export interface TextDisplay {
  text: string;
  type: 'narration' | 'dialogue' | 'action' | 'damage' | 'heal';
  speaker?: string;
}