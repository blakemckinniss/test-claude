import { 
  Character, 
  CombatState, 
  CombatPhase, 
  CombatAction, 
  DamageResult,
  CombatLogEntry,
  StatusEffectType,
  Item
} from '../../types/game';

export class CombatEngine {
  private combatState: CombatState;
  
  constructor(player: Character, enemy: Character) {
    this.combatState = {
      player: { ...player },
      enemy: { ...enemy },
      turn: this.determineFirstTurn(player, enemy),
      phase: CombatPhase.ATTACK,
      turnCount: 1,
      combatLog: [],
      isActive: true
    };
    
    this.addLogEntry(`Combat started! ${player.name} vs ${enemy.name}`, 'info');
    this.addLogEntry(`${this.combatState.turn === 'PLAYER' ? player.name : enemy.name} goes first!`, 'info');
  }
  
  private determineFirstTurn(player: Character, enemy: Character): 'PLAYER' | 'ENEMY' {
    // Speed determines who goes first, with some randomness
    const playerSpeed = player.speed + Math.random() * 10;
    const enemySpeed = enemy.speed + Math.random() * 10;
    return playerSpeed >= enemySpeed ? 'PLAYER' : 'ENEMY';
  }
  
  public executeAction(action: CombatAction): CombatState {
    if (!this.combatState.isActive) {
      return this.combatState;
    }
    
    // Apply status effects at the start of turn
    if (this.combatState.phase === CombatPhase.ATTACK) {
      this.applyStatusEffects();
    }
    
    switch (action.type) {
      case 'attack':
        this.handleAttack();
        break;
      case 'defend':
        this.handleDefend();
        break;
      case 'item':
        if (action.itemId) {
          this.handleItemUse(action.itemId);
        }
        break;
      case 'flee':
        this.handleFlee();
        break;
    }
    
    // Check for combat end conditions
    this.checkCombatEnd();
    
    // Progress turn if combat is still active
    if (this.combatState.isActive) {
      this.progressTurn();
    }
    
    return this.combatState;
  }
  
  private handleAttack(): void {
    const attacker = this.combatState.turn === 'PLAYER' 
      ? this.combatState.player 
      : this.combatState.enemy;
    const defender = this.combatState.turn === 'PLAYER' 
      ? this.combatState.enemy 
      : this.combatState.player;
    
    const result = this.calculateDamage(attacker, defender);
    
    if (result.dodged) {
      this.addLogEntry(`${defender.name} dodged the attack!`, 'info');
    } else if (result.blocked) {
      this.addLogEntry(`${defender.name} blocked the attack!`, 'info');
    } else {
      defender.health = Math.max(0, defender.health - result.damage);
      const critText = result.isCritical ? ' Critical hit!' : '';
      this.addLogEntry(
        `${attacker.name} deals ${result.damage} damage to ${defender.name}!${critText}`,
        'damage'
      );
      
      // Apply weapon durability loss
      this.applyWeaponDurabilityLoss(attacker);
    }
  }
  
  private handleDefend(): void {
    const defender = this.combatState.turn === 'PLAYER' 
      ? this.combatState.player 
      : this.combatState.enemy;
    
    // Defending reduces damage taken next turn and may restore some health
    const healAmount = Math.floor(defender.maxHealth * 0.05);
    defender.health = Math.min(defender.maxHealth, defender.health + healAmount);
    
    this.addLogEntry(`${defender.name} defends and recovers ${healAmount} health!`, 'heal');
    
    // Add temporary defense boost (stored as a status effect)
    defender.statusEffects.push({
      id: 'defend-boost',
      name: 'Defensive Stance',
      type: StatusEffectType.ENCHANT_DEFENSE,
      duration: 1,
      power: Math.floor(defender.defense * 0.5),
      description: 'Increased defense from defending'
    });
  }
  
  private handleItemUse(itemId: string): void {
    const user = this.combatState.turn === 'PLAYER' 
      ? this.combatState.player 
      : this.combatState.enemy;
    
    const itemIndex = user.inventory.items.findIndex(item => item?.id === itemId);
    if (itemIndex === -1 || !user.inventory.items[itemIndex]) {
      this.addLogEntry(`Item not found!`, 'info');
      return;
    }
    
    const item = user.inventory.items[itemIndex]!;
    
    // Use consumable item effects
    if (item.type === 'CONSUMABLE') {
      this.applyConsumableEffect(user, item);
      // Remove consumable after use
      user.inventory.items[itemIndex] = null;
    }
  }
  
