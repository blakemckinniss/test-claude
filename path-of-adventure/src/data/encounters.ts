import { RandomEncounter, EncounterTable } from '../types';

// Forest random encounters
export const forestEncounters: RandomEncounter[] = [
  {
    id: 'forest-wolf-pack',
    name: 'Wolf Pack',
    weight: 30,
    nodeId: 'encounter-wolf-pack',
    cooldown: 5
  },
  {
    id: 'forest-bandit-ambush',
    name: 'Bandit Ambush',
    weight: 20,
    nodeId: 'encounter-bandit-ambush',
    requirements: [
      {
        type: 'level',
        target: 'level',
        value: 3,
        comparison: 'gte'
      }
    ],
    cooldown: 10
  },
  {
    id: 'forest-merchant',
    name: 'Traveling Merchant',
    weight: 15,
    nodeId: 'encounter-merchant',
    cooldown: 20,
    maxTriggers: 3
  },
  {
    id: 'forest-fairy-blessing',
    name: 'Fairy Blessing',
    weight: 10,
    nodeId: 'encounter-fairy-blessing',
    requirements: [
      {
        type: 'reputation',
        target: 'mystic-grove',
        value: 0,
        comparison: 'gte'
      }
    ],
    maxTriggers: 1
  },
  {
    id: 'forest-lost-traveler',
    name: 'Lost Traveler',
    weight: 25,
    nodeId: 'encounter-lost-traveler',
    cooldown: 15
  }
];

// Mountain path random encounters
export const mountainEncounters: RandomEncounter[] = [
  {
    id: 'mountain-rockslide',
    name: 'Rockslide',
    weight: 25,
    nodeId: 'encounter-rockslide',
    cooldown: 10
  },
  {
    id: 'mountain-eagle-attack',
    name: 'Giant Eagle',
    weight: 20,
    nodeId: 'encounter-giant-eagle',
    requirements: [
      {
        type: 'level',
        target: 'level',
        value: 5,
        comparison: 'gte'
      }
    ],
    cooldown: 15
  },
  {
    id: 'mountain-hermit',
    name: 'Mountain Hermit',
    weight: 15,
    nodeId: 'encounter-hermit',
    maxTriggers: 2
  },
  {
    id: 'mountain-treasure-cache',
    name: 'Hidden Cache',
    weight: 10,
    nodeId: 'encounter-treasure-cache',
    requirements: [
      {
        type: 'stat',
        target: 'luck',
        value: 10,
        comparison: 'gte'
      }
    ],
    maxTriggers: 1
  }
];

// Dungeon random encounters
export const dungeonEncounters: RandomEncounter[] = [
  {
    id: 'dungeon-wandering-monster',
    name: 'Wandering Monster',
    weight: 40,
    nodeId: 'encounter-wandering-monster',
    cooldown: 3
  },
  {
    id: 'dungeon-trap',
    name: 'Hidden Trap',
    weight: 30,
    nodeId: 'encounter-hidden-trap',
    cooldown: 5
  },
  {
    id: 'dungeon-treasure-room',
    name: 'Secret Room',
    weight: 15,
    nodeId: 'encounter-secret-room',
    requirements: [
      {
        type: 'item',
        target: 'lockpick',
        value: 1,
        comparison: 'has'
      }
    ],
    cooldown: 20,
    maxTriggers: 2
  },
  {
    id: 'dungeon-lost-adventurer',
    name: 'Lost Adventurer',
    weight: 15,
    nodeId: 'encounter-lost-adventurer',
    cooldown: 15,
    maxTriggers: 3
  }
];

// Encounter tables
export const encounterTables: Record<string, EncounterTable> = {
  'forest-encounters': {
    id: 'forest-encounters',
    name: 'Forest Random Encounters',
    encounters: forestEncounters,
    triggerChance: 0.15
  },
  
  'mountain-encounters': {
    id: 'mountain-encounters',
    name: 'Mountain Random Encounters',
    encounters: mountainEncounters,
    triggerChance: 0.20
  },
  
  'dungeon-encounters': {
    id: 'dungeon-encounters',
    name: 'Dungeon Random Encounters',
    encounters: dungeonEncounters,
    triggerChance: 0.25
  },
  
  'road-encounters': {
    id: 'road-encounters',
    name: 'Road Random Encounters',
    encounters: [
      {
        id: 'road-merchant-caravan',
        name: 'Merchant Caravan',
        weight: 30,
        nodeId: 'encounter-merchant-caravan',
        cooldown: 10
      },
      {
        id: 'road-bandits',
        name: 'Highway Bandits',
        weight: 25,
        nodeId: 'encounter-highway-bandits',
        cooldown: 15
      },
      {
        id: 'road-pilgrims',
        name: 'Pilgrims',
        weight: 20,
        nodeId: 'encounter-pilgrims',
        cooldown: 20
      },
      {
        id: 'road-broken-wagon',
        name: 'Broken Wagon',
        weight: 25,
        nodeId: 'encounter-broken-wagon',
        cooldown: 10
      }
    ],
    triggerChance: 0.10
  }
};