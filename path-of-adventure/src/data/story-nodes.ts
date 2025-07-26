import { StoryNode } from '../types/game.types';

export const STORY_NODES: Record<string, StoryNode> = {
  'character-creation': {
    id: 'character-creation',
    type: 'event',
    text: 'Welcome to the Path of Adventure! Create your character to begin.',
    choices: []
  },

  'tutorial-start': {
    id: 'tutorial-start',
    type: 'narration',
    text: `You awaken in a small forest clearing. Sunlight filters through the canopy above, and you can hear the distant sound of running water. Your adventure begins here.

As you stand up and dust yourself off, you notice a worn leather pack beside you containing a few basic supplies. To your right, a narrow path winds deeper into the forest. To your left, you can make out what appears to be a small village in the distance.`,
    choices: [
      {
        text: 'Follow the path into the forest',
        nextNodeId: 'forest-path',
        consequences: { stepCount: 1 }
      },
      {
        text: 'Head toward the village',
        nextNodeId: 'village-approach',
        consequences: { stepCount: 1 }
      },
      {
        text: 'Examine the leather pack',
        nextNodeId: 'examine-pack',
        consequences: {}
      }
    ]
  },

  'examine-pack': {
    id: 'examine-pack',
    type: 'event',
    text: `You open the leather pack and find:
- A small loaf of bread (restores 5 health)
- A rusty dagger
- 10 gold pieces
- A hand-drawn map of the local area

The items have been added to your inventory.`,
    choices: [
      {
        text: 'Continue to the forest path',
        nextNodeId: 'forest-path',
        consequences: { 
          stepCount: 1,
          items: ['bread', 'rusty-dagger'],
          gold: 10
        }
      },
      {
        text: 'Head to the village',
        nextNodeId: 'village-approach',
        consequences: { 
          stepCount: 1,
          items: ['bread', 'rusty-dagger'],
          gold: 10
        }
      }
    ]
  },

  'forest-path': {
    id: 'forest-path',
    type: 'narration',
    text: `The forest path is well-worn but overgrown in places. Ancient trees tower overhead, their branches forming a natural canopy that filters the sunlight into dancing patterns on the ground.

After walking for several minutes, you hear rustling in the bushes ahead. A wild boar emerges, snorting aggressively and blocking your path. Its tusks gleam menacingly as it paws the ground.`,
    choices: [
      {
        text: 'Fight the wild boar',
        nextNodeId: 'boar-combat',
        consequences: { combat: 'wild-boar' }
      },
      {
        text: 'Try to sneak around it',
        nextNodeId: 'sneak-attempt',
        consequences: {},
        requirements: { stat: { type: 'speed', value: 8 } }
      },
      {
        text: 'Slowly back away',
        nextNodeId: 'retreat-village',
        consequences: { stepCount: 1 }
      }
    ]
  },

  'village-approach': {
    id: 'village-approach',
    type: 'narration',
    text: `As you approach the village, you can see smoke rising from several chimneys and hear the sounds of daily life - children playing, merchants calling their wares, and the rhythmic hammering from a blacksmith's shop.

A wooden sign at the village entrance reads "Thornwick Village - Population 247". A guard in simple leather armor notices your approach and raises his hand in greeting.`,
    choices: [
      {
        text: 'Speak with the guard',
        nextNodeId: 'guard-dialogue',
        consequences: {}
      },
      {
        text: 'Head directly to the market square',
        nextNodeId: 'market-square',
        consequences: { stepCount: 1 }
      },
      {
        text: 'Visit the blacksmith first',
        nextNodeId: 'blacksmith-shop',
        consequences: { stepCount: 1 }
      }
    ]
  },

  'guard-dialogue': {
    id: 'guard-dialogue',
    type: 'dialogue',
    speaker: 'Village Guard',
    text: `"Welcome to Thornwick Village, traveler! I'm Gareth, one of the village guards. You look like you've been on the road for a while."

He studies you with kind but cautious eyes.

"We don't get many adventurers through here these days, not since the troubles started in the Old Mine. If you're looking for work, you might want to speak with Elder Miriam in the town hall. She's been worried about the strange sounds coming from the mine entrance."`,
    choices: [
      {
        text: 'Ask about the Old Mine troubles',
        nextNodeId: 'mine-info',
        consequences: {}
      },
      {
        text: 'Ask for directions to the town hall',
        nextNodeId: 'town-hall-directions',
        consequences: {}
      },
      {
        text: 'Thank him and explore the village',
        nextNodeId: 'market-square',
        consequences: { stepCount: 1 }
      }
    ]
  },

  'mine-info': {
    id: 'mine-info',
    type: 'dialogue',
    speaker: 'Village Guard',
    text: `Gareth's expression grows serious.

"The Old Mine has been abandoned for nigh on twenty years now, ever since the silver ran dry. But lately, folks have been hearing strange noises echoing from deep within - scraping sounds, like something large moving around in the dark.

Last week, young Tom ventured too close to the entrance and came running back, white as a sheet. He claimed he saw glowing eyes in the darkness. Course, Tom's always been one for tall tales, but..."

He shakes his head.

"Elder Miriam thinks it might be bandits using the mine as a hideout, but I'm not so sure. Bandits don't make sounds like that."`,
    choices: [
      {
        text: 'Offer to investigate the mine',
        nextNodeId: 'volunteer-mine',
        consequences: {}
      },
      {
        text: 'Ask about rewards for helping',
        nextNodeId: 'reward-discussion',
        consequences: {}
      },
      {
        text: 'Say you\'ll think about it and head to the village',
        nextNodeId: 'market-square',
        consequences: { stepCount: 1 }
      }
    ]
  }
};

export default STORY_NODES;