  private handleFlee(): void {
    const fleeing = this.combatState.turn === 'PLAYER' 
      ? this.combatState.player 
      : this.combatState.enemy;
    
    // Success based on speed difference
    const speedDiff = fleeing.speed - (this.combatState.turn === 'PLAYER' 
      ? this.combatState.enemy.speed 
      : this.combatState.player.speed);
    
    const fleeChance = 0.3 + Math.max(0, speedDiff * 0.05);
    
    if (Math.random() < fleeChance) {
      this.addLogEntry(`${fleeing.name} fled from battle!`, 'info');
      this.combatState.isActive = false;
      this.combatState.phase = CombatPhase.ENDED;
    } else {
      this.addLogEntry(`${fleeing.name} couldn't escape!`, 'info');
    }
  }
  
  private calculateDamage(attacker: Character, defender: Character): DamageResult {
    // Base damage calculation
    let damage = attacker.attack;
    
    // Add weapon damage if equipped
    const weapon = attacker.inventory.items.find(item => 
      item?.type === 'WEAPON' && item.durability && item.durability > 0
    );
    
    if (weapon?.stats?.attack) {
      damage += weapon.stats.attack;
    }
    
    // Apply attack enchantments
    const attackBoost = attacker.statusEffects
      .filter(e => e.type === StatusEffectType.ENCHANT_ATTACK)
      .reduce((sum, e) => sum + e.power, 0);
    damage += attackBoost;
    
    // Calculate defense
    let defense = defender.defense;
    
    // Add armor defense
    const armor = defender.inventory.items.find(item => 
      item?.type === 'ARMOR' && item.durability && item.durability > 0
    );
    
    if (armor?.stats?.defense) {
      defense += armor.stats.defense;
    }
    
    // Apply defense enchantments
    const defenseBoost = defender.statusEffects
      .filter(e => e.type === StatusEffectType.ENCHANT_DEFENSE)
      .reduce((sum, e) => sum + e.power, 0);
    defense += defenseBoost;
    
    // Dodge chance based on speed
    const dodgeChance = defender.speed / (defender.speed + attacker.speed) * 0.2;
    if (Math.random() < dodgeChance) {
      return { damage: 0, isCritical: false, dodged: true, blocked: false };
    }
    
    // Block chance based on defense
    const blockChance = defense / (defense + damage) * 0.15;
    if (Math.random() < blockChance) {
      return { damage: 0, isCritical: false, dodged: false, blocked: true };
    }
    
    // Critical hit chance
    const critChance = 0.1 + (attacker.speed / 100);
    const isCritical = Math.random() < critChance;
    
    if (isCritical) {
      damage *= 1.5;
    }
    
    // Apply defense reduction
    const finalDamage = Math.max(1, Math.floor(damage - defense * 0.5));
    
    return {
      damage: finalDamage,
      isCritical,
      dodged: false,
      blocked: false
    };
  }
  
  private applyStatusEffects(): void {
    const character = this.combatState.turn === 'PLAYER' 
      ? this.combatState.player 
      : this.combatState.enemy;
    
    // Apply effects and reduce duration
    character.statusEffects = character.statusEffects.filter(effect => {
      switch (effect.type) {
        case StatusEffectType.POISON:
          const poisonDamage = effect.power;
          character.health = Math.max(0, character.health - poisonDamage);
          this.addLogEntry(`${character.name} takes ${poisonDamage} poison damage!`, 'damage');
          break;
          
        case StatusEffectType.REGENERATION:
          const healAmount = effect.power;
          character.health = Math.min(character.maxHealth, character.health + healAmount);
          this.addLogEntry(`${character.name} regenerates ${healAmount} health!`, 'heal');
          break;
          
        case StatusEffectType.STUN:
          this.addLogEntry(`${character.name} is stunned and cannot act!`, 'effect');
          // Skip the turn
          this.combatState.phase = CombatPhase.DEFEND;
          break;
      }
      
      effect.duration--;
      return effect.duration > 0;
    });
  }
  
