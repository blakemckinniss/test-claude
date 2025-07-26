import React, { createContext, useContext, useState, ReactNode } from 'react';

type TabType = 'story' | 'character' | 'inventory';

interface UIContextType {
  activeTab: TabType;
  setActiveTab: (tab: TabType) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
}

const UIContext = createContext<UIContextType>({} as UIContextType);

interface UIProviderProps {
  children: ReactNode;
}

export const UIProvider: React.FC<UIProviderProps> = ({ children }) => {
  const [activeTab, setActiveTab] = useState<TabType>('story');
  const [isLoading, setIsLoading] = useState(false);

  return (
    <UIContext.Provider value={{
      activeTab,
      setActiveTab,
      isLoading,
      setIsLoading
    }}>
      {children}
    </UIContext.Provider>
  );
};

export const useUI = () => {
  const context = useContext(UIContext);
  if (!context) {
    throw new Error('useUI must be used within a UIProvider');
  }
  return context;
};

export { UIContext };