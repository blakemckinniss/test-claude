import { 
  GameState, 
  Character, 
  CombatAction, 
  Item,
  Position,
  CombatPhase
} from '../types/game';
import { CombatEngine } from './combat/CombatEngine';
import { InventoryManager } from './inventory/InventoryManager';
import { LevelingSystem } from './character/LevelingSystem';
import { StatusEffectManager } from './effects/StatusEffectManager';
import { TreasureSystem } from './treasure/TreasureSystem';

export class GameController {
  private gameState: GameState;
  private combatEngine: CombatEngine | null = null;
  
  constructor() {
    this.gameState = this.initializeNewGame();
  }
  
  /**
   * Initialize a new game
   */
  private initializeNewGame(): GameState {
    const player = LevelingSystem.createCharacter('Hero', 1);
    
    // Give player starting equipment
    const startingWeapon: Item = {
      id: 'starter-sword',
      name: 'Training Sword',
      type: 'WEAPON',
      rarity: 'COMMON',
      stats: { attack: 3 },
      durability: 50,
      maxDurability: 50,
      value: 10,
      description: 'A basic sword for beginners'
    };
    
    const startingPotion: Item = {
      id: 'starter-potion',
      name: 'Health Potion',
      type: 'CONSUMABLE',
      rarity: 'COMMON',
      stats: { health: 30 },
      value: 20,
      description: 'Restores 30 health when consumed'
    };
    
    InventoryManager.addItem(player.inventory, startingWeapon);
    InventoryManager.addItem(player.inventory, startingPotion);
    
    // Give starting gold
    player.gold = 50;
    
    // Generate some treasure chests
    const treasureChests = [
      TreasureSystem.generateTreasureChest({ x: 5, y: 5 }, 1),
      TreasureSystem.generateTreasureChest({ x: 10, y: 3 }, 2),
      TreasureSystem.generateTreasureChest({ x: 15, y: 8 }, 3)
    ];
    
    return {
      player,
      currentCombat: null,
      treasureChests,
      gameTime: 0,
      difficulty: 'NORMAL'
    };
  }
  
  /**
   * Start a new combat encounter
   */
  startCombat(enemy: Character): void {
    this.combatEngine = new CombatEngine(this.gameState.player, enemy);
    this.gameState.currentCombat = this.combatEngine.getCombatState();
  }
  
  /**
   * Execute a combat action
   */
  executeCombatAction(action: CombatAction): void {
    if (!this.combatEngine || !this.gameState.currentCombat) {
      return;
    }
    
    // Player action
    this.gameState.currentCombat = this.combatEngine.executeAction(action);
    
    // If combat is still active and it's enemy turn, execute enemy AI
    if (this.gameState.currentCombat.isActive && !this.combatEngine.isPlayerTurn()) {
      this.executeEnemyAI();
    }
    
    // Check if combat ended
    if (!this.gameState.currentCombat.isActive) {
      this.handleCombatEnd();
    }
  }
  
  /**
   * Execute enemy AI
   */
  private executeEnemyAI(): void {
    if (!this.combatEngine || !this.gameState.currentCombat) {
      return;
    }
    
    const enemy = this.gameState.currentCombat.enemy;
    const player = this.gameState.currentCombat.player;
    
    // Simple AI logic
    let action: CombatAction;
    
    // If health is low, try to use healing item or defend
    if (enemy.health < enemy.maxHealth * 0.3) {
      const healingItem = enemy.inventory.items.find(
        item => item?.type === 'CONSUMABLE' && item.stats?.health
      );
      
      if (healingItem) {
        action = { type: 'item', itemId: healingItem.id };
      } else {
        action = { type: 'defend' };
      }
    } else {
      // Otherwise attack most of the time
      const rand = Math.random();
      if (rand < 0.7) {
        action = { type: 'attack' };
      } else if (rand < 0.9) {
        action = { type: 'defend' };
      } else {
        // Try to flee if losing badly
        action = { type: 'flee' };
      }
    }
    
    this.gameState.currentCombat = this.combatEngine.executeAction(action);
  }
  
  /**
   * Handle combat end
   */
  private handleCombatEnd(): void {
    if (!this.combatEngine || !this.gameState.currentCombat) {
      return;
    }
    
    // If player won, grant rewards
    if (this.gameState.currentCombat.phase === CombatPhase.REWARD) {
      const rewards = this.combatEngine.getRewards();
      
      // Add experience
      const levelUpResults = LevelingSystem.addExperience(
        this.gameState.player, 
        rewards.experience
      );
      
      // Add gold
      this.gameState.player.gold += rewards.gold;
      
      // Try to add items to inventory
      rewards.items.forEach(item => {
        InventoryManager.addItem(this.gameState.player.inventory, item);
      });
    }
    
    // Clear combat state
    this.gameState.currentCombat = null;
    this.combatEngine = null;
  }
  
  /**
   * Move player to a new position
   */
  movePlayer(newPosition: Position): void {
    this.gameState.player.position = newPosition;
    
    // Check for treasure at new position
    const chest = this.gameState.treasureChests.find(
      chest => !chest.opened && 
      chest.position.x === newPosition.x && 
      chest.position.y === newPosition.y
    );
    
    if (chest) {
      this.openTreasureChest(chest);
    }
  }
  
