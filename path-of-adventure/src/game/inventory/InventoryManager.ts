import { Character, Item, Inventory, ItemType } from '../../types/game';

export class InventoryManager {
  private static readonly MAX_INVENTORY_SLOTS = 4;
  
  /**
   * Initialize an empty inventory
   */
  static createInventory(): Inventory {
    return {
      items: new Array(this.MAX_INVENTORY_SLOTS).fill(null),
      maxSlots: this.MAX_INVENTORY_SLOTS
    };
  }
  
  /**
   * Add an item to the inventory
   * Returns true if successful, false if inventory is full
   */
  static addItem(inventory: Inventory, item: Item): boolean {
    const emptySlotIndex = inventory.items.findIndex(slot => slot === null);
    
    if (emptySlotIndex === -1) {
      return false; // Inventory full
    }
    
    inventory.items[emptySlotIndex] = item;
    return true;
  }
  
  /**
   * Remove an item from the inventory by item ID
   * Returns the removed item or null if not found
   */
  static removeItem(inventory: Inventory, itemId: string): Item | null {
    const itemIndex = inventory.items.findIndex(item => item?.id === itemId);
    
    if (itemIndex === -1 || !inventory.items[itemIndex]) {
      return null;
    }
    
    const removedItem = inventory.items[itemIndex];
    inventory.items[itemIndex] = null;
    return removedItem;
  }
  
  /**
   * Drop an item from the inventory at a specific slot
   * Returns the dropped item or null if slot is empty
   */
  static dropItemAtSlot(inventory: Inventory, slotIndex: number): Item | null {
    if (slotIndex < 0 || slotIndex >= inventory.maxSlots) {
      return null;
    }
    
    const droppedItem = inventory.items[slotIndex];
    inventory.items[slotIndex] = null;
    return droppedItem;
  }
  
  /**
   * Use an item from the inventory
   * Returns true if the item was used successfully
   */
  static useItem(character: Character, itemId: string): boolean {
    const item = character.inventory.items.find(i => i?.id === itemId);
    
    if (!item) {
      return false;
    }
    
    switch (item.type) {
      case ItemType.CONSUMABLE:
        return this.useConsumable(character, item);
        
      case ItemType.WEAPON:
      case ItemType.ARMOR:
        return this.equipItem(character, item);
        
      default:
        return false;
    }
  }
  
  /**
   * Use a consumable item
   */
  private static useConsumable(character: Character, item: Item): boolean {
    if (!item.stats) {
      return false;
    }
    
    // Apply item effects
    if (item.stats.health) {
      character.health = Math.min(
        character.maxHealth, 
        character.health + item.stats.health
      );
    }
    
    // Consumables are removed after use
    this.removeItem(character.inventory, item.id);
    return true;
  }
  
  /**
   * Equip a weapon or armor
   * Swaps with currently equipped item of the same type
   */
  private static equipItem(character: Character, newItem: Item): boolean {
    // Find currently equipped item of the same type
    const currentEquipped = character.inventory.items.find(
      item => item && item.type === newItem.type && item.id !== newItem.id
    );
    
    if (currentEquipped) {
      // Swap the items - the new item is already in inventory
      // Just need to mark which one is "equipped" (first of its type in inventory)
      const newItemIndex = character.inventory.items.findIndex(i => i?.id === newItem.id);
      const currentIndex = character.inventory.items.findIndex(i => i?.id === currentEquipped.id);
      
      if (newItemIndex !== -1 && currentIndex !== -1) {
        // Swap positions so the new item is first (equipped)
        [character.inventory.items[newItemIndex], character.inventory.items[currentIndex]] = 
        [character.inventory.items[currentIndex], character.inventory.items[newItemIndex]];
      }
    }
    
    return true;
  }
  
  /**
   * Get the currently equipped weapon
   */
  static getEquippedWeapon(inventory: Inventory): Item | null {
    return inventory.items.find(item => 
      item?.type === ItemType.WEAPON && 
      item.durability !== undefined && 
      item.durability > 0
    ) || null;
  }
  
  /**
   * Get the currently equipped armor
   */
  static getEquippedArmor(inventory: Inventory): Item | null {
    return inventory.items.find(item => 
      item?.type === ItemType.ARMOR && 
      item.durability !== undefined && 
      item.durability > 0
    ) || null;
  }
  
  /**
   * Get total inventory value
   */
  static getInventoryValue(inventory: Inventory): number {
    return inventory.items.reduce((total, item) => {
      return total + (item?.value || 0);
    }, 0);
  }
  
  /**
   * Get count of filled inventory slots
   */
  static getFilledSlots(inventory: Inventory): number {
    return inventory.items.filter(item => item !== null).length;
  }
  
  /**
   * Check if inventory has space
   */
  static hasSpace(inventory: Inventory): boolean {
    return this.getFilledSlots(inventory) < inventory.maxSlots;
  }
  
  /**
   * Sort inventory by item type and rarity
   */
  static sortInventory(inventory: Inventory): void {
    const sortOrder = {
      [ItemType.WEAPON]: 0,
      [ItemType.ARMOR]: 1,
      [ItemType.CONSUMABLE]: 2,
      [ItemType.TREASURE]: 3,
      [ItemType.QUEST]: 4
    };
    
    const rarityOrder = {
      LEGENDARY: 0,
      EPIC: 1,
      RARE: 2,
      UNCOMMON: 3,
      COMMON: 4
    };
    
    // Extract non-null items, sort them, then pad with nulls
    const items = inventory.items.filter(item => item !== null) as Item[];
    
    items.sort((a, b) => {
      // First sort by type
      const typeCompare = sortOrder[a.type] - sortOrder[b.type];
      if (typeCompare !== 0) return typeCompare;
      
      // Then by rarity
      return rarityOrder[a.rarity] - rarityOrder[b.rarity];
    });
    
    // Replace inventory items with sorted items + nulls
    inventory.items = [
      ...items,
      ...new Array(inventory.maxSlots - items.length).fill(null)
    ];
  }
  
  /**
   * Repair all equipment in inventory
   */
  static repairAllEquipment(inventory: Inventory, repairAmount: number = Infinity): void {
    inventory.items.forEach(item => {
      if (item && item.durability !== undefined && item.maxDurability) {
        item.durability = Math.min(
          item.maxDurability,
          item.durability + repairAmount
        );
      }
    });
  }
  
  /**
   * Get items by type
   */
  static getItemsByType(inventory: Inventory, type: ItemType): Item[] {
    return inventory.items.filter(item => item?.type === type) as Item[];
  }
}