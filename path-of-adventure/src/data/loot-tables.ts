import { LootTable } from '../types';

export const lootTables: Record<string, LootTable> = {
  // Tutorial loot tables
  'tutorial-combat-reward': {
    id: 'tutorial-combat-reward',
    name: 'Tutorial Combat Reward',
    guaranteed: [
      {
        itemId: 'healing-potion-small',
        quantity: { min: 1, max: 2, type: 'physical' }
      }
    ],
    randomPools: [
      {
        name: 'bonus',
        rolls: 1,
        entries: [
          {
            itemId: 'rusty-dagger',
            quantity: { min: 1, max: 1, type: 'physical' },
            chance: 0.3
          },
          {
            itemId: 'torch',
            quantity: { min: 2, max: 3, type: 'physical' },
            chance: 0.5
          },
          {
            itemId: 'rope',
            quantity: { min: 1, max: 1, type: 'physical' },
            chance: 0.2
          }
        ]
      }
    ]
  },
  
  'tutorial-treasure-chest': {
    id: 'tutorial-treasure-chest',
    name: 'Tutorial Treasure Chest',
    guaranteed: [
      {
        itemId: 'gold',
        quantity: { min: 25, max: 50, type: 'physical' }
      },
      {
        itemId: 'torch',
        quantity: { min: 3, max: 5, type: 'physical' }
      }
    ],
    randomPools: [
      {
        name: 'equipment',
        rolls: 1,
        entries: [
          {
            itemId: 'steel-dagger',
            quantity: { min: 1, max: 1, type: 'physical' },
            chance: 0.4
          },
          {
            itemId: 'iron-shield',
            quantity: { min: 1, max: 1, type: 'physical' },
            chance: 0.3
          },
          {
            itemId: 'lucky-charm',
            quantity: { min: 1, max: 1, type: 'physical' },
            chance: 0.3
          }
        ]
      }
    ]
  },
  
  // Enemy loot tables
  'tutorial-boar-loot': {
    id: 'tutorial-boar-loot',
    name: 'Wild Boar Loot',
    guaranteed: [],
    randomPools: [
      {
        name: 'common',
        rolls: 1,
        entries: [
          {
            itemId: 'healing-potion-small',
            quantity: { min: 1, max: 1, type: 'physical' },
            chance: 0.5
          },
          {
            itemId: 'antidote',
            quantity: { min: 1, max: 1, type: 'physical' },
            chance: 0.2
          }
        ]
      }
    ]
  },
  
  'forest-wolf-loot': {
    id: 'forest-wolf-loot',
    name: 'Gray Wolf Loot',
    guaranteed: [],
    randomPools: [
      {
        name: 'common',
        rolls: 1,
        entries: [
          {
            itemId: 'healing-potion-small',
            quantity: { min: 1, max: 1, type: 'physical' },
            chance: 0.6
          },
          {
            itemId: 'speed-potion',
            quantity: { min: 1, max: 1, type: 'physical' },
            chance: 0.2
          }
        ]
      }
    ]
  },
  
  'bandit-scout-loot': {
    id: 'bandit-scout-loot',
    name: 'Bandit Scout Loot',
    guaranteed: [],
    randomPools: [
      {
        name: 'consumables',
        rolls: 1,
        entries: [
          {
            itemId: 'healing-potion-small',
            quantity: { min: 1, max: 2, type: 'physical' },
            chance: 0.7
          },
          {
            itemId: 'smoke-bomb',
            quantity: { min: 1, max: 2, type: 'physical' },
            chance: 0.3
          },
          {
            itemId: 'lockpick',
            quantity: { min: 1, max: 3, type: 'physical' },
            chance: 0.4
          }
        ]
      },
      {
        name: 'equipment',
        rolls: 1,
        entries: [
          {
            itemId: 'steel-dagger',
            quantity: { min: 1, max: 1, type: 'physical' },
            chance: 0.15
          },
          {
            itemId: 'leather-armor',
            quantity: { min: 1, max: 1, type: 'physical' },
            chance: 0.1
          }
        ]
      }
    ]
  },
  
  'forest-spider-loot': {
    id: 'forest-spider-loot',
    name: 'Giant Spider Loot',
    guaranteed: [],
    randomPools: [
      {
        name: 'common',
        rolls: 1,
        entries: [
          {
            itemId: 'antidote',
            quantity: { min: 1, max: 2, type: 'physical' },
            chance: 0.8
          },
          {
            itemId: 'rope',
            quantity: { min: 2, max: 4, type: 'physical' },
            chance: 0.6
          },
          {
            itemId: 'healing-potion-medium',
            quantity: { min: 1, max: 1, type: 'physical' },
            chance: 0.3
          }
        ]
      }
    ]
  },
  
  'cave-bat-loot': {
    id: 'cave-bat-loot',
    name: 'Cave Bat Loot',
    guaranteed: [],
    randomPools: [
      {
        name: 'common',
        rolls: 1,
        entries: [
          {
            itemId: 'healing-potion-small',
            quantity: { min: 1, max: 1, type: 'physical' },
            chance: 0.3
          }
        ]
      }
    ]
  },
  
  'goblin-miner-loot': {
    id: 'goblin-miner-loot',
    name: 'Goblin Miner Loot',
    guaranteed: [
      {
        itemId: 'torch',
        quantity: { min: 1, max: 3, type: 'physical' }
      }
    ],
    randomPools: [
      {
        name: 'consumables',
        rolls: 1,
        entries: [
          {
            itemId: 'healing-potion-small',
            quantity: { min: 1, max: 2, type: 'physical' },
            chance: 0.6
          },
          {
            itemId: 'fire-bomb',
            quantity: { min: 1, max: 1, type: 'physical' },
            chance: 0.3
          }
        ]
      },
      {
        name: 'materials',
        rolls: 1,
        entries: [
          {
            itemId: 'crystal-shard',
            quantity: { min: 1, max: 1, type: 'physical' },
            chance: 0.1
          }
        ]
      }
    ]
  },
  
  'stone-golem-loot': {
    id: 'stone-golem-loot',
    name: 'Stone Golem Loot',
    guaranteed: [
      {
        itemId: 'crystal-shard',
        quantity: { min: 1, max: 2, type: 'physical' }
      }
    ],
    randomPools: [
      {
        name: 'rare',
        rolls: 1,
        entries: [
          {
            itemId: 'plate-armor',
            quantity: { min: 1, max: 1, type: 'physical' },
            chance: 0.15
          },
          {
            itemId: 'iron-shield',
            quantity: { min: 1, max: 1, type: 'physical' },
            chance: 0.3
          },
          {
            itemId: 'strength-potion',
            quantity: { min: 2, max: 3, type: 'physical' },
            chance: 0.5
          }
        ]
      }
    ]
  },
  
  'corrupted-fairy-loot': {
    id: 'corrupted-fairy-loot',
    name: 'Corrupted Fairy Loot',
    guaranteed: [],
    randomPools: [
      {
        name: 'magical',
        rolls: 1,
        entries: [
          {
            itemId: 'mana-potion-small',
            quantity: { min: 1, max: 2, type: 'physical' },
            chance: 0.7
          },
          {
            itemId: 'wooden-staff',
            quantity: { min: 1, max: 1, type: 'physical' },
            chance: 0.1
          },
          {
            itemId: 'mage-robes',
            quantity: { min: 1, max: 1, type: 'physical' },
            chance: 0.05
          }
        ]
      }
    ]
  },
  
  'treant-loot': {
    id: 'treant-loot',
    name: 'Ancient Treant Loot',
    guaranteed: [
      {
        itemId: 'healing-potion-large',
        quantity: { min: 1, max: 1, type: 'physical' }
      }
    ],
    randomPools: [
      {
        name: 'rare',
        rolls: 2,
        entries: [
          {
            itemId: 'enchanted-sword',
            quantity: { min: 1, max: 1, type: 'physical' },
            chance: 0.1
          },
          {
            itemId: 'ancient-key',
            quantity: { min: 1, max: 1, type: 'physical' },
            chance: 0.15
          },
          {
            itemId: 'crystal-shard',
            quantity: { min: 2, max: 3, type: 'physical' },
            chance: 0.4
          },
          {
            itemId: 'healing-potion-large',
            quantity: { min: 1, max: 2, type: 'physical' },
            chance: 0.3
          }
        ]
      }
    ]
  },
  
  'bandit-leader-loot': {
    id: 'bandit-leader-loot',
    name: 'Bandit Leader Loot',
    guaranteed: [
      {
        itemId: 'mysterious-letter',
        quantity: { min: 1, max: 1, type: 'physical' }
      }
    ],
    randomPools: [
      {
        name: 'boss-equipment',
        rolls: 2,
        entries: [
          {
            itemId: 'enchanted-sword',
            quantity: { min: 1, max: 1, type: 'physical' },
            chance: 0.3
          },
          {
            itemId: 'chainmail',
            quantity: { min: 1, max: 1, type: 'physical' },
            chance: 0.4
          },
          {
            itemId: 'lucky-charm',
            quantity: { min: 1, max: 1, type: 'physical' },
            chance: 0.5
          }
        ]
      },
      {
        name: 'boss-consumables',
        rolls: 3,
        entries: [
          {
            itemId: 'healing-potion-large',
            quantity: { min: 1, max: 2, type: 'physical' },
            chance: 0.6
          },
          {
            itemId: 'strength-potion',
            quantity: { min: 1, max: 2, type: 'physical' },
            chance: 0.4
          },
          {
            itemId: 'smoke-bomb',
            quantity: { min: 2, max: 4, type: 'physical' },
            chance: 0.5
          }
        ]
      }
    ]
  },
  
  // Chest and special loot tables
  'common-chest': {
    id: 'common-chest',
    name: 'Common Chest',
    guaranteed: [
      {
        itemId: 'gold',
        quantity: { min: 20, max: 50, type: 'physical' }
      }
    ],
    randomPools: [
      {
        name: 'common-items',
        rolls: 2,
        entries: [
          {
            itemId: 'healing-potion-small',
            quantity: { min: 1, max: 3, type: 'physical' },
            chance: 0.6
          },
          {
            itemId: 'torch',
            quantity: { min: 2, max: 5, type: 'physical' },
            chance: 0.5
          },
          {
            itemId: 'rope',
            quantity: { min: 1, max: 2, type: 'physical' },
            chance: 0.4
          },
          {
            itemId: 'lockpick',
            quantity: { min: 1, max: 3, type: 'physical' },
            chance: 0.3
          }
        ]
      }
    ]
  },
  
  'rare-chest': {
    id: 'rare-chest',
    name: 'Rare Chest',
    guaranteed: [
      {
        itemId: 'gold',
        quantity: { min: 100, max: 200, type: 'physical' }
      }
    ],
    randomPools: [
      {
        name: 'rare-equipment',
        rolls: 1,
        entries: [
          {
            itemId: 'steel-sword',
            quantity: { min: 1, max: 1, type: 'physical' },
            chance: 0.3
          },
          {
            itemId: 'chainmail',
            quantity: { min: 1, max: 1, type: 'physical' },
            chance: 0.3
          },
          {
            itemId: 'hunters-bow',
            quantity: { min: 1, max: 1, type: 'physical' },
            chance: 0.2
          },
          {
            itemId: 'lucky-charm',
            quantity: { min: 1, max: 1, type: 'physical' },
            chance: 0.2
          }
        ]
      },
      {
        name: 'rare-consumables',
        rolls: 2,
        entries: [
          {
            itemId: 'healing-potion-medium',
            quantity: { min: 2, max: 3, type: 'physical' },
            chance: 0.6
          },
          {
            itemId: 'strength-potion',
            quantity: { min: 1, max: 2, type: 'physical' },
            chance: 0.4
          },
          {
            itemId: 'speed-potion',
            quantity: { min: 1, max: 2, type: 'physical' },
            chance: 0.4
          },
          {
            itemId: 'fire-bomb',
            quantity: { min: 1, max: 3, type: 'physical' },
            chance: 0.3
          }
        ]
      }
    ]
  }
};