import React, { useContext } from 'react';
import { GameContext } from '../../contexts/GameContext';
import { Item, Weapon, Armor, Consumable } from '../../types/game.types';
import { Button } from '../ui/button';
import * as Icons from '../ui/Icons';

const InventoryView: React.FC = () => {
  const { state, dispatch } = useContext(GameContext);
  const { character } = state;

  if (!character) {
    return <div>No character data available</div>;
  }

  const handleUseItem = (item: Item, index: number) => {
    if (item.type === 'consumable') {
      dispatch({ type: 'USE_ITEM', payload: index });
    }
  };

  const handleDropItem = (index: number) => {
    dispatch({ type: 'DROP_ITEM', payload: index });
  };

  const handleEquipWeapon = (index: number) => {
    dispatch({ type: 'EQUIP_WEAPON', payload: index });
  };

  const handleEquipArmor = (index: number) => {
    dispatch({ type: 'EQUIP_ARMOR', payload: index });
  };

  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'legendary': return 'text-orange-400';
      case 'epic': return 'text-purple-400';
      case 'rare': return 'text-blue-400';
      case 'uncommon': return 'text-green-400';
      default: return 'text-gray-300';
    }
  };

  const renderItemIcon = (item: Item) => {
    switch (item.type) {
      case 'weapon': return <Icons.Sword className="h-8 w-8" />;
      case 'armor': return <Icons.Shield className="h-8 w-8" />;
      case 'consumable': return <Icons.Potion className="h-8 w-8" />;
      default: return <Icons.Bag className="h-8 w-8" />;
    }
  };

  const renderItemStats = (item: Item) => {
    if (item.type === 'weapon') {
      const weapon = item as Weapon;
      return (
        <div className="text-sm space-y-1">
          <div className="flex items-center gap-2">
            <Icons.Sword className="h-4 w-4" />
            <span>Damage: {weapon.damage.min}-{weapon.damage.max}</span>
          </div>
          {weapon.speed !== undefined && weapon.speed !== 0 && (
            <div className="flex items-center gap-2">
              <Icons.Boot className="h-4 w-4" />
              <span>Speed: {weapon.speed > 0 ? '+' : ''}{weapon.speed}</span>
            </div>
          )}
          {weapon.durability && (
            <div className="text-amber-400">
              Durability: {weapon.durability.current}/{weapon.durability.max}
            </div>
          )}
        </div>
      );
    } else if (item.type === 'armor') {
      const armor = item as Armor;
      return (
        <div className="text-sm space-y-1">
          <div className="flex items-center gap-2">
            <Icons.Shield className="h-4 w-4" />
            <span>Defense: +{armor.defense}</span>
          </div>
          {armor.speed !== undefined && armor.speed !== 0 && (
            <div className="flex items-center gap-2">
              <Icons.Boot className="h-4 w-4" />
              <span>Speed: {armor.speed > 0 ? '+' : ''}{armor.speed}</span>
            </div>
          )}
        </div>
      );
    } else if (item.type === 'consumable') {
      const consumable = item as Consumable;
      return (
        <div className="text-sm">
          <div className="text-green-400">{consumable.effect.description}</div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="inventory-view space-y-6">
      {/* Equipped Items */}
      <div>
        <h3 className="font-medieval text-xl mb-4 text-gold">Equipped</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {character.equipped.weapon && (
            <div className="bg-parchment-dark p-4 rounded-lg border-2 border-gold">
              <div className="flex items-start gap-3">
                {renderItemIcon(character.equipped.weapon)}
                <div className="flex-1">
                  <h4 className={`font-semibold ${getRarityColor(character.equipped.weapon.rarity)}`}>
                    {character.equipped.weapon.name}
                  </h4>
                  {renderItemStats(character.equipped.weapon)}
                </div>
              </div>
            </div>
          )}
          {character.equipped.armor && (
            <div className="bg-parchment-dark p-4 rounded-lg border-2 border-gold">
              <div className="flex items-start gap-3">
                {renderItemIcon(character.equipped.armor)}
                <div className="flex-1">
                  <h4 className={`font-semibold ${getRarityColor(character.equipped.armor.rarity)}`}>
                    {character.equipped.armor.name}
                  </h4>
                  {renderItemStats(character.equipped.armor)}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Inventory Slots */}
      <div>
        <h3 className="font-medieval text-xl mb-4 text-gold">
          Inventory ({character.inventory.filter(i => i !== null).length}/4)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {character.inventory.map((item, index) => (
            <div
              key={index}
              className={`bg-parchment-dark p-4 rounded-lg border-2 ${
                item ? 'border-parchment' : 'border-gray-600 border-dashed'
              }`}
            >
              {item ? (
                <div className="space-y-3">
                  <div className="flex items-start gap-3">
                    {renderItemIcon(item)}
                    <div className="flex-1">
                      <h4 className={`font-semibold ${getRarityColor(item.rarity)}`}>
                        {item.name}
                      </h4>
                      <p className="text-sm text-gray-400 mt-1">{item.description}</p>
                      {renderItemStats(item)}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    {item.type === 'consumable' && (
                      <Button
                        size="sm"
                        variant="success"
                        onClick={() => handleUseItem(item, index)}
                      >
                        Use
                      </Button>
                    )}
                    {item.type === 'weapon' && !character.equipped.weapon && (
                      <Button
                        size="sm"
                        variant="default"
                        onClick={() => handleEquipWeapon(index)}
                      >
                        Equip
                      </Button>
                    )}
                    {item.type === 'armor' && !character.equipped.armor && (
                      <Button
                        size="sm"
                        variant="default"
                        onClick={() => handleEquipArmor(index)}
                      >
                        Equip
                      </Button>
                    )}
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => handleDropItem(index)}
                    >
                      Drop
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="text-center text-gray-500 py-8">
                  <Icons.Bag className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p>Empty Slot</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Gold */}
      <div className="bg-parchment-dark p-4 rounded-lg border-2 border-gold">
        <div className="flex items-center justify-between">
          <h3 className="font-medieval text-xl text-gold">Treasure</h3>
          <div className="flex items-center gap-2">
            <Icons.Diamond className="h-6 w-6 text-yellow-400" />
            <span className="text-2xl font-bold text-yellow-400">{character.gold}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InventoryView;