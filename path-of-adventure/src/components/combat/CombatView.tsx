import React, { useContext, useState } from 'react';
import { GameContext } from '../../contexts/GameContext';
import { Button } from '../ui/button';
import * as Icons from '../ui/Icons';
import { Weapon } from '../../types/game.types';

const CombatView: React.FC = () => {
  const { state, dispatch } = useContext(GameContext);
  const { combat, character } = state;
  const [selectedAction, setSelectedAction] = useState<string | null>(null);

  if (!combat || !character) return null;

  const handleAttack = (weaponIndex?: number) => {
    dispatch({ 
      type: 'COMBAT_ACTION', 
      payload: { 
        action: 'attack', 
        weaponIndex 
      } 
    });
    setSelectedAction(null);
  };

  const handleDefend = (type: 'block' | 'dodge', itemIndex?: number) => {
    dispatch({ 
      type: 'COMBAT_ACTION', 
      payload: { 
        action: 'defend',
        defendType: type,
        itemIndex
      } 
    });
    setSelectedAction(null);
  };

  const handleFlee = () => {
    dispatch({ type: 'FLEE_COMBAT' });
  };

  const getAvailableWeapons = () => {
    const weapons: Array<{ weapon: Weapon | null; index?: number; label: string }> = [];
    
    // Add equipped weapon
    if (character.equipped.weapon) {
      weapons.push({
        weapon: character.equipped.weapon,
        label: `${character.equipped.weapon.name} (Equipped)`
      });
    }

    // Add inventory weapons
    character.inventory.forEach((item, index) => {
      if (item && item.type === 'weapon' && !item.faded) {
        weapons.push({
          weapon: item as Weapon,
          index,
          label: item.name
        });
      }
    });

    // Always add bare hands option
    weapons.push({
      weapon: null,
      label: 'Bare Hands'
    });

    return weapons;
  };

  const getDefenseOptions = () => {
    const options: Array<{ type: 'block' | 'dodge'; item?: any; index?: number; label: string }> = [];

    // Add equipped armor
    if (character.equipped.armor) {
      options.push({
        type: 'block',
        item: character.equipped.armor,
        label: `Block with ${character.equipped.armor.name} (+${character.equipped.armor.defense})`
      });
    }

    // Add equipped weapon if it has defense
    if (character.equipped.weapon && character.equipped.weapon.defense) {
      options.push({
        type: 'block',
        item: character.equipped.weapon,
        label: `Block with ${character.equipped.weapon.name} (+${character.equipped.weapon.defense || 0})`
      });
    }

    // Always add dodge option
    options.push({
      type: 'dodge',
      label: 'Dodge (25% chance)'
    });

    return options;
  };

  return (
    <div className="combat-view space-y-6">
      {/* Enemy Status */}
      <div className="bg-red-900 bg-opacity-50 p-6 rounded-lg border-2 border-red-600">
        <h3 className="font-medieval text-2xl mb-4 text-red-400">{combat.enemy.name}</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div className="text-center">
            <Icons.Heart className="h-8 w-8 mx-auto text-red-500" />
            <p className="text-xl font-bold">{combat.enemy.health}/{combat.enemy.maxHealth}</p>
            <p className="text-sm text-gray-400">Health</p>
          </div>
          <div className="text-center">
            <Icons.Sword className="h-8 w-8 mx-auto text-orange-400" />
            <p className="text-xl font-bold">{combat.enemy.attack.min}-{combat.enemy.attack.max}</p>
            <p className="text-sm text-gray-400">Attack</p>
          </div>
          <div className="text-center">
            <Icons.Shield className="h-8 w-8 mx-auto text-blue-400" />
            <p className="text-xl font-bold">{combat.enemy.defense}</p>
            <p className="text-sm text-gray-400">Defense</p>
          </div>
          <div className="text-center">
            <Icons.Boot className="h-8 w-8 mx-auto text-green-400" />
            <p className="text-xl font-bold">{combat.enemy.speed}</p>
            <p className="text-sm text-gray-400">Speed</p>
          </div>
        </div>
        {/* Enemy Health Bar */}
        <div className="w-full bg-gray-700 rounded-full h-4">
          <div
            className="bg-red-500 h-4 rounded-full transition-all"
            style={{ width: `${(combat.enemy.health / combat.enemy.maxHealth) * 100}%` }}
          />
        </div>
      </div>

      {/* Combat Log */}
      <div className="bg-parchment-dark p-4 rounded-lg border-2 border-parchment max-h-40 overflow-y-auto">
        <h4 className="font-medieval text-lg mb-2 text-gold">Combat Log</h4>
        <div className="space-y-1 text-sm">
          {combat.log.slice(-5).map((entry, index) => (
            <p key={index} className={
              entry.includes('dealt') ? 'text-orange-300' :
              entry.includes('took') || entry.includes('damaged') ? 'text-red-300' :
              entry.includes('blocked') || entry.includes('dodged') ? 'text-blue-300' :
              'text-gray-300'
            }>
              {entry}
            </p>
          ))}
        </div>
      </div>

      {/* Combat Actions */}
      <div className="space-y-4">
        {combat.phase === 'player_turn' && !selectedAction && (
          <div>
            <h4 className="font-medieval text-xl mb-3 text-gold">Your Turn - Choose Action</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <Button
                variant="destructive"
                size="lg"
                onClick={() => setSelectedAction('attack')}
              >
                ⚔️ Attack
              </Button>
              <Button
                variant="outline"
                size="lg"
                onClick={handleFlee}
              >
                Flee (Costs {Math.floor(combat.enemy.level * 10)} gold)
              </Button>
            </div>
          </div>
        )}

        {combat.phase === 'player_turn' && selectedAction === 'attack' && (
          <div>
            <h4 className="font-medieval text-xl mb-3 text-gold">Choose Weapon</h4>
            <div className="space-y-2">
              {getAvailableWeapons().map((option, index) => (
                <Button
                  key={index}
                  variant="default"
                  className="w-full"
                  onClick={() => handleAttack(option.index)}
                  disabled={option.weapon?.faded}
                >
                  {option.label}
                  {option.weapon && (
                    <span className="ml-2 text-sm">
                      ({option.weapon.damage.min}-{option.weapon.damage.max} damage)
                    </span>
                  )}
                  {option.weapon?.faded && <span className="ml-2">(Faded)</span>}
                </Button>
              ))}
              <Button
                variant="outline"
                className="w-full"
                onClick={() => setSelectedAction(null)}
              >
                Cancel
              </Button>
            </div>
          </div>
        )}

        {combat.phase === 'enemy_turn' && (
          <div>
            <h4 className="font-medieval text-xl mb-3 text-gold">
              Enemy Attack Incoming! ({combat.enemy.attack.min}-{combat.enemy.attack.max} damage)
            </h4>
            <div className="space-y-2">
              {getDefenseOptions().map((option, index) => (
                <Button
                  key={index}
                  variant={option.type === 'block' ? 'default' : 'secondary'}
                  className="w-full"
                  onClick={() => handleDefend(option.type, option.index)}
                >
                  {option.type === 'block' ? '🛡️' : '💨'} {option.label}
                </Button>
              ))}
            </div>
          </div>
        )}

        {combat.phase === 'victory' && (
          <div className="text-center">
            <h4 className="font-medieval text-2xl mb-4 text-gold">Victory!</h4>
            <p className="text-lg mb-4">You have defeated {combat.enemy.name}!</p>
            {combat.rewards && (
              <div className="space-y-2 mb-4">
                <p className="text-green-400">+{combat.rewards.experience} Experience</p>
                <p className="text-yellow-400">+{combat.rewards.gold} Gold</p>
                {combat.rewards.items && combat.rewards.items.length > 0 && (
                  <p className="text-blue-400">Found: {combat.rewards.items.map(i => i.name).join(', ')}</p>
                )}
              </div>
            )}
            <Button
              variant="success"
              size="lg"
              onClick={() => dispatch({ type: 'END_COMBAT' })}
            >
              Continue
            </Button>
          </div>
        )}

        {combat.phase === 'defeat' && (
          <div className="text-center">
            <h4 className="font-medieval text-2xl mb-4 text-red-500">Defeat!</h4>
            <p className="text-lg mb-4">You have been defeated by {combat.enemy.name}...</p>
            <Button
              variant="destructive"
              size="lg"
              onClick={() => dispatch({ type: 'GAME_OVER' })}
            >
              Game Over
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default CombatView;