  /**
   * Open a treasure chest
   */
  private openTreasureChest(chest: TreasureChest): void {
    const result = TreasureSystem.openTreasureChest(chest, this.gameState.player);
    
    // Log results (in a real game, this would trigger UI notifications)
    console.log(`Found ${result.gold} gold!`);
    result.items.forEach(item => {
      console.log(`Found ${item.name}!`);
    });
    result.dropped.forEach(item => {
      console.log(`${item.name} was dropped (inventory full)!`);
    });
  }
  
  /**
   * Use an item from inventory
   */
  useItem(itemId: string): boolean {
    return InventoryManager.useItem(this.gameState.player, itemId);
  }
  
  /**
   * Drop an item from inventory
   */
  dropItem(slotIndex: number): Item | null {
    return InventoryManager.dropItemAtSlot(this.gameState.player.inventory, slotIndex);
  }
  
  /**
   * Buy item from shop
   */
  buyItem(item: Item): boolean {
    if (this.gameState.player.gold < item.value) {
      return false; // Not enough gold
    }
    
    if (!InventoryManager.hasSpace(this.gameState.player.inventory)) {
      return false; // Inventory full
    }
    
    this.gameState.player.gold -= item.value;
    return InventoryManager.addItem(this.gameState.player.inventory, item);
  }
  
  /**
   * Sell item from inventory
   */
  sellItem(itemId: string): boolean {
    const item = InventoryManager.removeItem(this.gameState.player.inventory, itemId);
    
    if (!item) {
      return false;
    }
    
    const sellPrice = TreasureSystem.calculateSellPrice(item);
    this.gameState.player.gold += sellPrice;
    
    return true;
  }
  
  /**
   * Apply a status effect to the player
   */
  applyStatusEffect(effect: StatusEffect): void {
    StatusEffectManager.applyEffect(this.gameState.player, effect);
  }
  
  /**
   * Process turn-based effects (called at start of each turn)
   */
  processTurnEffects(): void {
    const results = StatusEffectManager.processTurnEffects(this.gameState.player);
    
    // In a real game, these results would be displayed in the UI
    results.forEach(result => {
      console.log(`${this.gameState.player.name} ${result.result}`);
    });
    
    // Increment game time
    this.gameState.gameTime++;
  }
  
  /**
   * Get current game state
   */
  getGameState(): GameState {
    return this.gameState;
  }
  
  /**
   * Save game state
   */
  saveGame(): string {
    return JSON.stringify(this.gameState);
  }
  
  /**
   * Load game state
   */
  loadGame(saveData: string): void {
    try {
      this.gameState = JSON.parse(saveData);
      this.combatEngine = null; // Combat state will be recreated if needed
    } catch (error) {
      console.error('Failed to load game:', error);
    }
  }
  
  /**
   * Get player's effective stats (including equipment and effects)
   */
  getPlayerEffectiveStats() {
    return LevelingSystem.getEffectiveStats(this.gameState.player);
  }
  
  /**
   * Generate a random enemy based on player level
   */
  generateRandomEnemy(): Character {
    const enemyTypes = [
      { name: 'Goblin', healthMod: 0.8, attackMod: 0.9, defenseMod: 0.7, speedMod: 1.2 },
      { name: 'Orc', healthMod: 1.2, attackMod: 1.1, defenseMod: 1.0, speedMod: 0.8 },
      { name: 'Bandit', healthMod: 1.0, attackMod: 1.0, defenseMod: 0.9, speedMod: 1.0 },
      { name: 'Wolf', healthMod: 0.7, attackMod: 1.2, defenseMod: 0.6, speedMod: 1.5 },
      { name: 'Skeleton', healthMod: 0.9, attackMod: 0.8, defenseMod: 1.2, speedMod: 0.9 }
    ];
    
    const enemyType = enemyTypes[Math.floor(Math.random() * enemyTypes.length)];
    const enemyLevel = Math.max(1, this.gameState.player.level + Math.floor(Math.random() * 3) - 1);
    
    const baseEnemy = LevelingSystem.createCharacter(enemyType.name, 1);
    
    // Apply type modifiers
    baseEnemy.maxHealth = Math.floor(baseEnemy.maxHealth * enemyType.healthMod);
    baseEnemy.health = baseEnemy.maxHealth;
    baseEnemy.attack = Math.floor(baseEnemy.attack * enemyType.attackMod);
    baseEnemy.defense = Math.floor(baseEnemy.defense * enemyType.defenseMod);
    baseEnemy.speed = Math.floor(baseEnemy.speed * enemyType.speedMod);
    
    // Scale to appropriate level
    const scaledEnemy = LevelingSystem.scaleEnemyToLevel(baseEnemy, enemyLevel);
    
    // Give enemy some items
    if (Math.random() < 0.3) {
      const weapon = TreasureSystem.generateRandomItem(enemyLevel);
      if (weapon.type === 'WEAPON') {
        InventoryManager.addItem(scaledEnemy.inventory, weapon);
      }
    }
    
    if (Math.random() < 0.5) {
      const potion: Item = {
        id: `enemy-potion-${Date.now()}`,
        name: 'Health Potion',
        type: 'CONSUMABLE',
        rarity: 'COMMON',
        stats: { health: 20 + enemyLevel * 5 },
        value: 20,
        description: 'Restores health when consumed'
      };
      InventoryManager.addItem(scaledEnemy.inventory, potion);
    }
    
    return scaledEnemy;
  }
}