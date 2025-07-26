import React, { useContext, useEffect } from 'react';
import { GameProvider, GameContext } from './contexts/GameContext';
import { UIProvider, UIContext } from './contexts/UIContext';
import GameLayout from './components/layout/GameLayout';
import StatsBar from './components/ui/StatsBar';
import { GameTabs } from './components/ui/game-tabs';
import StoryView from './components/story/StoryView';
import CharacterView from './components/character/CharacterView';
import InventoryView from './components/inventory/InventoryView';
import CombatView from './components/combat/CombatView';
import CharacterCreation from './components/character/CharacterCreation';
import { Button } from './components/ui/button';
import './styles/parchment-theme.css';

const GameContent: React.FC = () => {
  const { state, dispatch } = useContext(GameContext);
  const { activeTab, setActiveTab } = useContext(UIContext);

  useEffect(() => {
    // Apply status effects each turn
    if (state.character && !state.combat) {
      dispatch({ type: 'APPLY_STATUS_EFFECTS' });
    }
  }, [state.currentNode]);

  const handleNewGame = () => {
    if (window.confirm('Are you sure you want to start a new game? All progress will be lost.')) {
      dispatch({ type: 'NEW_GAME' });
    }
  };

  const renderContent = () => {
    if (!state.character) {
      return <CharacterCreation />;
    }

    if (state.combat) {
      return <CombatView />;
    }

    switch (activeTab) {
      case 'story':
        return <StoryView />;
      case 'character':
        return <CharacterView />;
      case 'inventory':
        return <InventoryView />;
      default:
        return <StoryView />;
    }
  };

  return (
    <GameLayout>
      <div className="space-y-6">
        {/* Game Header */}
        {state.character && (
          <div className="space-y-4">
            {/* Title and Game Controls */}
            <div className="text-center mb-6">
              <h1 className="font-script text-4xl text-amber-800 mb-2 drop-shadow-lg">
                Path of Adventure
              </h1>
              <div className="flex justify-between items-center">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleNewGame}
                  className="flex items-center gap-2"
                >
                  🔄 New Game
                </Button>
                <div className="bg-parchment-dark/80 px-4 py-2 rounded-lg border border-parchment-shadow">
                  <span className="text-ink-black font-medium">
                    Step {state.stepCount} / 50
                  </span>
                </div>
              </div>
            </div>
            
            {/* Stats Bar */}
            <StatsBar
              health={state.character.health}
              maxHealth={state.character.maxHealth}
              attack={state.character.attack}
              speed={state.character.speed}
              gems={state.character.gold}
            />
          </div>
        )}

        {/* Character Creation Title */}
        {!state.character && (
          <div className="text-center mb-8">
            <h1 className="font-script text-5xl text-amber-800 mb-4 drop-shadow-lg">
              Path of Adventure
            </h1>
            <p className="text-ink-black/80 text-lg font-medium">
              Begin your epic journey...
            </p>
          </div>
        )}

        {/* Main Content */}
        <div className="min-h-[400px]">
          {!state.combat && state.character ? (
            <GameTabs activeTab={activeTab} onTabChange={setActiveTab}>
              {renderContent()}
            </GameTabs>
          ) : (
            <div className="w-full">
              {renderContent()}
            </div>
          )}
        </div>
      </div>
    </GameLayout>
  );
};

function App() {
  return (
    <GameProvider>
      <UIProvider>
        <GameContent />
      </UIProvider>
    </GameProvider>
  );
}

export default App;