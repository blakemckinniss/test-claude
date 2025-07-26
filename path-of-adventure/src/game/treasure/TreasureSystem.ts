import { Item, ItemType, ItemRarity, TreasureChest, Position, Character } from '../../types/game';

export class TreasureSystem {
  private static readonly RARITY_WEIGHTS = {
    [ItemRarity.COMMON]: 50,
    [ItemRarity.UNCOMMON]: 30,
    [ItemRarity.RARE]: 15,
    [ItemRarity.EPIC]: 4,
    [ItemRarity.LEGENDARY]: 1
  };
  
  /**
   * Generate a treasure chest at a position
   */
  static generateTreasureChest(position: Position, level: number): TreasureChest {
    const itemCount = Math.floor(Math.random() * 3) + 1; // 1-3 items
    const items: Item[] = [];
    
    for (let i = 0; i < itemCount; i++) {
      items.push(this.generateRandomItem(level));
    }
    
    // Generate gold based on level
    const baseGold = level * 10;
    const gold = baseGold + Math.floor(Math.random() * baseGold);
    
    return {
      id: `chest-${Date.now()}-${Math.random()}`,
      position,
      items,
      gold,
      opened: false
    };
  }
  
  /**
   * Generate a random item based on level
   */
  static generateRandomItem(level: number): Item {
    const rarity = this.rollRarity(level);
    const type = this.rollItemType();
    
    switch (type) {
      case ItemType.WEAPON:
        return this.generateWeapon(level, rarity);
      case ItemType.ARMOR:
        return this.generateArmor(level, rarity);
      case ItemType.CONSUMABLE:
        return this.generateConsumable(level, rarity);
      case ItemType.TREASURE:
        return this.generateTreasure(level, rarity);
      default:
        return this.generateTreasure(level, rarity);
    }
  }
  
  /**
   * Roll for item rarity based on level
   */
  private static rollRarity(level: number): ItemRarity {
    // Higher levels have better chances for rare items
    const levelBonus = level * 2;
    const totalWeight = Object.values(this.RARITY_WEIGHTS).reduce((sum, w) => sum + w, 0);
    let roll = Math.random() * (totalWeight + levelBonus);
    
    // Check from highest rarity to lowest
    const rarities = [
      ItemRarity.LEGENDARY,
      ItemRarity.EPIC,
      ItemRarity.RARE,
      ItemRarity.UNCOMMON,
      ItemRarity.COMMON
    ];
    
    for (const rarity of rarities) {
      roll -= this.RARITY_WEIGHTS[rarity] + (rarity === ItemRarity.LEGENDARY ? levelBonus : 0);
      if (roll <= 0) {
        return rarity;
      }
    }
    
    return ItemRarity.COMMON;
  }
  
  /**
   * Roll for item type
   */
  private static rollItemType(): ItemType {
    const weights = {
      [ItemType.WEAPON]: 25,
      [ItemType.ARMOR]: 25,
      [ItemType.CONSUMABLE]: 35,
      [ItemType.TREASURE]: 15
    };
    
    const totalWeight = Object.values(weights).reduce((sum, w) => sum + w, 0);
    let roll = Math.random() * totalWeight;
    
    for (const [type, weight] of Object.entries(weights)) {
      roll -= weight;
      if (roll <= 0) {
        return type as ItemType;
      }
    }
    
    return ItemType.TREASURE;
  }
  
  /**
   * Generate a weapon
   */
  private static generateWeapon(level: number, rarity: ItemRarity): Item {
    const weaponNames = {
      [ItemRarity.COMMON]: ['Rusty Sword', 'Wooden Club', 'Stone Axe'],
      [ItemRarity.UNCOMMON]: ['Iron Sword', 'Steel Mace', 'Sharp Dagger'],
      [ItemRarity.RARE]: ['Enchanted Blade', 'Crystal Staff', 'Silver Spear'],
      [ItemRarity.EPIC]: ['Dragonbane', 'Shadowstrike', 'Thunderfury'],
      [ItemRarity.LEGENDARY]: ['Excalibur', 'Ragnarok', 'Soulreaper']
    };
    
    const names = weaponNames[rarity];
    const name = names[Math.floor(Math.random() * names.length)];
    
    // Calculate stats based on level and rarity
    const rarityMultiplier = {
      [ItemRarity.COMMON]: 1,
      [ItemRarity.UNCOMMON]: 1.5,
      [ItemRarity.RARE]: 2,
      [ItemRarity.EPIC]: 3,
      [ItemRarity.LEGENDARY]: 5
    };
    
    const baseAttack = 5 + level * 2;
    const attack = Math.floor(baseAttack * rarityMultiplier[rarity]);
    
    // Calculate durability
    const baseDurability = 20 + level * 5;
    const durability = Math.floor(baseDurability * rarityMultiplier[rarity]);
    
    // Calculate value
    const baseValue = 50 + level * 10;
    const value = Math.floor(baseValue * rarityMultiplier[rarity]);
    
    return {
      id: `weapon-${Date.now()}-${Math.random()}`,
      name,
      type: ItemType.WEAPON,
      rarity,
      stats: {
        attack,
        speed: rarity === ItemRarity.EPIC || rarity === ItemRarity.LEGENDARY 
          ? Math.floor(Math.random() * 5) + 1 
          : 0
      },
      durability,
      maxDurability: durability,
      value,
      description: `A ${rarity.toLowerCase()} weapon that grants +${attack} attack power.`
    };
  }
  