  private applyWeaponDurabilityLoss(attacker: Character): void {
    const weapon = attacker.inventory.items.find(item => 
      item?.type === 'WEAPON' && item.durability && item.durability > 0
    );
    
    if (weapon && weapon.durability !== undefined) {
      weapon.durability--;
      
      if (weapon.durability <= 0) {
        this.addLogEntry(`${weapon.name} has broken!`, 'info');
      } else if (weapon.durability <= 5) {
        this.addLogEntry(`${weapon.name} is about to break! (${weapon.durability} uses left)`, 'info');
      }
    }
  }
  
  private applyConsumableEffect(user: Character, item: Item): void {
    if (item.stats) {
      if (item.stats.health) {
        const healAmount = item.stats.health;
        user.health = Math.min(user.maxHealth, user.health + healAmount);
        this.addLogEntry(`${user.name} uses ${item.name} and heals ${healAmount} health!`, 'heal');
      }
      
      // Apply temporary stat boosts as status effects
      if (item.stats.attack) {
        user.statusEffects.push({
          id: `boost-attack-${Date.now()}`,
          name: 'Attack Boost',
          type: StatusEffectType.ENCHANT_ATTACK,
          duration: 3,
          power: item.stats.attack,
          description: `+${item.stats.attack} attack from ${item.name}`
        });
        this.addLogEntry(`${user.name} gains +${item.stats.attack} attack!`, 'effect');
      }
      
      if (item.stats.defense) {
        user.statusEffects.push({
          id: `boost-defense-${Date.now()}`,
          name: 'Defense Boost',
          type: StatusEffectType.ENCHANT_DEFENSE,
          duration: 3,
          power: item.stats.defense,
          description: `+${item.stats.defense} defense from ${item.name}`
        });
        this.addLogEntry(`${user.name} gains +${item.stats.defense} defense!`, 'effect');
      }
      
      if (item.stats.speed) {
        user.statusEffects.push({
          id: `boost-speed-${Date.now()}`,
          name: 'Speed Boost',
          type: StatusEffectType.ENCHANT_SPEED,
          duration: 3,
          power: item.stats.speed,
          description: `+${item.stats.speed} speed from ${item.name}`
        });
        this.addLogEntry(`${user.name} gains +${item.stats.speed} speed!`, 'effect');
      }
    }
  }
  
  private checkCombatEnd(): void {
    if (this.combatState.player.health <= 0) {
      this.addLogEntry(`${this.combatState.player.name} has been defeated!`, 'info');
      this.combatState.isActive = false;
      this.combatState.phase = CombatPhase.ENDED;
    } else if (this.combatState.enemy.health <= 0) {
      this.addLogEntry(`${this.combatState.enemy.name} has been defeated!`, 'info');
      this.combatState.isActive = false;
      this.combatState.phase = CombatPhase.REWARD;
    }
  }
  
  private progressTurn(): void {
    // Move to next phase or next turn
    if (this.combatState.phase === CombatPhase.ATTACK) {
      this.combatState.phase = CombatPhase.DEFEND;
    } else {
      // Switch turns
      this.combatState.turn = this.combatState.turn === 'PLAYER' ? 'ENEMY' : 'PLAYER';
      this.combatState.phase = CombatPhase.ATTACK;
      this.combatState.turnCount++;
    }
  }
  
  private addLogEntry(message: string, type: CombatLogEntry['type']): void {
    this.combatState.combatLog.push({
      message,
      type,
      timestamp: Date.now()
    });
  }
  
  public getCombatState(): CombatState {
    return { ...this.combatState };
  }
  
  public isPlayerTurn(): boolean {
    return this.combatState.turn === 'PLAYER' && this.combatState.isActive;
  }
  
  public getRewards(): { experience: number; gold: number; items: Item[] } {
    if (this.combatState.phase !== CombatPhase.REWARD) {
      return { experience: 0, gold: 0, items: [] };
    }
    
    // Calculate rewards based on enemy level and rarity
    const baseExp = this.combatState.enemy.level * 10;
    const baseGold = this.combatState.enemy.level * 5;
    
    return {
      experience: baseExp + Math.floor(Math.random() * baseExp),
      gold: baseGold + Math.floor(Math.random() * baseGold),
      items: [] // Items would be generated based on enemy type and level
    };
  }
}