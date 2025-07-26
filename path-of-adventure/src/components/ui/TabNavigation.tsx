import React from 'react';
import * as Icons from './Icons';

type TabType = 'story' | 'character' | 'inventory';

interface TabNavigationProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
}

const TabNavigation: React.FC<TabNavigationProps> = ({ activeTab, onTabChange }) => {
  const tabs = [
    { id: 'story' as TabType, label: 'Story', icon: Icons.Scroll },
    { id: 'character' as TabType, label: 'Character', icon: Icons.Character },
    { id: 'inventory' as TabType, label: 'Inventory', icon: Icons.Bag }
  ];

  return (
    <div className="tab-navigation bg-parchment-dark rounded-lg border-2 border-parchment p-1">
      <div className="flex">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => onTabChange(id)}
            className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded transition-all ${
              activeTab === id
                ? 'bg-gold text-black font-semibold'
                : 'text-parchment-light hover:bg-parchment hover:text-white'
            }`}
          >
            <Icon className="h-5 w-5" />
            <span className="hidden sm:inline">{label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default TabNavigation;