  /**
   * Generate armor
   */
  private static generateArmor(level: number, rarity: ItemRarity): Item {
    const armorNames = {
      [ItemRarity.COMMON]: ['Leather Vest', 'Wooden Shield', 'Cloth Robes'],
      [ItemRarity.UNCOMMON]: ['Chainmail', 'Iron Plate', 'Reinforced Leather'],
      [ItemRarity.RARE]: ['Mithril Mail', 'Dragon Scale', 'Enchanted Robes'],
      [ItemRarity.EPIC]: ['Aegis Plate', 'Shadow Cloak', 'Titan Armor'],
      [ItemRarity.LEGENDARY]: ['Godplate', 'Ethereal Vestments', 'Invincible Mail']
    };
    
    const names = armorNames[rarity];
    const name = names[Math.floor(Math.random() * names.length)];
    
    const rarityMultiplier = {
      [ItemRarity.COMMON]: 1,
      [ItemRarity.UNCOMMON]: 1.5,
      [ItemRarity.RARE]: 2,
      [ItemRarity.EPIC]: 3,
      [ItemRarity.LEGENDARY]: 5
    };
    
    const baseDefense = 3 + level;
    const defense = Math.floor(baseDefense * rarityMultiplier[rarity]);
    
    const baseDurability = 30 + level * 5;
    const durability = Math.floor(baseDurability * rarityMultiplier[rarity]);
    
    const baseValue = 40 + level * 8;
    const value = Math.floor(baseValue * rarityMultiplier[rarity]);
    
    return {
      id: `armor-${Date.now()}-${Math.random()}`,
      name,
      type: ItemType.ARMOR,
      rarity,
      stats: {
        defense,
        health: rarity === ItemRarity.EPIC || rarity === ItemRarity.LEGENDARY 
          ? Math.floor(Math.random() * 20) + 10 
          : 0
      },
      durability,
      maxDurability: durability,
      value,
      description: `${rarity.toLowerCase()} armor that grants +${defense} defense.`
    };
  }
  
  /**
   * Generate consumable
   */
  private static generateConsumable(level: number, rarity: ItemRarity): Item {
    const consumableTypes = [
      { 
        name: 'Health Potion', 
        stat: 'health', 
        baseValue: 20,
        description: 'Restores health when consumed'
      },
      { 
        name: 'Strength Elixir', 
        stat: 'attack', 
        baseValue: 5,
        description: 'Temporarily increases attack power'
      },
      { 
        name: 'Iron Skin Potion', 
        stat: 'defense', 
        baseValue: 5,
        description: 'Temporarily increases defense'
      },
      { 
        name: 'Swiftness Draught', 
        stat: 'speed', 
        baseValue: 5,
        description: 'Temporarily increases speed'
      }
    ];
    
    const consumableType = consumableTypes[Math.floor(Math.random() * consumableTypes.length)];
    
    const rarityMultiplier = {
      [ItemRarity.COMMON]: 1,
      [ItemRarity.UNCOMMON]: 1.5,
      [ItemRarity.RARE]: 2,
      [ItemRarity.EPIC]: 3,
      [ItemRarity.LEGENDARY]: 5
    };
    
    const statValue = Math.floor(
      (consumableType.baseValue + level * 2) * rarityMultiplier[rarity]
    );
    
    const prefixes = {
      [ItemRarity.COMMON]: '',
      [ItemRarity.UNCOMMON]: 'Greater ',
      [ItemRarity.RARE]: 'Superior ',
      [ItemRarity.EPIC]: 'Masterwork ',
      [ItemRarity.LEGENDARY]: 'Divine '
    };
    
    const name = prefixes[rarity] + consumableType.name;
    const value = Math.floor((10 + level * 5) * rarityMultiplier[rarity]);
    
    return {
      id: `consumable-${Date.now()}-${Math.random()}`,
      name,
      type: ItemType.CONSUMABLE,
      rarity,
      stats: {
        [consumableType.stat]: statValue
      } as any,
      value,
      description: `${consumableType.description}. Effect: +${statValue} ${consumableType.stat}`
    };
  }
  
