import { Item, Weapon, Armor, Consumable } from '../types';

// Weapons
export const weapons: Record<string, Weapon> = {
  'iron-sword': {
    id: 'iron-sword',
    name: 'Iron Sword',
    description: 'A simple but reliable iron sword.',
    type: 'weapon',
    weaponType: 'sword',
    rarity: 'common',
    value: 100,
    stackable: false,
    damage: {
      min: 5,
      max: 10,
      type: 'physical'
    },
    attackSpeed: 1.0,
    critMultiplier: 1.5
  },
  
  'steel-sword': {
    id: 'steel-sword',
    name: 'Steel Sword',
    description: 'A well-crafted steel blade with excellent balance.',
    type: 'weapon',
    weaponType: 'sword',
    rarity: 'uncommon',
    value: 250,
    stackable: false,
    damage: {
      min: 8,
      max: 15,
      type: 'physical'
    },
    attackSpeed: 1.0,
    critMultiplier: 1.75,
    requirements: [
      {
        type: 'level',
        value: 5
      }
    ]
  },
  
  'enchanted-sword': {
    id: 'enchanted-sword',
    name: 'Enchanted Sword',
    description: 'A blade that glows with magical energy.',
    type: 'weapon',
    weaponType: 'sword',
    rarity: 'rare',
    value: 500,
    stackable: false,
    damage: {
      min: 12,
      max: 20,
      type: 'magical'
    },
    attackSpeed: 1.1,
    critMultiplier: 2.0,
    requirements: [
      {
        type: 'level',
        value: 10
      }
    ],
    specialAbility: {
      name: 'Arcane Strike',
      description: 'Unleash a blast of magical energy',
      effect: [
        {
          type: 'damage',
          target: 'enemy',
          value: 25,
          chance: 0.3
        }
      ],
      manaCost: 10
    }
  },
  
  'rusty-dagger': {
    id: 'rusty-dagger',
    name: 'Rusty Dagger',
    description: 'A worn dagger that has seen better days.',
    type: 'weapon',
    weaponType: 'dagger',
    rarity: 'common',
    value: 50,
    stackable: false,
    damage: {
      min: 3,
      max: 6,
      type: 'physical'
    },
    attackSpeed: 1.5,
    critMultiplier: 2.0
  },
  
  'steel-dagger': {
    id: 'steel-dagger',
    name: 'Steel Dagger',
    description: 'A sharp steel dagger, perfect for quick strikes.',
    type: 'weapon',
    weaponType: 'dagger',
    rarity: 'uncommon',
    value: 150,
    stackable: false,
    damage: {
      min: 5,
      max: 9,
      type: 'physical'
    },
    attackSpeed: 1.5,
    critMultiplier: 2.5,
    effects: [
      {
        type: 'stat',
        target: 'self',
        stat: 'critChance',
        value: 5
      }
    ]
  },
  
  'wooden-staff': {
    id: 'wooden-staff',
    name: 'Wooden Staff',
    description: 'A basic staff carved from oak.',
    type: 'weapon',
    weaponType: 'staff',
    rarity: 'common',
    value: 80,
    stackable: false,
    damage: {
      min: 4,
      max: 8,
      type: 'magical'
    },
    attackSpeed: 0.8,
    effects: [
      {
        type: 'stat',
        target: 'self',
        stat: 'magicPower',
        value: 5
      }
    ]
  },
  
  'hunters-bow': {
    id: 'hunters-bow',
    name: 'Hunter\'s Bow',
    description: 'A reliable bow used by hunters and scouts.',
    type: 'weapon',
    weaponType: 'bow',
    rarity: 'common',
    value: 120,
    stackable: false,
    damage: {
      min: 6,
      max: 12,
      type: 'physical'
    },
    attackSpeed: 1.2,
    critMultiplier: 2.0
  }
};

