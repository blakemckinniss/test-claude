/**
 * Game Initialization Framework - Component Interfaces
 * 
 * This file defines the core interfaces for the game initialization system.
 * These interfaces establish contracts between components and enable
 * dependency injection and testing.
 */

// Core Types
export type InitPhase = 'environment' | 'config' | 'services' | 'resources' | 'state' | 'plugins' | 'final';
export type LogLevel = 'debug' | 'info' | 'warn' | 'error';
export type StorageType = 'local' | 'session' | 'indexed' | 'cloud';

// Configuration Types
export interface Config {
  version: string;
  environment: 'development' | 'staging' | 'production';
  game: GameConfig;
  services: ServicesConfig;
  features: FeatureFlags;
}

export interface GameConfig {
  title: string;
  version: string;
  saveSlots: number;
  autoSaveInterval: number;
  defaultVolume: number;
}

export interface ServicesConfig {
  storage: StorageConfig;
  analytics: AnalyticsConfig;
  logging: LoggingConfig;
}

export interface StorageConfig {
  type: StorageType;
  namespace: string;
  maxSize: number;
}

export interface AnalyticsConfig {
  enabled: boolean;
  endpoint: string;
  sessionTimeout: number;
}

export interface LoggingConfig {
  level: LogLevel;
  console: boolean;
  remote: boolean;
}

export interface FeatureFlags {
  [key: string]: boolean;
}

// Validation Types
export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

export interface ValidationWarning {
  field: string;
  message: string;
}

// Health Check Types
export interface HealthCheckResult {
  healthy: boolean;
  checks: HealthCheck[];
  timestamp: number;
}

export interface HealthCheck {
  name: string;
  status: 'pass' | 'fail' | 'warn';
  message?: string;
  duration: number;
}

// Resource Types
export interface Asset {
  id: string;
  type: 'image' | 'audio' | 'data' | 'font';
  url: string;
  size: number;
  loaded: boolean;
}

export interface AssetMap {
  [id: string]: Asset;
}

export interface SoundManifest {
  music: string[];
  effects: string[];
  ambient: string[];
}

// Game State Types
export interface GameState {
  version: string;
  player: PlayerState;
  world: WorldState;
  progress: ProgressState;
  settings: GameSettings;
}

export interface PlayerState {
  id: string;
  name: string;
  class: 'warrior' | 'rogue' | 'mage';
  level: number;
  experience: number;
  health: number;
  maxHealth: number;
  gold: number;
  inventory: InventoryItem[];
  stats: PlayerStats;
}

export interface WorldState {
  currentLocation: string;
  visitedLocations: string[];
  completedQuests: string[];
  gameFlags: { [key: string]: any };
}

export interface ProgressState {
  playTime: number;
  saveCount: number;
  lastSaved: number;
  achievements: string[];
}

export interface GameSettings {
  volume: VolumeSettings;
  display: DisplaySettings;
  gameplay: GameplaySettings;
}

export interface VolumeSettings {
  master: number;
  music: number;
  effects: number;
}

export interface DisplaySettings {
  fullscreen: boolean;
  resolution: string;
  quality: 'low' | 'medium' | 'high';
}

export interface GameplaySettings {
  difficulty: 'easy' | 'normal' | 'hard';
  autoSave: boolean;
  hints: boolean;
}

// Plugin Types
export interface PluginContext {
  config: Config;
  services: ServiceRegistry;
  events: EventBus;
  logger: Logger;
}

export interface PluginMetadata {
  name: string;
  version: string;
  description: string;
  author: string;
  dependencies?: string[];
}

// Service Registry
export interface ServiceRegistry {
  register<T>(name: string, service: T): void;
  get<T>(name: string): T | null;
  has(name: string): boolean;
  list(): string[];
}

// Event Types
export interface GameEvent {
  type: string;
  timestamp: number;
  data: any;
}

export type EventHandler = (event: GameEvent) => void | Promise<void>;

// Error Types
export interface InitializationError {
  phase: InitPhase;
  message: string;
  recoverable: boolean;
  cause?: Error;
}

// Factory Types
export type Factory<T> = (container: DIContainer) => T | Promise<T>;
export type Token<T> = string | symbol;

// DI Container Interface
export interface DIContainer {
  register<T>(token: Token<T>, factory: Factory<T>): void;
  resolve<T>(token: Token<T>): T;
  resolveAsync<T>(token: Token<T>): Promise<T>;
  createScope(): DIContainer;
  has(token: Token<any>): boolean;
}

