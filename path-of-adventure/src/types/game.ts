// Core game type definitions for Path of Adventure

export interface Character {
  id: string;
  name: string;
  health: number;
  maxHealth: number;
  attack: number;
  defense: number;
  speed: number;
  level: number;
  experience: number;
  experienceToNext: number;
  gold: number;
  inventory: Inventory;
  statusEffects: StatusEffect[];
  position: Position;
}

export interface Position {
  x: number;
  y: number;
}

export interface Inventory {
  items: (Item | null)[];
  maxSlots: number;
}

export interface Item {
  id: string;
  name: string;
  type: ItemType;
  rarity: ItemRarity;
  stats?: ItemStats;
  durability?: number;
  maxDurability?: number;
  value: number;
  description: string;
}

export interface ItemStats {
  attack?: number;
  defense?: number;
  speed?: number;
  health?: number;
}

export enum ItemType {
  WEAPON = 'WEAPON',
  ARMOR = 'ARMOR',
  CONSUMABLE = 'CONSUMABLE',
  TREASURE = 'TREASURE',
  QUEST = 'QUEST'
}

export enum ItemRarity {
  COMMON = 'COMMON',
  UNCOMMON = 'UNCOMMON',
  RARE = 'RARE',
  EPIC = 'EPIC',
  LEGENDARY = 'LEGENDARY'
}

export interface StatusEffect {
  id: string;
  name: string;
  type: StatusEffectType;
  duration: number;
  power: number;
  description: string;
}

export enum StatusEffectType {
  POISON = 'POISON',
  GROWTH = 'GROWTH',
  ENCHANT_ATTACK = 'ENCHANT_ATTACK',
  ENCHANT_DEFENSE = 'ENCHANT_DEFENSE',
  ENCHANT_SPEED = 'ENCHANT_SPEED',
  STUN = 'STUN',
  REGENERATION = 'REGENERATION'
}

export interface CombatState {
  player: Character;
  enemy: Character;
  turn: 'PLAYER' | 'ENEMY';
  phase: CombatPhase;
  turnCount: number;
  combatLog: CombatLogEntry[];
  isActive: boolean;
}

export enum CombatPhase {
  ATTACK = 'ATTACK',
  DEFEND = 'DEFEND',
  EFFECT = 'EFFECT',
  REWARD = 'REWARD',
  ENDED = 'ENDED'
}

export interface CombatLogEntry {
  message: string;
  type: 'damage' | 'heal' | 'effect' | 'info';
  timestamp: number;
}

export interface CombatAction {
  type: 'attack' | 'defend' | 'item' | 'flee';
  target?: 'self' | 'enemy';
  itemId?: string;
}

export interface DamageResult {
  damage: number;
  isCritical: boolean;
  dodged: boolean;
  blocked: boolean;
}

export interface LevelUpResult {
  newLevel: number;
  statsGained: {
    health: number;
    attack: number;
    defense: number;
    speed: number;
  };
}

export interface TreasureChest {
  id: string;
  position: Position;
  items: Item[];
  gold: number;
  opened: boolean;
}

export interface GameState {
  player: Character;
  currentCombat: CombatState | null;
  treasureChests: TreasureChest[];
  gameTime: number;
  difficulty: 'EASY' | 'NORMAL' | 'HARD';
}