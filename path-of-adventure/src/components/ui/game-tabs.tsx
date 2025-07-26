import React from 'react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from './tabs';
import * as Icons from './Icons';

type TabType = 'story' | 'character' | 'inventory';

interface GameTabsProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
  children: React.ReactNode;
}

export const GameTabs: React.FC<GameTabsProps> = ({ activeTab, onTabChange, children }) => {
  return (
    <Tabs value={activeTab} onValueChange={(value) => onTabChange(value as TabType)}>
      <TabsList className="grid w-full grid-cols-3">
        <TabsTrigger value="story" className="flex items-center gap-2">
          <Icons.Scroll className="h-4 w-4" />
          <span className="hidden sm:inline">Story</span>
        </TabsTrigger>
        <TabsTrigger value="character" className="flex items-center gap-2">
          <Icons.Character className="h-4 w-4" />
          <span className="hidden sm:inline">Character</span>
        </TabsTrigger>
        <TabsTrigger value="inventory" className="flex items-center gap-2">
          <Icons.Bag className="h-4 w-4" />
          <span className="hidden sm:inline">Inventory</span>
        </TabsTrigger>
      </TabsList>
      <TabsContent value={activeTab} className="mt-4">
        {children}
      </TabsContent>
    </Tabs>
  );
};