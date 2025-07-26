import { NPC } from '../types';

export const npcs: Record<string, NPC> = {
  'elder-aldric': {
    id: 'elder-aldric',
    name: 'Elder Aldric',
    title: 'Village Elder',
    description: 'A wise old man with a long white beard and knowing eyes. He has lived in Thornwick for over seventy years and knows every secret the village holds.',
    dialogueTreeId: 'elder-aldric-dialogue',
    questGiver: true,
    faction: 'thornwick-village'
  },
  
  'martha-innkeeper': {
    id: 'martha-innkeeper',
    name: 'Martha',
    title: 'Innkeeper',
    description: 'A plump, cheerful woman who runs the Wanderer\'s Rest Inn. Her warm smile and hearty meals have comforted many travelers.',
    dialogueTreeId: 'martha-dialogue',
    questGiver: false,
    faction: 'thornwick-village'
  },
  
  'gareth-blacksmith': {
    id: 'gareth-blacksmith',
    name: 'Gareth',
    title: 'Blacksmith',
    description: 'A burly man with arms like tree trunks, his face often covered in soot. Despite his intimidating appearance, he has a gentle heart.',
    dialogueTreeId: 'gareth-dialogue',
    shopInventory: ['steel-sword', 'steel-dagger', 'chainmail', 'iron-shield', 'plate-armor'],
    questGiver: false,
    faction: 'thornwick-village'
  },
  
  'old-tom-shopkeeper': {
    id: 'old-tom-shopkeeper',
    name: 'Old Tom',
    title: 'General Store Owner',
    description: 'An elderly man with spectacles perched on his nose. He knows the price of everything and the value of nothing, as they say.',
    dialogueTreeId: 'old-tom-dialogue',
    shopInventory: ['healing-potion-small', 'mana-potion-small', 'torch', 'rope', 'lockpick', 'antidote'],
    questGiver: false,
    faction: 'thornwick-village'
  },
  
  'mysterious-stranger': {
    id: 'mysterious-stranger',
    name: '???',
    title: 'Hooded Stranger',
    description: 'A figure shrouded in a dark cloak. You can\'t make out any features beneath the hood, but you feel their gaze upon you.',
    dialogueTreeId: 'mysterious-stranger-dialogue',
    questGiver: true,
    faction: 'unknown'
  },
  
  'captain-helena': {
    id: 'captain-helena',
    name: 'Captain Helena',
    title: 'Guard Captain',
    description: 'A stern woman in her thirties, wearing the insignia of the village guard. Her sharp eyes miss nothing.',
    dialogueTreeId: 'captain-helena-dialogue',
    questGiver: true,
    faction: 'thornwick-guard'
  },
  
  'sage-elara': {
    id: 'sage-elara',
    name: 'Sage Elara',
    title: 'Grove Keeper',
    description: 'An ethereal woman who seems to be one with the forest. Flowers bloom where she walks, and birds sing at her approach.',
    dialogueTreeId: 'sage-elara-dialogue',
    questGiver: true,
    faction: 'mystic-grove'
  },
  
  'prospector-finn': {
    id: 'prospector-finn',
    name: 'Finn',
    title: 'Old Prospector',
    description: 'A grizzled miner who survived the mine collapse years ago. He knows the tunnels better than anyone, but rarely speaks of what he\'s seen.',
    dialogueTreeId: 'prospector-finn-dialogue',
    questGiver: true,
    faction: 'independent'
  },
  
  'merchant-hassan': {
    id: 'merchant-hassan',
    name: 'Hassan',
    title: 'Traveling Merchant',
    description: 'A jovial merchant from distant lands, his wagon filled with exotic goods. He always has interesting stories to share.',
    dialogueTreeId: 'merchant-hassan-dialogue',
    shopInventory: ['enchanted-sword', 'mage-robes', 'lucky-charm', 'healing-potion-large', 'crystal-shard'],
    questGiver: false,
    faction: 'merchant-guild'
  },
  
  'scholar-magnus': {
    id: 'scholar-magnus',
    name: 'Magnus',
    title: 'Lore Keeper',
    description: 'A thin man surrounded by dusty tomes and ancient scrolls. He speaks in riddles and quotes from texts no one else has read.',
    dialogueTreeId: 'scholar-magnus-dialogue',
    questGiver: true,
    faction: 'scholars-circle'
  }
};