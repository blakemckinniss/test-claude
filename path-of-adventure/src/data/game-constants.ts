// Game configuration constants

export const GAME_CONSTANTS = {
  // Character creation
  STARTING_STATS: {
    health: 100,
    maxHealth: 100,
    mana: 50,
    maxMana: 50,
    strength: 10,
    agility: 10,
    intelligence: 10,
    vitality: 10,
    luck: 5
  },
  
  // Character progression
  LEVEL_UP: {
    HEALTH_PER_LEVEL: 10,
    MANA_PER_LEVEL: 5,
    STAT_POINTS_PER_LEVEL: 3,
    BASE_EXP_TO_NEXT: 100,
    EXP_MULTIPLIER: 1.5 // Each level requires 50% more exp than previous
  },
  
  // Combat formulas
  COMBAT: {
    BASE_HIT_CHANCE: 80,
    CRIT_MULTIPLIER: 2.0,
    DODGE_CAP: 75, // Maximum dodge chance
    BLOCK_CAP: 50, // Maximum block chance
    BLOCK_DAMAGE_REDUCTION: 0.5, // 50% damage reduction on block
    TURN_LIMIT: 50 // Maximum turns before combat auto-ends
  },
  
  // Stat calculations
  STAT_FORMULAS: {
    // Attack = Strength + Weapon damage
    ATTACK_FROM_STRENGTH: 1.0,
    
    // Defense = Vitality * 0.5 + Armor defense
    DEFENSE_FROM_VITALITY: 0.5,
    
    // Magic Power = Intelligence * 1.5
    MAGIC_FROM_INTELLIGENCE: 1.5,
    
    // Crit Chance = Luck * 2 + Agility * 0.5
    CRIT_FROM_LUCK: 2.0,
    CRIT_FROM_AGILITY: 0.5,
    
    // Dodge Chance = Agility * 2
    DODGE_FROM_AGILITY: 2.0,
    
    // Block Chance = Strength * 0.5 + Shield bonus
    BLOCK_FROM_STRENGTH: 0.5,
    
    // Max Health = Vitality * 10 + Base health
    HEALTH_FROM_VITALITY: 10,
    
    // Max Mana = Intelligence * 5 + Base mana
    MANA_FROM_INTELLIGENCE: 5
  },
  
  // Shop pricing
  SHOP: {
    SELL_PRICE_MULTIPLIER: 0.5, // Items sell for 50% of their value
    REPUTATION_DISCOUNT_MAX: 0.2, // Max 20% discount with high reputation
    REPUTATION_THRESHOLD: 50 // Reputation needed for max discount
  },
  
  // Difficulty modifiers
  DIFFICULTY: {
    easy: {
      ENEMY_HEALTH_MULTIPLIER: 0.75,
      ENEMY_DAMAGE_MULTIPLIER: 0.75,
      PLAYER_DAMAGE_MULTIPLIER: 1.25,
      EXP_MULTIPLIER: 1.5,
      GOLD_MULTIPLIER: 1.5
    },
    normal: {
      ENEMY_HEALTH_MULTIPLIER: 1.0,
      ENEMY_DAMAGE_MULTIPLIER: 1.0,
      PLAYER_DAMAGE_MULTIPLIER: 1.0,
      EXP_MULTIPLIER: 1.0,
      GOLD_MULTIPLIER: 1.0
    },
    hard: {
      ENEMY_HEALTH_MULTIPLIER: 1.5,
      ENEMY_DAMAGE_MULTIPLIER: 1.5,
      PLAYER_DAMAGE_MULTIPLIER: 0.9,
      EXP_MULTIPLIER: 0.75,
      GOLD_MULTIPLIER: 0.75
    },
    nightmare: {
      ENEMY_HEALTH_MULTIPLIER: 2.0,
      ENEMY_DAMAGE_MULTIPLIER: 2.0,
      PLAYER_DAMAGE_MULTIPLIER: 0.75,
      EXP_MULTIPLIER: 0.5,
      GOLD_MULTIPLIER: 0.5
    }
  },
  
  // Save system
  SAVE: {
    MAX_SAVE_SLOTS: 3,
    AUTOSAVE_INTERVAL: 300000, // 5 minutes in milliseconds
    VERSION: '1.0.0'
  },
  
  // UI constants
  UI: {
    ANIMATION_DURATION: 300, // milliseconds
    TOOLTIP_DELAY: 500,
    MESSAGE_DISPLAY_TIME: 3000,
    COMBAT_LOG_MAX_ENTRIES: 50
  },
  
  // Random generation
  RANDOM: {
    CRIT_ROLL_MAX: 100,
    DODGE_ROLL_MAX: 100,
    LOOT_ROLL_MAX: 100,
    ENCOUNTER_ROLL_MAX: 100
  },
  
  // Status effect durations (in combat turns)
  STATUS_DURATIONS: {
    POISON: 5,
    BURN: 3,
    STUN: 1,
    SLOW: 3,
    STRENGTH_BUFF: 5,
    DEFENSE_BUFF: 5,
    SPEED_BUFF: 5
  },
  
  // Reputation levels
  REPUTATION: {
    HOSTILE: -50,
    UNFRIENDLY: -25,
    NEUTRAL: 0,
    FRIENDLY: 25,
    HONORED: 50,
    REVERED: 100
  }
};