// Armor
export const armor: Record<string, Armor> = {
  'leather-armor': {
    id: 'leather-armor',
    name: 'Leather Armor',
    description: 'Light armor made from tanned hide.',
    type: 'armor',
    armorType: 'light',
    rarity: 'common',
    value: 150,
    stackable: false,
    defense: 5,
    dodgeModifier: 5
  },
  
  'chainmail': {
    id: 'chainmail',
    name: 'Chainmail',
    description: 'Interlocking metal rings provide good protection.',
    type: 'armor',
    armorType: 'medium',
    rarity: 'uncommon',
    value: 300,
    stackable: false,
    defense: 10,
    magicResist: 5,
    requirements: [
      {
        type: 'stat',
        stat: 'strength',
        value: 10
      }
    ]
  },
  
  'plate-armor': {
    id: 'plate-armor',
    name: 'Plate Armor',
    description: 'Heavy armor that offers excellent protection.',
    type: 'armor',
    armorType: 'heavy',
    rarity: 'rare',
    value: 600,
    stackable: false,
    defense: 20,
    magicResist: 10,
    dodgeModifier: -10,
    requirements: [
      {
        type: 'stat',
        stat: 'strength',
        value: 15
      },
      {
        type: 'level',
        value: 10
      }
    ]
  },
  
  'mage-robes': {
    id: 'mage-robes',
    name: 'Mage Robes',
    description: 'Enchanted robes that enhance magical abilities.',
    type: 'armor',
    armorType: 'light',
    rarity: 'uncommon',
    value: 250,
    stackable: false,
    defense: 3,
    magicResist: 15,
    effects: [
      {
        type: 'stat',
        target: 'self',
        stat: 'magicPower',
        value: 10
      }
    ]
  }
};

// Consumables
export const consumables: Record<string, Consumable> = {
  'healing-potion-small': {
    id: 'healing-potion-small',
    name: 'Small Healing Potion',
    description: 'Restores a small amount of health.',
    type: 'consumable',
    consumableType: 'potion',
    rarity: 'common',
    value: 50,
    stackable: true,
    maxStack: 10,
    useInCombat: true,
    effects: [
      {
        type: 'heal',
        target: 'self',
        value: 25
      }
    ]
  },
  
  'healing-potion-medium': {
    id: 'healing-potion-medium',
    name: 'Medium Healing Potion',
    description: 'Restores a moderate amount of health.',
    type: 'consumable',
    consumableType: 'potion',
    rarity: 'uncommon',
    value: 100,
    stackable: true,
    maxStack: 10,
    useInCombat: true,
    effects: [
      {
        type: 'heal',
        target: 'self',
        value: 50
      }
    ]
  },
  
  'healing-potion-large': {
    id: 'healing-potion-large',
    name: 'Large Healing Potion',
    description: 'Restores a large amount of health.',
    type: 'consumable',
    consumableType: 'potion',
    rarity: 'rare',
    value: 200,
    stackable: true,
    maxStack: 5,
    useInCombat: true,
    effects: [
      {
        type: 'heal',
        target: 'self',
        value: 100
      }
    ]
  },
  
  'mana-potion-small': {
    id: 'mana-potion-small',
    name: 'Small Mana Potion',
    description: 'Restores a small amount of mana.',
    type: 'consumable',
    consumableType: 'potion',
    rarity: 'common',
    value: 40,
    stackable: true,
    maxStack: 10,
    useInCombat: true,
    effects: [
      {
        type: 'stat',
        target: 'self',
        stat: 'mana',
        value: 20
      }
    ]
  },
  
  'strength-potion': {
    id: 'strength-potion',
    name: 'Potion of Strength',
    description: 'Temporarily increases your strength.',
    type: 'consumable',
    consumableType: 'potion',
    rarity: 'uncommon',
    value: 150,
    stackable: true,
    maxStack: 5,
    useInCombat: true,
    effects: [
      {
        type: 'buff',
        target: 'self',
        stat: 'strength',
        value: 5,
        duration: 10
      }
    ]
  },
  
  'speed-potion': {
    id: 'speed-potion',
    name: 'Potion of Speed',
    description: 'Temporarily increases your agility.',
    type: 'consumable',
    consumableType: 'potion',
    rarity: 'uncommon',
    value: 150,
    stackable: true,
    maxStack: 5,
    useInCombat: true,
    effects: [
      {
        type: 'buff',
        target: 'self',
        stat: 'agility',
        value: 5,
        duration: 10
      }
    ]
  },
  
  'antidote': {
    id: 'antidote',
    name: 'Antidote',
    description: 'Cures poison and prevents it for a short time.',
    type: 'consumable',
    consumableType: 'potion',
    rarity: 'common',
    value: 75,
    stackable: true,
    maxStack: 10,
    useInCombat: true,
    effects: [
      {
        type: 'special',
        target: 'self',
        value: 1 // Remove poison status
      }
    ]
  },
  
  'fire-bomb': {
    id: 'fire-bomb',
    name: 'Fire Bomb',
    description: 'Explodes on impact, dealing fire damage to enemies.',
    type: 'consumable',
    consumableType: 'bomb',
    rarity: 'uncommon',
    value: 100,
    stackable: true,
    maxStack: 5,
    useInCombat: true,
    effects: [
      {
        type: 'damage',
        target: 'all_enemies',
        value: 30
      }
    ]
  },
  
  'smoke-bomb': {
    id: 'smoke-bomb',
    name: 'Smoke Bomb',
    description: 'Creates a smoke screen, increasing dodge chance.',
    type: 'consumable',
    consumableType: 'bomb',
    rarity: 'uncommon',
    value: 80,
    stackable: true,
    maxStack: 5,
    useInCombat: true,
    effects: [
      {
        type: 'buff',
        target: 'self',
        stat: 'dodgeChance',
        value: 25,
        duration: 3
      }
    ]
  }
};

