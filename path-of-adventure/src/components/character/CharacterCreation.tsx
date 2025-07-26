import React, { useState, useContext } from 'react';
import { GameContext } from '../../contexts/GameContext';
import { CharacterClass } from '../../types/game.types';
import { Button } from '../ui/button';

const CharacterCreation: React.FC = () => {
  const { dispatch } = useContext(GameContext);
  const [name, setName] = useState('');
  const [characterClass, setCharacterClass] = useState<CharacterClass>('warrior');

  const handleCreateCharacter = () => {
    if (name.trim()) {
      dispatch({
        type: 'CREATE_CHARACTER',
        payload: { name: name.trim(), characterClass }
      });
    }
  };

  const classDescriptions = {
    warrior: 'Strong and durable. High health and attack, but slower movement.',
    rogue: 'Quick and agile. Fast movement and good at avoiding damage.',
    mage: 'Intelligent spellcaster. Moderate stats with potential for magical abilities.'
  };

  return (
    <div className="character-creation bg-parchment-dark p-8 rounded-lg border-2 border-gold max-w-md mx-auto">
      <h2 className="font-medieval text-3xl text-gold mb-6 text-center">
        Create Your Character
      </h2>
      
      <div className="space-y-6">
        <div>
          <label className="block text-lg font-semibold mb-2 text-parchment-light">
            Character Name
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full p-3 bg-parchment border-2 border-parchment-dark rounded text-black"
            placeholder="Enter your name..."
            maxLength={20}
          />
        </div>

        <div>
          <label className="block text-lg font-semibold mb-2 text-parchment-light">
            Choose Your Class
          </label>
          <div className="space-y-3">
            {(Object.keys(classDescriptions) as CharacterClass[]).map((cls) => (
              <div
                key={cls}
                className={`p-4 border-2 rounded cursor-pointer transition-colors ${
                  characterClass === cls
                    ? 'border-gold bg-gold bg-opacity-20'
                    : 'border-parchment-dark bg-parchment-dark hover:border-gold'
                }`}
                onClick={() => setCharacterClass(cls)}
              >
                <h3 className="font-semibold text-lg capitalize mb-1 text-gold">
                  {cls}
                </h3>
                <p className="text-sm text-parchment-light">
                  {classDescriptions[cls]}
                </p>
              </div>
            ))}
          </div>
        </div>

        <Button
          onClick={handleCreateCharacter}
          disabled={!name.trim()}
          variant="default"
          size="lg"
          className="w-full"
        >
          Begin Adventure
        </Button>
      </div>
    </div>
  );
};

export default CharacterCreation;