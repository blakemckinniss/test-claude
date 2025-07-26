// Central export for all game data

export * from './story-nodes';
export * from './items';
export * from './enemies';
export * from './npcs';
export * from './loot-tables';
export * from './dungeons';
export * from './encounters';
export * from './game-constants';

// Re-export specific collections for convenience
export { storyNodes, tutorialNodes, mainStoryNodes } from './story-nodes';
export { items, weapons, armor, consumables, miscItems } from './items';
export { enemies } from './enemies';
export { npcs } from './npcs';
export { lootTables } from './loot-tables';
export { dungeons, oldMineDungeon, mysticGroveDungeon } from './dungeons';
export { encounterTables, forestEncounters, mountainEncounters, dungeonEncounters } from './encounters';
export { 
  GAME_CONSTANTS, 
  SKILL_CHECK_DIFFICULTY,
  getExperienceForLevel,
  calculateDerivedStats,
  calculateMaxHealthMana
} from './game-constants';