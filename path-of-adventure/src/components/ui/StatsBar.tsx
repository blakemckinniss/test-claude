import React from 'react';
import * as Icons from './Icons';
import { Card, CardContent } from './card';
import { Progress } from './progress';

export interface StatsBarProps {
  health: number;
  maxHealth: number;
  attack: number;
  speed: number;
  gems: number;
}

const StatsBar: React.FC<StatsBarProps> = ({
  health,
  maxHealth,
  attack,
  speed,
  gems
}) => {
  const healthPercent = (health / maxHealth) * 100;

  return (
    <Card className="mb-6 bg-gradient-to-br from-parchment-light/95 to-parchment-dark/90 backdrop-blur-sm border-2 border-parchment-shadow/50 shadow-lg hover:shadow-xl transition-all duration-300">
      <CardContent className="p-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {/* Health */}
          <div className="stat-item bg-gradient-to-br from-parchment/50 to-parchment-dark/50 p-4 rounded-lg border border-parchment-shadow/30 hover:bg-parchment/60 transition-all duration-200">
            <div className="flex items-center gap-2 mb-2">
              <Icons.Heart className="h-5 w-5 text-red-600 drop-shadow-sm" />
              <span className="font-semibold text-ink-black font-medieval">Health</span>
            </div>
            <div className="text-lg font-bold text-ink-black mb-2">
              {health} / {maxHealth}
            </div>
            <Progress 
              value={healthPercent} 
              className="mt-1"
              indicatorClassName="bg-gradient-to-r from-red-600 to-red-400"
            />
          </div>

          {/* Attack */}
          <div className="stat-item bg-gradient-to-br from-parchment/50 to-parchment-dark/50 p-4 rounded-lg border border-parchment-shadow/30 hover:bg-parchment/60 transition-all duration-200">
            <div className="flex items-center gap-2 mb-2">
              <Icons.Sword className="h-5 w-5 text-orange-600 drop-shadow-sm" />
              <span className="font-semibold text-ink-black font-medieval">Attack</span>
            </div>
            <div className="text-xl font-bold text-orange-600">{attack}</div>
          </div>

          {/* Speed */}
          <div className="stat-item bg-gradient-to-br from-parchment/50 to-parchment-dark/50 p-4 rounded-lg border border-parchment-shadow/30 hover:bg-parchment/60 transition-all duration-200">
            <div className="flex items-center gap-2 mb-2">
              <Icons.Boot className="h-5 w-5 text-green-600 drop-shadow-sm" />
              <span className="font-semibold text-ink-black font-medieval">Speed</span>
            </div>
            <div className="text-xl font-bold text-green-600">{speed}</div>
          </div>

          {/* Gold */}
          <div className="stat-item bg-gradient-to-br from-parchment/50 to-parchment-dark/50 p-4 rounded-lg border border-parchment-shadow/30 hover:bg-parchment/60 transition-all duration-200">
            <div className="flex items-center gap-2 mb-2">
              <Icons.Diamond className="h-5 w-5 text-gold drop-shadow-sm" />
              <span className="font-semibold text-ink-black font-medieval">Gold</span>
            </div>
            <div className="text-xl font-bold text-gold">{gems}</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default StatsBar;