// Skill check difficulty thresholds
export const SKILL_CHECK_DIFFICULTY = {
  TRIVIAL: 5,
  EASY: 10,
  MEDIUM: 15,
  HARD: 20,
  EXTREME: 25,
  LEGENDARY: 30
};

// Experience required per level (calculated dynamically)
export function getExperienceForLevel(level: number): number {
  if (level <= 1) return 0;
  const base = GAME_CONSTANTS.LEVEL_UP.BASE_EXP_TO_NEXT;
  const multiplier = GAME_CONSTANTS.LEVEL_UP.EXP_MULTIPLIER;
  let total = 0;
  
  for (let i = 1; i < level; i++) {
    total += Math.floor(base * Math.pow(multiplier, i - 1));
  }
  
  return total;
}

// Calculate derived stats from base stats
export function calculateDerivedStats(baseStats: any) {
  const formulas = GAME_CONSTANTS.STAT_FORMULAS;
  
  return {
    attack: Math.floor(baseStats.strength * formulas.ATTACK_FROM_STRENGTH),
    defense: Math.floor(baseStats.vitality * formulas.DEFENSE_FROM_VITALITY),
    magicPower: Math.floor(baseStats.intelligence * formulas.MAGIC_FROM_INTELLIGENCE),
    critChance: Math.min(
      Math.floor(baseStats.luck * formulas.CRIT_FROM_LUCK + baseStats.agility * formulas.CRIT_FROM_AGILITY),
      GAME_CONSTANTS.COMBAT.DODGE_CAP
    ),
    dodgeChance: Math.min(
      Math.floor(baseStats.agility * formulas.DODGE_FROM_AGILITY),
      GAME_CONSTANTS.COMBAT.DODGE_CAP
    ),
    blockChance: Math.min(
      Math.floor(baseStats.strength * formulas.BLOCK_FROM_STRENGTH),
      GAME_CONSTANTS.COMBAT.BLOCK_CAP
    )
  };
}

// Calculate max health and mana
export function calculateMaxHealthMana(baseStats: any) {
  const formulas = GAME_CONSTANTS.STAT_FORMULAS;
  const starting = GAME_CONSTANTS.STARTING_STATS;
  
  return {
    maxHealth: starting.maxHealth + Math.floor(baseStats.vitality * formulas.HEALTH_FROM_VITALITY),
    maxMana: starting.maxMana + Math.floor(baseStats.intelligence * formulas.MANA_FROM_INTELLIGENCE)
  };
}