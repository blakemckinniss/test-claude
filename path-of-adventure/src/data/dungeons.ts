import { Dungeon, DungeonFloor, DungeonRoom } from '../types';

// The Old Mine dungeon
const oldMineFloor1Rooms: Record<string, DungeonRoom> = {
  'mine-1-entrance': {
    id: 'mine-1-entrance',
    roomType: 'entrance',
    description: 'The mine entrance is dark and foreboding. Old mining equipment lies scattered about.',
    connections: [
      { toRoomId: 'mine-1-tunnel-1', direction: 'north' },
      { toRoomId: 'mine-1-storage', direction: 'east' }
    ],
    visited: false
  },
  
  'mine-1-tunnel-1': {
    id: 'mine-1-tunnel-1',
    roomType: 'combat',
    description: 'A narrow tunnel with low ceilings. You hear chittering sounds echoing off the walls.',
    connections: [
      { toRoomId: 'mine-1-entrance', direction: 'south' },
      { toRoomId: 'mine-1-chamber', direction: 'north' },
      { toRoomId: 'mine-1-tunnel-2', direction: 'west' }
    ],
    content: {
      enemies: ['cave-bat', 'cave-bat']
    },
    visited: false
  },
  
  'mine-1-storage': {
    id: 'mine-1-storage',
    roomType: 'treasure',
    description: 'An old storage room filled with mining supplies. A chest sits in the corner.',
    connections: [
      { toRoomId: 'mine-1-entrance', direction: 'west' }
    ],
    content: {
      lootTableId: 'common-chest'
    },
    visited: false
  },
  
  'mine-1-tunnel-2': {
    id: 'mine-1-tunnel-2',
    roomType: 'trap',
    description: 'This tunnel looks unstable. Loose rocks hang precariously from the ceiling.',
    connections: [
      { toRoomId: 'mine-1-tunnel-1', direction: 'east' },
      { toRoomId: 'mine-1-goblin-camp', direction: 'west' }
    ],
    content: {
      trapType: 'spike'
    },
    visited: false
  },
  
  'mine-1-chamber': {
    id: 'mine-1-chamber',
    roomType: 'combat',
    description: 'A larger chamber where miners once took their breaks. Now it\'s home to dangerous creatures.',
    connections: [
      { toRoomId: 'mine-1-tunnel-1', direction: 'south' },
      { toRoomId: 'mine-1-deep-tunnel', direction: 'north' }
    ],
    content: {
      enemies: ['goblin-miner', 'cave-bat']
    },
    visited: false
  },
  
  'mine-1-goblin-camp': {
    id: 'mine-1-goblin-camp',
    roomType: 'combat',
    description: 'A makeshift goblin camp. Crude bedrolls and cooking fires are scattered about.',
    connections: [
      { toRoomId: 'mine-1-tunnel-2', direction: 'east' },
      { toRoomId: 'mine-1-treasure-room', direction: 'north', locked: true, keyItemId: 'rusty-mine-key' }
    ],
    content: {
      enemies: ['goblin-miner', 'goblin-miner']
    },
    visited: false
  },
  
  'mine-1-treasure-room': {
    id: 'mine-1-treasure-room',
    roomType: 'treasure',
    description: 'The goblins\' treasure hoard! Stolen goods and shiny objects fill the room.',
    connections: [
      { toRoomId: 'mine-1-goblin-camp', direction: 'south' }
    ],
    content: {
      lootTableId: 'rare-chest'
    },
    visited: false
  },
  
  'mine-1-deep-tunnel': {
    id: 'mine-1-deep-tunnel',
    roomType: 'rest',
    description: 'A quiet alcove with an underground spring. The water looks clean and refreshing.',
    connections: [
      { toRoomId: 'mine-1-chamber', direction: 'south' },
      { toRoomId: 'mine-1-boss-room', direction: 'east' }
    ],
    content: {
      healingAmount: 50
    },
    visited: false
  },
  
  'mine-1-boss-room': {
    id: 'mine-1-boss-room',
    roomType: 'boss',
    description: 'A massive cavern. In the center stands an ancient guardian, awakened by your presence.',
    connections: [
      { toRoomId: 'mine-1-deep-tunnel', direction: 'west' }
    ],
    content: {
      enemies: ['stone-golem']
    },
    visited: false
  }
};