  /**
   * Generate treasure (valuable items with no combat use)
   */
  private static generateTreasure(level: number, rarity: ItemRarity): Item {
    const treasureNames = {
      [ItemRarity.COMMON]: ['Copper Coin', 'Small Gem', 'Silver Ring'],
      [ItemRarity.UNCOMMON]: ['Gold Coin', 'Jade Figurine', 'Pearl Necklace'],
      [ItemRarity.RARE]: ['Ruby', 'Sapphire', 'Emerald'],
      [ItemRarity.EPIC]: ['Diamond', 'Ancient Artifact', 'Royal Crown'],
      [ItemRarity.LEGENDARY]: ['Philosopher\'s Stone', 'Dragon\'s Heart', 'God\'s Tear']
    };
    
    const names = treasureNames[rarity];
    const name = names[Math.floor(Math.random() * names.length)];
    
    const rarityMultiplier = {
      [ItemRarity.COMMON]: 1,
      [ItemRarity.UNCOMMON]: 3,
      [ItemRarity.RARE]: 10,
      [ItemRarity.EPIC]: 30,
      [ItemRarity.LEGENDARY]: 100
    };
    
    const baseValue = 100 + level * 20;
    const value = Math.floor(baseValue * rarityMultiplier[rarity]);
    
    return {
      id: `treasure-${Date.now()}-${Math.random()}`,
      name,
      type: ItemType.TREASURE,
      rarity,
      value,
      description: `A valuable ${rarity.toLowerCase()} treasure worth ${value} gold.`
    };
  }
  
  /**
   * Open a treasure chest and transfer contents to character
   */
  static openTreasureChest(chest: TreasureChest, character: Character): {
    items: Item[];
    gold: number;
    dropped: Item[];
  } {
    if (chest.opened) {
      return { items: [], gold: 0, dropped: [] };
    }
    
    chest.opened = true;
    const dropped: Item[] = [];
    const obtained: Item[] = [];
    
    // Add gold
    character.gold += chest.gold;
    
    // Try to add items to inventory
    chest.items.forEach(item => {
      // Check if inventory has space
      const emptySlot = character.inventory.items.findIndex(slot => slot === null);
      
      if (emptySlot !== -1) {
        character.inventory.items[emptySlot] = item;
        obtained.push(item);
      } else {
        // Inventory full, item is dropped
        dropped.push(item);
      }
    });
    
    return {
      items: obtained,
      gold: chest.gold,
      dropped
    };
  }
  
  /**
   * Generate shop inventory based on level
   */
  static generateShopInventory(level: number, itemCount: number = 6): Item[] {
    const items: Item[] = [];
    
    // Ensure at least one weapon, armor, and consumables
    items.push(this.generateWeapon(level, this.rollRarity(level)));
    items.push(this.generateArmor(level, this.rollRarity(level)));
    items.push(this.generateConsumable(level, ItemRarity.COMMON));
    items.push(this.generateConsumable(level, ItemRarity.UNCOMMON));
    
    // Fill remaining slots with random items
    for (let i = items.length; i < itemCount; i++) {
      items.push(this.generateRandomItem(level));
    }
    
    // Increase shop prices by 50%
    items.forEach(item => {
      item.value = Math.floor(item.value * 1.5);
    });
    
    return items;
  }
  
  /**
   * Calculate item sell price (typically 50% of value)
   */
  static calculateSellPrice(item: Item): number {
    let sellPrice = Math.floor(item.value * 0.5);
    
    // Damaged equipment sells for less
    if (item.durability !== undefined && item.maxDurability) {
      const durabilityRatio = item.durability / item.maxDurability;
      sellPrice = Math.floor(sellPrice * durabilityRatio);
    }
    
    return Math.max(1, sellPrice); // Always worth at least 1 gold
  }
}