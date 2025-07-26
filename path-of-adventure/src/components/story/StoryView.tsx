import React, { useContext, useEffect, useRef } from 'react';
import { GameContext } from '../../contexts/GameContext';
import StoryTextArea from '../ui/StoryTextArea';
import { Button } from '../ui/button';
import { StoryChoice } from '../../types/game.types';

const StoryView: React.FC = () => {
  const { state, dispatch } = useContext(GameContext);
  const { currentNode, previousTexts } = state;
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [previousTexts]);

  const handleChoice = (choice: StoryChoice) => {
    dispatch({ type: 'MAKE_CHOICE', payload: choice });
  };

  const renderContent = () => {
    const allTexts = [...previousTexts];
    if (currentNode?.text) {
      allTexts.push({
        text: currentNode.text,
        type: currentNode.type === 'dialogue' ? 'dialogue' : 'narration'
      });
    }

    return (
      <>
        <StoryTextArea texts={allTexts} />
        {currentNode?.choices && currentNode.choices.length > 0 && (
          <div className="mt-6 space-y-3">
            {currentNode.choices.map((choice, index) => {
              const meetsRequirements = !choice.requirements || 
                (choice.requirements.level ? (state.character?.level || 0) >= choice.requirements.level : true) &&
                (choice.requirements.stat ? 
                  (state.character?.[choice.requirements.stat.type] || 0) >= choice.requirements.stat.value : true) &&
                (choice.requirements.item ? 
                  state.character?.inventory.some(i => i?.id === choice.requirements.item) : true);

              return (
                <Button
                  key={index}
                  onClick={() => handleChoice(choice)}
                  disabled={!meetsRequirements}
                  variant={choice.consequences?.health ? 'destructive' : 'default'}
                  className="w-full"
                  size="lg"
                >
                  {choice.text}
                  {!meetsRequirements && ' (Requirements not met)'}
                </Button>
              );
            })}
          </div>
        )}
        <div ref={bottomRef} />
      </>
    );
  };

  return (
    <div className="story-view">
      {renderContent()}
    </div>
  );
};

export default StoryView;