const oldMineFloor1: DungeonFloor = {
  id: 'old-mine-floor-1',
  name: 'Upper Mines',
  rooms: Object.values(oldMineFloor1Rooms),
  startRoomId: 'mine-1-entrance',
  bossRoomId: 'mine-1-boss-room',
  treasureRoomIds: ['mine-1-storage', 'mine-1-treasure-room']
};

export const oldMineDungeon: Dungeon = {
  id: 'old-mine',
  name: 'The Old Mine',
  description: 'An abandoned mine that was sealed years ago after a terrible accident. Recently, strange noises have been heard from within.',
  floors: [oldMineFloor1],
  theme: 'cave',
  unlockRequirements: [
    {
      type: 'item',
      target: 'torch',
      value: 1,
      comparison: 'has'
    }
  ]
};

// The Mystic Grove dungeon
const mysticGroveRooms: Record<string, DungeonRoom> = {
  'grove-entrance': {
    id: 'grove-entrance',
    roomType: 'entrance',
    description: 'The grove entrance glows with ethereal light. Ancient trees form a natural archway.',
    connections: [
      { toRoomId: 'grove-fairy-circle', direction: 'north' },
      { toRoomId: 'grove-meditation-pool', direction: 'east' }
    ],
    visited: false
  },
  
  'grove-fairy-circle': {
    id: 'grove-fairy-circle',
    roomType: 'combat',
    description: 'A circle of mushrooms marks this as a fairy gathering place. But something is wrong here.',
    connections: [
      { toRoomId: 'grove-entrance', direction: 'south' },
      { toRoomId: 'grove-twisted-path', direction: 'north' },
      { toRoomId: 'grove-ancient-tree', direction: 'west' }
    ],
    content: {
      enemies: ['corrupted-fairy', 'corrupted-fairy']
    },
    visited: false
  },
  
  'grove-meditation-pool': {
    id: 'grove-meditation-pool',
    roomType: 'rest',
    description: 'A serene pool reflects the canopy above. The water has healing properties.',
    connections: [
      { toRoomId: 'grove-entrance', direction: 'west' }
    ],
    content: {
      healingAmount: 75
    },
    visited: false
  },
  
  'grove-ancient-tree': {
    id: 'grove-ancient-tree',
    roomType: 'puzzle',
    description: 'An enormous tree with a door carved into its trunk. Ancient runes glow faintly.',
    connections: [
      { toRoomId: 'grove-fairy-circle', direction: 'east' },
      { toRoomId: 'grove-tree-hollow', direction: 'north', locked: true }
    ],
    content: {
      puzzleId: 'rune-sequence'
    },
    visited: false
  },
  
  'grove-tree-hollow': {
    id: 'grove-tree-hollow',
    roomType: 'treasure',
    description: 'Inside the ancient tree, treasures of the forest are stored.',
    connections: [
      { toRoomId: 'grove-ancient-tree', direction: 'south' }
    ],
    content: {
      lootTableId: 'rare-chest'
    },
    visited: false
  },
  
  'grove-twisted-path': {
    id: 'grove-twisted-path',
    roomType: 'trap',
    description: 'The path here seems to shift and change. Thorny vines reach out to ensnare the unwary.',
    connections: [
      { toRoomId: 'grove-fairy-circle', direction: 'south' },
      { toRoomId: 'grove-corrupted-heart', direction: 'north' }
    ],
    content: {
      trapType: 'poison'
    },
    visited: false
  },
  
  'grove-corrupted-heart': {
    id: 'grove-corrupted-heart',
    roomType: 'boss',
    description: 'The heart of the grove, now twisted by dark magic. A massive treant stands guard.',
    connections: [
      { toRoomId: 'grove-twisted-path', direction: 'south' }
    ],
    content: {
      enemies: ['treant']
    },
    visited: false
  }
};

const mysticGroveFloor: DungeonFloor = {
  id: 'mystic-grove-floor',
  name: 'The Sacred Grove',
  rooms: Object.values(mysticGroveRooms),
  startRoomId: 'grove-entrance',
  bossRoomId: 'grove-corrupted-heart',
  treasureRoomIds: ['grove-tree-hollow']
};

export const mysticGroveDungeon: Dungeon = {
  id: 'mystic-grove-dungeon',
  name: 'Corrupted Mystic Grove',
  description: 'Once a place of natural beauty and magic, the grove has been corrupted by an unknown force.',
  floors: [mysticGroveFloor],
  theme: 'forest'
};

// Export all dungeons
export const dungeons: Record<string, Dungeon> = {
  'old-mine': oldMineDungeon,
  'mystic-grove': mysticGroveDungeon
};