// Core Service Interfaces

export interface InitializationManager {
  initialize(): Promise<void>;
  validateEnvironment(): Promise<ValidationResult>;
  loadConfiguration(): Promise<Config>;
  setupServices(): Promise<void>;
  runHealthChecks(): Promise<HealthCheckResult>;
  getProgress(): InitializationProgress;
}

export interface InitializationProgress {
  phase: InitPhase;
  progress: number;
  message: string;
}

export interface ConfigurationService {
  loadConfig(source: ConfigSource): Promise<Config>;
  validateConfig(config: Config): ValidationResult;
  mergeConfigs(...configs: Config[]): Config;
  watchConfig(callback: ConfigChangeHandler): void;
  getConfig(): Config;
}

export type ConfigSource = 'default' | 'file' | 'env' | 'remote';
export type ConfigChangeHandler = (newConfig: Config, oldConfig: Config) => void;

export interface ResourceManager {
  loadAssets(manifest?: AssetManifest): Promise<AssetMap>;
  cacheAssets(assets: AssetMap): void;
  getAsset(id: string): Asset | null;
  preloadCritical(): Promise<void>;
  clearCache(): void;
  getLoadProgress(): number;
}

export interface AssetManifest {
  critical: string[];
  lazy: string[];
  optional: string[];
}

export interface GameStateService {
  initializeState(): GameState;
  loadSavedState(saveId: string): Promise<GameState>;
  saveState(state: GameState, saveId: string): Promise<void>;
  validateState(state: GameState): boolean;
  migrateState(state: GameState, fromVersion: string): GameState;
  listSaves(): Promise<SaveInfo[]>;
}

export interface SaveInfo {
  id: string;
  name: string;
  timestamp: number;
  playTime: number;
  level: number;
}

export interface StorageService {
  init(): Promise<void>;
  save(key: string, data: any): Promise<void>;
  load<T>(key: string): Promise<T | null>;
  delete(key: string): Promise<void>;
  clear(): Promise<void>;
  list(): Promise<string[]>;
  getSize(): Promise<number>;
}

export interface AudioService {
  initialize(): Promise<void>;
  preloadSounds(manifest: SoundManifest): Promise<void>;
  play(soundId: string, options?: PlayOptions): void;
  stop(soundId: string): void;
  setVolume(category: string, level: number): void;
  mute(muted: boolean): void;
}

export interface PlayOptions {
  loop?: boolean;
  volume?: number;
  fadeIn?: number;
}

export interface AnalyticsService {
  initialize(config: AnalyticsConfig): Promise<void>;
  trackEvent(event: GameEvent): void;
  trackError(error: Error, context?: any): void;
  trackTiming(category: string, variable: string, time: number): void;
  setUser(userId: string): void;
  flush(): Promise<void>;
}

export interface Logger {
  debug(message: string, context?: any): void;
  info(message: string, context?: any): void;
  warn(message: string, context?: any): void;
  error(message: string, error?: Error, context?: any): void;
  setLevel(level: LogLevel): void;
  addTransport(transport: LogTransport): void;
}

export interface LogTransport {
  name: string;
  log(level: LogLevel, message: string, context?: any): void;
}

export interface EventBus {
  emit(event: string, data?: any): void;
  on(event: string, handler: EventHandler): () => void;
  once(event: string, handler: EventHandler): void;
  off(event: string, handler: EventHandler): void;
  clear(event?: string): void;
}

export interface GamePlugin {
  metadata: PluginMetadata;
  initialize(context: PluginContext): Promise<void>;
  onGameStart?(): void | Promise<void>;
  onGameEnd?(): void | Promise<void>;
  onStateChange?(newState: GameState, oldState: GameState): void;
  destroy?(): void | Promise<void>;
}

export interface PluginManager {
  register(plugin: GamePlugin): void;
  unregister(pluginName: string): void;
  initialize(): Promise<void>;
  getPlugin(name: string): GamePlugin | null;
  listPlugins(): PluginMetadata[];
  isInitialized(name: string): boolean;
}

// Inventory Types (for completeness)
export interface InventoryItem {
  id: string;
  name: string;
  type: 'weapon' | 'armor' | 'consumable' | 'quest';
  quantity: number;
  equipped: boolean;
}

export interface PlayerStats {
  strength: number;
  agility: number;
  intelligence: number;
  vitality: number;
}