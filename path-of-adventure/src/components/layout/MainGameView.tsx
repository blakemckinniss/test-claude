import React, { useContext } from 'react';
import { GameContext } from '../../contexts/GameContext';
import { UIContext } from '../../contexts/UIContext';
import StoryView from '../story/StoryView';
import CharacterView from '../character/CharacterView';
import InventoryView from '../inventory/InventoryView';
import CombatView from '../combat/CombatView';
import CharacterCreation from '../character/CharacterCreation';
import { GameTabs } from '../ui/game-tabs';
import StatsBar from '../ui/StatsBar';

const MainGameView: React.FC = () => {
  const { state } = useContext(GameContext);
  const { activeTab, setActiveTab } = useContext(UIContext);

  if (!state.character) {
    return <CharacterCreation />;
  }

  const renderActiveView = () => {
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
    <div className="main-game-view h-screen bg-cave bg-cover bg-center">
      <div className="h-full bg-black bg-opacity-60 flex flex-col">
        <div className="p-4">
          <StatsBar
            health={state.character.health}
            maxHealth={state.character.maxHealth}
            attack={state.character.attack}
            speed={state.character.speed}
            gems={state.character.gold}
          />
        </div>
        
        <div className="flex-1 p-4">
          <div className="max-w-4xl mx-auto">
            {!state.combat ? (
              <GameTabs activeTab={activeTab} onTabChange={setActiveTab}>
                {renderActiveView()}
              </GameTabs>
            ) : (
              <div className="game-content">
                {renderActiveView()}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MainGameView;