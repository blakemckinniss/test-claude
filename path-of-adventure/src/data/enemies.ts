import { Enemy } from '../types';

export const enemies: Record<string, Enemy> = {
  // Tutorial enemies
  'tutorial-boar': {
    id: 'tutorial-boar',
    name: 'Wild Boar',
    description: 'A territorial boar with sharp tusks.',
    level: 1,
    health: 30,
    stats: {
      attack: 8,
      defense: 5,
      speed: 3,
      magicPower: 0,
      critChance: 5,
      dodgeChance: 10
    },
    attacks: [
      {
        name: 'Tusk Charge',
        damage: {
          min: 5,
          max: 10,
          type: 'physical'
        },
        accuracy: 90,
        priority: 1
      }
    ],
    lootTableId: 'tutorial-boar-loot',
    experienceReward: 15,
    goldReward: {
      min: 5,
      max: 15,
      type: 'physical' // Reusing damage range type
    },
    ai: 'aggressive'
  },
  
  // Forest enemies
  'forest-wolf': {
    id: 'forest-wolf',
    name: 'Gray Wolf',
    description: 'A hungry wolf with gleaming eyes.',
    level: 2,
    health: 40,
    stats: {
      attack: 12,
      defense: 6,
      speed: 8,
      magicPower: 0,
      critChance: 10,
      dodgeChance: 15
    },
    attacks: [
      {
        name: 'Bite',
        damage: {
          min: 8,
          max: 12,
          type: 'physical'
        },
        accuracy: 85,
        priority: 2
      },
      {
        name: 'Howl',
        damage: {
          min: 0,
          max: 0,
          type: 'physical'
        },
        accuracy: 100,
        effects: [
          {
            type: 'buff',
            target: 'self',
            stat: 'attack',
            value: 3,
            duration: 3
          }
        ],
        cooldown: 3,
        priority: 1
      }
    ],
    lootTableId: 'forest-wolf-loot',
    experienceReward: 25,
    goldReward: {
      min: 10,
      max: 20,
      type: 'physical'
    },
    ai: 'balanced'
  },
  
  'bandit-scout': {
    id: 'bandit-scout',
    name: 'Bandit Scout',
    description: 'A nimble bandit armed with dual daggers.',
    level: 3,
    health: 45,
    stats: {
      attack: 10,
      defense: 8,
      speed: 10,
      magicPower: 0,
      critChance: 20,
      dodgeChance: 25
    },
    attacks: [
      {
        name: 'Quick Strike',
        damage: {
          min: 6,
          max: 10,
          type: 'physical'
        },
        accuracy: 95,
        priority: 3
      },
      {
        name: 'Backstab',
        damage: {
          min: 12,
          max: 18,
          type: 'physical'
        },
        accuracy: 75,
        priority: 1,
        condition: {
          type: 'health_below',
          value: 50
        }
      }
    ],
    lootTableId: 'bandit-scout-loot',
    experienceReward: 35,
    goldReward: {
      min: 20,
      max: 40,
      type: 'physical'
    },
    weaknesses: ['magical'],
    ai: 'aggressive'
  },
  
  'forest-spider': {
    id: 'forest-spider',
    name: 'Giant Spider',
    description: 'A massive spider with venomous fangs.',
    level: 4,
    health: 55,
    stats: {
      attack: 14,
      defense: 10,
      speed: 6,
      magicPower: 0,
      critChance: 15,
      dodgeChance: 20
    },
    attacks: [
      {
        name: 'Venomous Bite',
        damage: {
          min: 10,
          max: 15,
          type: 'physical'
        },
        accuracy: 80,
        effects: [
          {
            type: 'debuff',
            target: 'enemy',
            stat: 'health',
            value: -3,
            duration: 5,
            chance: 0.5
          }
        ],
        priority: 2
      },
      {
        name: 'Web Shot',
        damage: {
          min: 0,
          max: 0,
          type: 'physical'
        },
        accuracy: 70,
        effects: [
          {
            type: 'debuff',
            target: 'enemy',
            stat: 'speed',
            value: -5,
            duration: 3
          }
        ],
        cooldown: 2,
        priority: 1
      }
    ],
    lootTableId: 'forest-spider-loot',
    experienceReward: 45,
    goldReward: {
      min: 15,
      max: 30,
      type: 'physical'
    },
    weaknesses: ['fire'],
    resistances: ['poison'],
    ai: 'balanced'
  },
  
  // Mine enemies
  'cave-bat': {
    id: 'cave-bat',
    name: 'Cave Bat',
    description: 'A screeching bat that attacks in swarms.',
    level: 2,
    health: 25,
    stats: {
      attack: 8,
      defense: 4,
      speed: 12,
      magicPower: 0,
      critChance: 5,
      dodgeChance: 30
    },
    attacks: [
      {
        name: 'Sonic Screech',
        damage: {
          min: 4,
          max: 8,
          type: 'magical'
        },
        accuracy: 85,
        priority: 1
      }
    ],
    lootTableId: 'cave-bat-loot',
    experienceReward: 20,
    goldReward: {
      min: 5,
      max: 10,
      type: 'physical'
    },
    ai: 'aggressive'
  },
  
  'goblin-miner': {
    id: 'goblin-miner',
    name: 'Goblin Miner',
    description: 'A greedy goblin with a pickaxe.',
    level: 3,
    health: 50,
    stats: {
      attack: 12,
      defense: 10,
      speed: 5,
      magicPower: 0,
      critChance: 10,
      dodgeChance: 15
    },
    attacks: [
      {
        name: 'Pickaxe Swing',
        damage: {
          min: 8,
          max: 14,
          type: 'physical'
        },
        accuracy: 80,
        priority: 2
      },
      {
        name: 'Rock Throw',
        damage: {
          min: 6,
          max: 10,
          type: 'physical'
        },
        accuracy: 70,
        priority: 1,
        condition: {
          type: 'turn_number',
          value: 3
        }
      }
    ],
    lootTableId: 'goblin-miner-loot',
    experienceReward: 30,
    goldReward: {
      min: 25,
      max: 50,
      type: 'physical'
    },
    ai: 'defensive'
  },
  
  'stone-golem': {
    id: 'stone-golem',
    name: 'Stone Golem',
    description: 'An ancient guardian made of living rock.',
    level: 5,
    health: 100,
    stats: {
      attack: 18,
      defense: 20,
      speed: 2,
      magicPower: 0,
      critChance: 5,
      dodgeChance: 0
    },
    attacks: [
      {
        name: 'Stone Fist',
        damage: {
          min: 15,
          max: 25,
          type: 'physical'
        },
        accuracy: 70,
        priority: 2
      },
      {
        name: 'Earthquake',
        damage: {
          min: 10,
          max: 15,
          type: 'physical'
        },
        accuracy: 90,
        effects: [
          {
            type: 'debuff',
            target: 'enemy',
            stat: 'dodgeChance',
            value: -10,
            duration: 2
          }
        ],
        cooldown: 3,
        priority: 1
      }
    ],
    lootTableId: 'stone-golem-loot',
    experienceReward: 75,
    goldReward: {
      min: 50,
      max: 100,
      type: 'physical'
    },
    resistances: ['physical'],
    weaknesses: ['magical'],
    ai: 'defensive'
  },
  
  // Mystic Grove enemies
  'corrupted-fairy': {
    id: 'corrupted-fairy',
    name: 'Corrupted Fairy',
    description: 'A fairy twisted by dark magic.',
    level: 4,
    health: 40,
    stats: {
      attack: 8,
      defense: 6,
      speed: 15,
      magicPower: 20,
      critChance: 15,
      dodgeChance: 35
    },
    attacks: [
      {
        name: 'Dark Bolt',
        damage: {
          min: 10,
          max: 16,
          type: 'magical'
        },
        accuracy: 90,
        priority: 2
      },
      {
        name: 'Curse',
        damage: {
          min: 0,
          max: 0,
          type: 'magical'
        },
        accuracy: 80,
        effects: [
          {
            type: 'debuff',
            target: 'enemy',
            stat: 'attack',
            value: -5,
            duration: 4
          },
          {
            type: 'debuff',
            target: 'enemy',
            stat: 'defense',
            value: -5,
            duration: 4
          }
        ],
        cooldown: 4,
        priority: 1
      }
    ],
    lootTableId: 'corrupted-fairy-loot',
    experienceReward: 50,
    goldReward: {
      min: 20,
      max: 35,
      type: 'physical'
    },
    resistances: ['magical'],
    weaknesses: ['physical'],
    ai: 'balanced'
  },
  
  'treant': {
    id: 'treant',
    name: 'Ancient Treant',
    description: 'A walking tree animated by forest magic.',
    level: 6,
    health: 120,
    stats: {
      attack: 20,
      defense: 25,
      speed: 3,
      magicPower: 15,
      critChance: 10,
      dodgeChance: 5
    },
    attacks: [
      {
        name: 'Branch Slam',
        damage: {
          min: 18,
          max: 28,
          type: 'physical'
        },
        accuracy: 75,
        priority: 2
      },
      {
        name: 'Regeneration',
        damage: {
          min: 0,
          max: 0,
          type: 'magical'
        },
        accuracy: 100,
        effects: [
          {
            type: 'heal',
            target: 'self',
            value: 15
          }
        ],
        cooldown: 4,
        priority: 1,
        condition: {
          type: 'health_below',
          value: 50
        }
      },
      {
        name: 'Root Entangle',
        damage: {
          min: 5,
          max: 10,
          type: 'physical'
        },
        accuracy: 80,
        effects: [
          {
            type: 'debuff',
            target: 'enemy',
            stat: 'speed',
            value: -10,
            duration: 3
          }
        ],
        cooldown: 3,
        priority: 1
      }
    ],
    lootTableId: 'treant-loot',
    experienceReward: 100,
    goldReward: {
      min: 75,
      max: 150,
      type: 'physical'
    },
    resistances: ['physical'],
    weaknesses: ['fire'],
    ai: 'defensive'
  },
  
  // Boss enemies
  'bandit-leader': {
    id: 'bandit-leader',
    name: 'Bandit Leader Grimjaw',
    description: 'The ruthless leader of the forest bandits.',
    level: 8,
    health: 200,
    stats: {
      attack: 25,
      defense: 20,
      speed: 12,
      magicPower: 0,
      critChance: 25,
      dodgeChance: 20
    },
    attacks: [
      {
        name: 'Brutal Strike',
        damage: {
          min: 20,
          max: 35,
          type: 'physical'
        },
        accuracy: 85,
        priority: 3
      },
      {
        name: 'Rally Cry',
        damage: {
          min: 0,
          max: 0,
          type: 'physical'
        },
        accuracy: 100,
        effects: [
          {
            type: 'buff',
            target: 'self',
            stat: 'attack',
            value: 10,
            duration: 5
          },
          {
            type: 'buff',
            target: 'self',
            stat: 'defense',
            value: 10,
            duration: 5
          }
        ],
        cooldown: 5,
        priority: 1,
        condition: {
          type: 'health_below',
          value: 50
        }
      },
      {
        name: 'Dirty Trick',
        damage: {
          min: 10,
          max: 15,
          type: 'physical'
        },
        accuracy: 90,
        effects: [
          {
            type: 'debuff',
            target: 'enemy',
            stat: 'dodgeChance',
            value: -20,
            duration: 3
          }
        ],
        cooldown: 3,
        priority: 2
      }
    ],
    lootTableId: 'bandit-leader-loot',
    experienceReward: 250,
    goldReward: {
      min: 200,
      max: 300,
      type: 'physical'
    },
    ai: 'aggressive'
  }
};