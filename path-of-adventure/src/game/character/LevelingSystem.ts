import { Character, LevelUpResult } from '../../types/game';

export class LevelingSystem {
  // Experience required for each level follows a quadratic curve
  private static readonly BASE_EXP_REQUIREMENT = 100;
  private static readonly EXP_MULTIPLIER = 1.5;
  
  // Stat gains per level
  private static readonly HEALTH_PER_LEVEL = 10;
  private static readonly ATTACK_PER_LEVEL = 2;
  private static readonly DEFENSE_PER_LEVEL = 1;
  private static readonly SPEED_PER_LEVEL = 1;
  
  /**
   * Calculate experience required for a specific level
   */
  static getExperienceRequiredForLevel(level: number): number {
    if (level <= 1) return 0;
    
    // Quadratic growth: exp = base * level^multiplier
    return Math.floor(
      this.BASE_EXP_REQUIREMENT * Math.pow(level - 1, this.EXP_MULTIPLIER)
    );
  }
  
  /**
   * Add experience to a character and handle level ups
   * Returns array of level up results (can level up multiple times)
   */
  static addExperience(character: Character, expGained: number): LevelUpResult[] {
    const levelUpResults: LevelUpResult[] = [];
    character.experience += expGained;
    
    // Check for level ups
    while (character.experience >= character.experienceToNext) {
      const result = this.levelUp(character);
      levelUpResults.push(result);
    }
    
    return levelUpResults;
  }
  
  /**
   * Level up a character
   */
  private static levelUp(character: Character): LevelUpResult {
    // Store old stats for comparison
    const oldLevel = character.level;
    const oldMaxHealth = character.maxHealth;
    const oldAttack = character.attack;
    const oldDefense = character.defense;
    const oldSpeed = character.speed;
    
    // Increase level
    character.level++;
    
    // Calculate stat gains (with some randomness)
    const healthGain = this.HEALTH_PER_LEVEL + Math.floor(Math.random() * 5);
    const attackGain = this.ATTACK_PER_LEVEL + Math.floor(Math.random() * 2);
    const defenseGain = this.DEFENSE_PER_LEVEL + Math.floor(Math.random() * 2);
    const speedGain = this.SPEED_PER_LEVEL + (Math.random() < 0.3 ? 1 : 0);
    
    // Apply stat gains
    character.maxHealth += healthGain;
    character.health += healthGain; // Also heal on level up
    character.attack += attackGain;
    character.defense += defenseGain;
    character.speed += speedGain;
    
    // Calculate remaining experience and requirement for next level
    character.experience -= character.experienceToNext;
    character.experienceToNext = this.getExperienceRequiredForLevel(character.level + 1) - 
                                this.getExperienceRequiredForLevel(character.level);
    
    return {
      newLevel: character.level,
      statsGained: {
        health: character.maxHealth - oldMaxHealth,
        attack: character.attack - oldAttack,
        defense: character.defense - oldDefense,
        speed: character.speed - oldSpeed
      }
    };
  }
  
  /**
   * Get experience progress as a percentage
   */
  static getExperienceProgress(character: Character): number {
    return (character.experience / character.experienceToNext) * 100;
  }
  
  /**
   * Calculate total experience earned by a character
   */
  static getTotalExperience(character: Character): number {
    let totalExp = character.experience;
    
    // Add experience from all previous levels
    for (let level = 1; level < character.level; level++) {
      totalExp += this.getExperienceRequiredForLevel(level + 1) - 
                  this.getExperienceRequiredForLevel(level);
    }
    
    return totalExp;
  }
  
  /**
   * Create a new character with starting stats
   */
  static createCharacter(name: string, level: number = 1): Character {
    const baseHealth = 100;
    const baseAttack = 10;
    const baseDefense = 5;
    const baseSpeed = 10;
    
    // Calculate stats for the given level
    const health = baseHealth + (level - 1) * this.HEALTH_PER_LEVEL;
    const attack = baseAttack + (level - 1) * this.ATTACK_PER_LEVEL;
    const defense = baseDefense + (level - 1) * this.DEFENSE_PER_LEVEL;
    const speed = baseSpeed + (level - 1) * this.SPEED_PER_LEVEL;
    
    return {
      id: `char-${Date.now()}`,
      name,
      health,
      maxHealth: health,
      attack,
      defense,
      speed,
      level,
      experience: 0,
      experienceToNext: this.getExperienceRequiredForLevel(level + 1) - 
                       this.getExperienceRequiredForLevel(level),
      gold: 0,
      inventory: {
        items: new Array(4).fill(null),
        maxSlots: 4
      },
      statusEffects: [],
      position: { x: 0, y: 0 }
    };
  }
  
  /**
   * Scale enemy stats based on player level
   */
  static scaleEnemyToLevel(baseEnemy: Character, targetLevel: number): Character {
    const levelDifference = targetLevel - baseEnemy.level;
    
    // Scale stats based on level difference
    const scaledEnemy = { ...baseEnemy };
    scaledEnemy.level = targetLevel;
    
    // Apply scaling factor (10% per level)
    const scaleFactor = 1 + (levelDifference * 0.1);
    
    scaledEnemy.maxHealth = Math.floor(baseEnemy.maxHealth * scaleFactor);
    scaledEnemy.health = scaledEnemy.maxHealth;
    scaledEnemy.attack = Math.floor(baseEnemy.attack * scaleFactor);
    scaledEnemy.defense = Math.floor(baseEnemy.defense * scaleFactor);
    scaledEnemy.speed = Math.floor(baseEnemy.speed * scaleFactor);
    
    // Scale gold rewards
    scaledEnemy.gold = Math.floor(baseEnemy.gold * scaleFactor);
    
    return scaledEnemy;
  }
  
  /**
   * Get stat totals including equipment bonuses
   */
  static getEffectiveStats(character: Character): {
    attack: number;
    defense: number;
    speed: number;
  } {
    let attack = character.attack;
    let defense = character.defense;
    let speed = character.speed;
    
    // Add equipment bonuses
    character.inventory.items.forEach(item => {
      if (item && item.stats) {
        if (item.type === 'WEAPON' && item.durability && item.durability > 0) {
          attack += item.stats.attack || 0;
          speed += item.stats.speed || 0;
        } else if (item.type === 'ARMOR' && item.durability && item.durability > 0) {
          defense += item.stats.defense || 0;
          speed += item.stats.speed || 0;
        }
      }
    });
    
    // Add status effect bonuses
    character.statusEffects.forEach(effect => {
      switch (effect.type) {
        case 'ENCHANT_ATTACK':
          attack += effect.power;
          break;
        case 'ENCHANT_DEFENSE':
          defense += effect.power;
          break;
        case 'ENCHANT_SPEED':
          speed += effect.power;
          break;
      }
    });
    
    return { attack, defense, speed };
  }
}