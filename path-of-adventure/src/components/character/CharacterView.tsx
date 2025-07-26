import React, { useContext } from 'react';
import { GameContext } from '../../contexts/GameContext';
import * as Icons from '../ui/Icons';
import { StatusEffect } from '../../types/game.types';

const CharacterView: React.FC = () => {
  const { state } = useContext(GameContext);
  const { character, combat } = state;

  if (!character) {
    return <div>No character data available</div>;
  }

  const getEffectiveStats = () => {
    let attack = character.attack;
    let defense = character.defense;
    let speed = character.speed;

    // Add equipment bonuses
    if (character.equipped.weapon) {
      speed += character.equipped.weapon.speed || 0;
    }
    if (character.equipped.armor) {
      defense += character.equipped.armor.defense || 0;
      speed += character.equipped.armor.speed || 0;
    }

    // Add status effect modifiers
    character.statusEffects.forEach(effect => {
      if (effect.type === 'attack_boost') attack += effect.value || 0;
      if (effect.type === 'defense_boost') defense += effect.value || 0;
      if (effect.type === 'speed_boost') speed += effect.value || 0;
    });

    return { attack, defense, speed };
  };

  const effectiveStats = getEffectiveStats();

  const getStatusEffectIcon = (effect: StatusEffect) => {
    switch (effect.type) {
      case 'poison': return <Icons.Poison className="h-6 w-6" />;
      case 'regeneration': return <Icons.Heart className="h-6 w-6 text-green-400" />;
      case 'attack_boost':
      case 'defense_boost':
      case 'speed_boost': return <Icons.Buff className="h-6 w-6" />;
      case 'stun': return <Icons.Frozen className="h-6 w-6" />;
      default: return null;
    }
  };

  const getStatusEffectColor = (effect: StatusEffect) => {
    switch (effect.type) {
      case 'poison': return 'text-purple-400';
      case 'regeneration': return 'text-green-400';
      case 'stun': return 'text-blue-400';
      default: return 'text-yellow-400';
    }
  };

  return (
    <div className="character-view space-y-6">
      {/* Character Info */}
      <div className="bg-parchment-dark p-6 rounded-lg border-2 border-gold">
        <h3 className="font-medieval text-2xl mb-4 text-gold">{character.name}</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-400">Class</p>
            <p className="text-xl font-semibold capitalize">{character.class}</p>
          </div>
          <div>
            <p className="text-sm text-gray-400">Level</p>
            <p className="text-xl font-semibold">{character.level}</p>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="bg-parchment-dark p-6 rounded-lg border-2 border-parchment">
        <h3 className="font-medieval text-xl mb-4 text-gold">Statistics</h3>
        <div className="space-y-4">
          {/* Health */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Icons.Heart className="h-6 w-6 text-red-500" />
                <span className="font-semibold">Health</span>
              </div>
              <span className="text-xl">{character.health} / {character.maxHealth}</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-3">
              <div
                className="bg-red-500 h-3 rounded-full transition-all"
                style={{ width: `${(character.health / character.maxHealth) * 100}%` }}
              />
            </div>
          </div>

          {/* Attack */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Icons.Sword className="h-6 w-6 text-orange-400" />
              <span className="font-semibold">Attack</span>
            </div>
            <div className="text-xl">
              <span className={effectiveStats.attack > character.attack ? 'text-green-400' : ''}>
                {effectiveStats.attack}
              </span>
              {effectiveStats.attack !== character.attack && (
                <span className="text-sm text-gray-400 ml-2">
                  ({character.attack} + {effectiveStats.attack - character.attack})
                </span>
              )}
            </div>
          </div>

          {/* Defense */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Icons.Shield className="h-6 w-6 text-blue-400" />
              <span className="font-semibold">Defense</span>
            </div>
            <div className="text-xl">
              <span className={effectiveStats.defense > character.defense ? 'text-green-400' : ''}>
                {effectiveStats.defense}
              </span>
              {effectiveStats.defense !== character.defense && (
                <span className="text-sm text-gray-400 ml-2">
                  ({character.defense} + {effectiveStats.defense - character.defense})
                </span>
              )}
            </div>
          </div>

          {/* Speed */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Icons.Boot className="h-6 w-6 text-green-400" />
              <span className="font-semibold">Speed</span>
            </div>
            <div className="text-xl">
              <span className={effectiveStats.speed !== character.speed ? 
                (effectiveStats.speed > character.speed ? 'text-green-400' : 'text-red-400') : ''}>
                {effectiveStats.speed}
              </span>
              {effectiveStats.speed !== character.speed && (
                <span className="text-sm text-gray-400 ml-2">
                  ({character.speed} {effectiveStats.speed > character.speed ? '+' : ''}{effectiveStats.speed - character.speed})
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Experience */}
      <div className="bg-parchment-dark p-6 rounded-lg border-2 border-parchment">
        <h3 className="font-medieval text-xl mb-4 text-gold">Experience</h3>
        <div>
          <div className="flex justify-between mb-2">
            <span>Progress to Level {character.level + 1}</span>
            <span>{character.experience} / {character.experienceToNext} XP</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-3">
            <div
              className="bg-purple-500 h-3 rounded-full transition-all"
              style={{ width: `${(character.experience / character.experienceToNext) * 100}%` }}
            />
          </div>
        </div>
      </div>

      {/* Status Effects */}
      {character.statusEffects.length > 0 && (
        <div className="bg-parchment-dark p-6 rounded-lg border-2 border-parchment">
          <h3 className="font-medieval text-xl mb-4 text-gold">Status Effects</h3>
          <div className="space-y-3">
            {character.statusEffects.map((effect, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {getStatusEffectIcon(effect)}
                  <div>
                    <p className={`font-semibold capitalize ${getStatusEffectColor(effect)}`}>
                      {effect.type.replace('_', ' ')}
                    </p>
                    <p className="text-sm text-gray-400">{effect.description}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-400">
                    {effect.duration} {effect.duration === 1 ? 'turn' : 'turns'} left
                  </p>
                  {effect.value && (
                    <p className="text-sm font-semibold">+{effect.value}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Combat Stats (if in combat) */}
      {combat && (
        <div className="bg-red-900 bg-opacity-50 p-6 rounded-lg border-2 border-red-600">
          <h3 className="font-medieval text-xl mb-4 text-red-400">In Combat!</h3>
          <div className="space-y-2">
            <p className="text-lg">Fighting: <span className="font-bold text-red-300">{combat.enemy.name}</span></p>
            <p>Turn: {combat.turn}</p>
            <p>Phase: {combat.phase}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default CharacterView;