# Path of Adventure

A browser-based remake of the classic choose-your-own-adventure RPG, built with React and TypeScript.

## 🎮 Features

- **Choose Your Adventure**: Navigate through a branching narrative with meaningful choices
- **Turn-Based Combat**: Strategic combat system with attack/defense phases
- **Character Development**: Level up system with stat progression
- **Inventory Management**: 4-slot inventory with weapons, armor, and consumables
- **Status Effects**: Poison, regeneration, and various buffs/debuffs
- **Dungeon Exploration**: Explore optional dungeons with treasures and boss fights
- **Medieval UI**: Parchment-style interface with atmospheric cave backdrop

## 🚀 Getting Started

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser to `http://localhost:5173`

## 🎯 How to Play

1. **Create Your Character**: Choose between Warrior, Rogue, or Mage classes
2. **Make Choices**: Click on story options to progress through the adventure
3. **Combat**: 
   - Attack Phase: Choose your weapon or use bare hands
   - Defense Phase: Block with shields/armor or try to dodge
4. **Manage Resources**: Keep track of health, gold, and inventory
5. **Level Up**: Gain experience from combat to increase your stats

## 🏗️ Architecture

- **State Management**: React Context with useReducer for game state
- **Component-Based**: Modular UI components with TypeScript
- **Data-Driven**: Story nodes, items, and enemies defined in JSON
- **Responsive Design**: Works on desktop and mobile devices

## 📁 Project Structure

```
src/
├── components/      # React components
├── game/           # Game logic and mechanics
├── data/           # Game content (story, items, enemies)
├── types/          # TypeScript type definitions
├── contexts/       # React contexts for state management
└── styles/         # CSS and theming
```

## 🛠️ Technologies

- React 18
- TypeScript 5
- Vite
- Tailwind CSS
- CSS Custom Properties for theming

## 🎨 Credits

Inspired by classic text-based RPGs and choose-your-own-adventure games.