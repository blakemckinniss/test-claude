import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react'

export type UIPanel = 'inventory' | 'character' | 'quest' | 'map' | 'settings' | 'combat' | 'dialogue'

interface UIState {
  activePanel: UIPanel | null
  isPanelOpen: boolean
  isMenuOpen: boolean
  notifications: Notification[]
  modalContent: ModalContent | null
  theme: 'light' | 'dark'
}

interface Notification {
  id: string
  message: string
  type: 'info' | 'success' | 'warning' | 'error'
  duration?: number
}

interface ModalContent {
  title: string
  content: ReactNode
  actions?: ModalAction[]
}

interface ModalAction {
  label: string
  onClick: () => void
  variant?: 'primary' | 'secondary' | 'danger'
}

interface UIContextType {
  state: UIState
  
  // Panel management
  openPanel: (panel: UIPanel) => void
  closePanel: () => void
  togglePanel: (panel: UIPanel) => void
  
  // Menu management
  toggleMenu: () => void
  
  // Notifications
  showNotification: (message: string, type?: Notification['type'], duration?: number) => void
  dismissNotification: (id: string) => void
  
  // Modal management
  showModal: (content: ModalContent) => void
  closeModal: () => void
  
  // Theme
  toggleTheme: () => void
}

const UIContext = createContext<UIContextType | undefined>(undefined)

export const useUI = () => {
  const context = useContext(UIContext)
  if (!context) {
    throw new Error('useUI must be used within a UIProvider')
  }
  return context
}

interface UIProviderProps {
  children: ReactNode
}

export const UIProvider: React.FC<UIProviderProps> = ({ children }) => {
  const [state, setState] = useState<UIState>({
    activePanel: null,
    isPanelOpen: false,
    isMenuOpen: false,
    notifications: [],
    modalContent: null,
    theme: 'dark'
  })

  // Panel management
  const openPanel = useCallback((panel: UIPanel) => {
    setState(prev => ({
      ...prev,
      activePanel: panel,
      isPanelOpen: true
    }))
  }, [])

  const closePanel = useCallback(() => {
    setState(prev => ({
      ...prev,
      isPanelOpen: false
    }))
  }, [])

  const togglePanel = useCallback((panel: UIPanel) => {
    setState(prev => ({
      ...prev,
      activePanel: panel,
      isPanelOpen: prev.activePanel === panel ? !prev.isPanelOpen : true
    }))
  }, [])

  // Menu management
  const toggleMenu = useCallback(() => {
    setState(prev => ({
      ...prev,
      isMenuOpen: !prev.isMenuOpen
    }))
  }, [])

  // Notifications
  const showNotification = useCallback(
    (message: string, type: Notification['type'] = 'info', duration: number = 5000) => {
      const id = Date.now().toString()
      const notification: Notification = {
        id,
        message,
        type,
        duration
      }

      setState(prev => ({
        ...prev,
        notifications: [...prev.notifications, notification]
      }))

      if (duration > 0) {
        setTimeout(() => {
          dismissNotification(id)
        }, duration)
      }
    },
    []
  )

  const dismissNotification = useCallback((id: string) => {
    setState(prev => ({
      ...prev,
      notifications: prev.notifications.filter(n => n.id !== id)
    }))
  }, [])

  // Modal management
  const showModal = useCallback((content: ModalContent) => {
    setState(prev => ({
      ...prev,
      modalContent: content
    }))
  }, [])

  const closeModal = useCallback(() => {
    setState(prev => ({
      ...prev,
      modalContent: null
    }))
  }, [])

  // Theme
  const toggleTheme = useCallback(() => {
    setState(prev => ({
      ...prev,
      theme: prev.theme === 'dark' ? 'light' : 'dark'
    }))
  }, [])

  const value: UIContextType = {
    state,
    openPanel,
    closePanel,
    togglePanel,
    toggleMenu,
    showNotification,
    dismissNotification,
    showModal,
    closeModal,
    toggleTheme
  }

  return <UIContext.Provider value={value}>{children}</UIContext.Provider>
}