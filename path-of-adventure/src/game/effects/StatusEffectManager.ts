import { Character, StatusEffect, StatusEffectType } from '../../types/game';

export class StatusEffectManager {
  /**
   * Apply a status effect to a character
   * Handles stacking rules and duration management
   */
  static applyEffect(character: Character, effect: StatusEffect): void {
    // Check if character already has this type of effect
    const existingEffectIndex = character.statusEffects.findIndex(
      e => e.type === effect.type && e.name === effect.name
    );
    
    if (existingEffectIndex !== -1) {
      // Handle stacking rules
      const existingEffect = character.statusEffects[existingEffectIndex];
      
      switch (effect.type) {
        case StatusEffectType.POISON:
        case StatusEffectType.REGENERATION:
          // These stack in power but refresh duration
          existingEffect.power += effect.power;
          existingEffect.duration = Math.max(existingEffect.duration, effect.duration);
          break;
          
        case StatusEffectType.ENCHANT_ATTACK:
        case StatusEffectType.ENCHANT_DEFENSE:
        case StatusEffectType.ENCHANT_SPEED:
          // These replace with the stronger effect
          if (effect.power > existingEffect.power) {
            existingEffect.power = effect.power;
            existingEffect.duration = effect.duration;
          } else {
            // Just refresh duration if new effect is weaker
            existingEffect.duration = Math.max(existingEffect.duration, effect.duration);
          }
          break;
          
        case StatusEffectType.STUN:
          // Stun just refreshes duration
          existingEffect.duration = Math.max(existingEffect.duration, effect.duration);
          break;
          
        case StatusEffectType.GROWTH:
          // Growth effects stack completely
          character.statusEffects.push({ ...effect });
          break;
      }
    } else {
      // Add new effect
      character.statusEffects.push({ ...effect });
    }
  }
  
  /**
   * Remove a specific status effect
   */
  static removeEffect(character: Character, effectId: string): void {
    character.statusEffects = character.statusEffects.filter(e => e.id !== effectId);
  }
  
  /**
   * Remove all effects of a specific type
   */
  static removeEffectsByType(character: Character, type: StatusEffectType): void {
    character.statusEffects = character.statusEffects.filter(e => e.type !== type);
  }
  
  /**
   * Process status effects at the start of a turn
   * Returns array of effect results for UI display
   */
  static processTurnEffects(character: Character): Array<{
    effect: StatusEffect;
    result: string;
    value?: number;
  }> {
    const results: Array<{ effect: StatusEffect; result: string; value?: number }> = [];
    
    // Process each effect and reduce duration
    character.statusEffects = character.statusEffects.filter(effect => {
      let keepEffect = true;
      
      switch (effect.type) {
        case StatusEffectType.POISON:
          const poisonDamage = effect.power;
          character.health = Math.max(0, character.health - poisonDamage);
          results.push({
            effect,
            result: `takes ${poisonDamage} poison damage`,
            value: -poisonDamage
          });
          break;
          
        case StatusEffectType.REGENERATION:
          const healAmount = effect.power;
          const actualHeal = Math.min(healAmount, character.maxHealth - character.health);
          character.health += actualHeal;
          results.push({
            effect,
            result: `regenerates ${actualHeal} health`,
            value: actualHeal
          });
          break;
          
        case StatusEffectType.GROWTH:
          // Growth permanently increases stats
          character.maxHealth += 2;
          character.health += 2;
          character.attack += 1;
          results.push({
            effect,
            result: `grows stronger! +2 HP, +1 ATK`,
            value: 2
          });
          break;
          
        case StatusEffectType.STUN:
          results.push({
            effect,
            result: `is stunned and cannot act!`,
            value: 0
          });
          break;
          
        case StatusEffectType.ENCHANT_ATTACK:
        case StatusEffectType.ENCHANT_DEFENSE:
        case StatusEffectType.ENCHANT_SPEED:
          // These are passive and don't need processing
          break;
      }
      
      // Reduce duration
      effect.duration--;
      
      // Remove expired effects
      if (effect.duration <= 0) {
        keepEffect = false;
        results.push({
          effect,
          result: `${effect.name} has worn off`,
          value: 0
        });
      }
      
      return keepEffect;
    });
    
    return results;
  }
  
  /**
   * Check if character has a specific effect type
   */
  static hasEffectType(character: Character, type: StatusEffectType): boolean {
    return character.statusEffects.some(e => e.type === type);
  }
  
  /**
   * Get total power of all effects of a specific type
   */
  static getEffectPower(character: Character, type: StatusEffectType): number {
    return character.statusEffects
      .filter(e => e.type === type)
      .reduce((total, effect) => total + effect.power, 0);
  }
  
  /**
   * Clear all negative effects (for cleanse items/abilities)
   */
  static clearNegativeEffects(character: Character): void {
    const negativeTypes = [StatusEffectType.POISON, StatusEffectType.STUN];
    character.statusEffects = character.statusEffects.filter(
      e => !negativeTypes.includes(e.type)
    );
  }
  
  /**
   * Clear all positive effects (for dispel abilities)
   */
  static clearPositiveEffects(character: Character): void {
    const positiveTypes = [
      StatusEffectType.REGENERATION,
      StatusEffectType.GROWTH,
      StatusEffectType.ENCHANT_ATTACK,
      StatusEffectType.ENCHANT_DEFENSE,
      StatusEffectType.ENCHANT_SPEED
    ];
    character.statusEffects = character.statusEffects.filter(
      e => !positiveTypes.includes(e.type)
    );
  }
  
  /**
   * Create common status effects
   */
  static createPoison(power: number, duration: number): StatusEffect {
    return {
      id: `poison-${Date.now()}`,
      name: 'Poison',
      type: StatusEffectType.POISON,
      duration,
      power,
      description: `Takes ${power} damage per turn`
    };
  }
  
  static createRegeneration(power: number, duration: number): StatusEffect {
    return {
      id: `regen-${Date.now()}`,
      name: 'Regeneration',
      type: StatusEffectType.REGENERATION,
      duration,
      power,
      description: `Heals ${power} health per turn`
    };
  }
  
  static createStun(duration: number): StatusEffect {
    return {
      id: `stun-${Date.now()}`,
      name: 'Stun',
      type: StatusEffectType.STUN,
      duration,
      power: 0,
      description: `Cannot act for ${duration} turn(s)`
    };
  }
  
  static createGrowth(duration: number): StatusEffect {
    return {
      id: `growth-${Date.now()}`,
      name: 'Growth',
      type: StatusEffectType.GROWTH,
      duration,
      power: 1,
      description: `Permanently gain +2 HP and +1 ATK per turn`
    };
  }
  
  static createAttackBoost(power: number, duration: number): StatusEffect {
    return {
      id: `atk-boost-${Date.now()}`,
      name: 'Attack Boost',
      type: StatusEffectType.ENCHANT_ATTACK,
      duration,
      power,
      description: `+${power} attack power`
    };
  }
  
  static createDefenseBoost(power: number, duration: number): StatusEffect {
    return {
      id: `def-boost-${Date.now()}`,
      name: 'Defense Boost',
      type: StatusEffectType.ENCHANT_DEFENSE,
      duration,
      power,
      description: `+${power} defense`
    };
  }
  
  static createSpeedBoost(power: number, duration: number): StatusEffect {
    return {
      id: `spd-boost-${Date.now()}`,
      name: 'Speed Boost',
      type: StatusEffectType.ENCHANT_SPEED,
      duration,
      power,
      description: `+${power} speed`
    };
  }
}