// Quest and Misc Items
export const miscItems: Record<string, Item> = {
  'torch': {
    id: 'torch',
    name: 'Torch',
    description: 'Provides light in dark places.',
    type: 'misc',
    rarity: 'common',
    value: 10,
    stackable: true,
    maxStack: 20
  },
  
  'rope': {
    id: 'rope',
    name: 'Rope',
    description: 'Useful for climbing or tying things.',
    type: 'misc',
    rarity: 'common',
    value: 20,
    stackable: true,
    maxStack: 5
  },
  
  'lockpick': {
    id: 'lockpick',
    name: 'Lockpick',
    description: 'Used to open locked chests and doors.',
    type: 'misc',
    rarity: 'common',
    value: 25,
    stackable: true,
    maxStack: 10
  },
  
  'iron-shield': {
    id: 'iron-shield',
    name: 'Iron Shield',
    description: 'A sturdy shield that increases block chance.',
    type: 'accessory',
    rarity: 'common',
    value: 200,
    stackable: false,
    effects: [
      {
        type: 'stat',
        target: 'self',
        stat: 'blockChance',
        value: 15
      }
    ]
  },
  
  'lucky-charm': {
    id: 'lucky-charm',
    name: 'Lucky Charm',
    description: 'A small trinket that brings good fortune.',
    type: 'accessory',
    rarity: 'uncommon',
    value: 300,
    stackable: false,
    effects: [
      {
        type: 'stat',
        target: 'self',
        stat: 'luck',
        value: 3
      },
      {
        type: 'stat',
        target: 'self',
        stat: 'critChance',
        value: 5
      }
    ]
  },
  
  'ancient-key': {
    id: 'ancient-key',
    name: 'Ancient Key',
    description: 'An ornate key that looks very old. Wonder what it opens?',
    type: 'quest',
    rarity: 'rare',
    value: 0,
    stackable: false
  },
  
  'crystal-shard': {
    id: 'crystal-shard',
    name: 'Crystal Shard',
    description: 'A fragment of a larger crystal. It pulses with energy.',
    type: 'quest',
    rarity: 'rare',
    value: 500,
    stackable: true,
    maxStack: 5
  },
  
  'mysterious-letter': {
    id: 'mysterious-letter',
    name: 'Mysterious Letter',
    description: 'A sealed letter with no addressee. The wax seal bears an unfamiliar symbol.',
    type: 'quest',
    rarity: 'uncommon',
    value: 0,
    stackable: false
  }
};

// Combine all items
export const items: Record<string, Item> = {
  ...weapons,
  ...armor,
  ...consumables,
  ...miscItems
};