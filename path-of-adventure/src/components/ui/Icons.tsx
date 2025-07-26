import React from 'react';

interface IconProps {
  className?: string;
}

export const Heart: React.FC<IconProps> = ({ className = '' }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24">
    <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
  </svg>
);

export const Shield: React.FC<IconProps> = ({ className = '' }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24">
    <path d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1M12,7C13.4,7 14.8,8.6 14.8,10V11H16V16H8V11H9.2V10C9.2,8.6 10.6,7 12,7M12,8.2C11.2,8.2 10.4,8.7 10.4,10V11H13.6V10C13.6,8.7 12.8,8.2 12,8.2Z"/>
  </svg>
);

export const Sword: React.FC<IconProps> = ({ className = '' }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24">
    <path d="M6.92,5H5L6.5,6.5L10.9,10.9L9.17,12.63L3.71,7.17L2.29,8.58L7.75,14.04L6.04,15.75L5.33,15.04L4.62,15.75L7.75,18.88L8.46,18.17L7.75,17.46L9.46,15.75L15.96,22.25L17.38,20.83L11.92,15.38L13.63,13.67L18.04,18.08L19.46,16.67L14,11.21L18.5,6.71L16.8,5H15.92L12.21,8.71L11.5,8L6.92,5M16.5,5V6.5L12,11L11,10L15.5,5.5H16.5Z"/>
  </svg>
);

export const Boot: React.FC<IconProps> = ({ className = '' }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24">
    <path d="M5 5V18L7 19L12 15L13 16L19 15V9C19 7.9 18.1 7 17 7H12V5H5M7 9H17V13H7V9Z"/>
  </svg>
);

export const Diamond: React.FC<IconProps> = ({ className = '' }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24">
    <path d="M6,2L2,8L12,22L22,8L18,2H6M6.5,4H9.5L11,7L8.5,7L6.5,4M10.5,9L12,11.5L13.5,9H10.5M12,13.5L8,9H16L12,13.5M17.5,7L15.5,7L14.5,4H17.5L17.5,7Z"/>
  </svg>
);

export const Potion: React.FC<IconProps> = ({ className = '' }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24">
    <path d="M5 5.5C5 4.119 6.119 3 7.5 3S10 4.119 10 5.5V7.257C10.581 7.604 11 8.257 11 9C11 10.105 10.105 11 9 11H8V21C8 21.552 7.552 22 7 22H6C5.448 22 5 21.552 5 21V11H4C2.895 11 2 10.105 2 9C2 8.257 2.419 7.604 3 7.257V5.5C3 4.119 4.119 3 5.5 3S8 4.119 8 5.5"/>
  </svg>
);

export const Scroll: React.FC<IconProps> = ({ className = '' }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24">
    <path d="M19,19V5L15,5V19L19,19M13,5H11V19H13V5M9,19V5L5,19H9M3,3H21V21H3V3Z"/>
  </svg>
);

export const Bag: React.FC<IconProps> = ({ className = '' }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24">
    <path d="M12,2A3,3 0 0,1 15,5V7H19A1,1 0 0,1 20,8V19A3,3 0 0,1 17,22H7A3,3 0 0,1 4,19V8A1,1 0 0,1 5,7H9V5A3,3 0 0,1 12,2M12,4A1,1 0 0,0 11,5V7H13V5A1,1 0 0,0 12,4M6,9V19A1,1 0 0,0 7,20H17A1,1 0 0,0 18,19V9H6Z"/>
  </svg>
);

export const Settings: React.FC<IconProps> = ({ className = '' }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24">
    <path d="M12,15.5A3.5,3.5 0 0,1 8.5,12A3.5,3.5 0 0,1 12,8.5A3.5,3.5 0 0,1 15.5,12A3.5,3.5 0 0,1 12,15.5M19.43,12.97C19.47,12.65 19.5,12.33 19.5,12C19.5,11.67 19.47,11.34 19.43,11L21.54,9.37C21.73,9.22 21.78,8.95 21.66,8.73L19.66,5.27C19.54,5.05 19.27,4.96 19.05,5.05L16.56,6.05C16.04,5.66 15.5,5.32 14.87,5.07L14.5,2.42C14.46,2.18 14.25,2 14,2H10C9.75,2 9.54,2.18 9.5,2.42L9.13,5.07C8.5,5.32 7.96,5.66 7.44,6.05L4.95,5.05C4.73,4.96 4.46,5.05 4.34,5.27L2.34,8.73C2.22,8.95 2.27,9.22 2.46,9.37L4.57,11C4.53,11.34 4.5,11.67 4.5,12C4.5,12.33 4.53,12.65 4.57,12.97L2.46,14.63C2.27,14.78 2.22,15.05 2.34,15.27L4.34,18.73C4.46,18.95 4.73,19.03 4.95,18.95L7.44,17.94C7.96,18.34 8.5,18.68 9.13,18.93L9.5,21.58C9.54,21.82 9.75,22 10,22H14C14.25,22 14.46,21.82 14.5,21.58L14.87,18.93C15.5,18.68 16.04,18.34 16.56,17.94L19.05,18.95C19.27,19.03 19.54,18.95 19.66,18.73L21.66,15.27C21.78,15.05 21.73,14.78 21.54,14.63L19.43,12.97Z"/>
  </svg>
);

export const Quest: React.FC<IconProps> = ({ className = '' }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24">
    <path d="M12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,17A1.5,1.5 0 0,1 10.5,15.5A1.5,1.5 0 0,1 12,14A1.5,1.5 0 0,1 13.5,15.5A1.5,1.5 0 0,1 12,17M12,10.5C10.07,10.5 8.5,8.93 8.5,7C8.5,5.07 10.07,3.5 12,3.5C13.93,3.5 15.5,5.07 15.5,7C15.5,8.93 13.93,10.5 12,10.5Z"/>
  </svg>
);

export const Character: React.FC<IconProps> = ({ className = '' }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24">
    <path d="M12,4A4,4 0 0,1 16,8A4,4 0 0,1 12,12A4,4 0 0,1 8,8A4,4 0 0,1 12,4M12,14C16.42,14 20,15.79 20,18V20H4V18C4,15.79 7.58,14 12,14Z"/>
  </svg>
);

export const Poison: React.FC<IconProps> = ({ className = '' }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24">
    <path d="M7,2V4H9V2.5C9,2.22 9.22,2 9.5,2H14.5C14.78,2 15,2.22 15,2.5V4H17V2C17,0.89 16.1,0 15,0H9C7.89,0 7,0.89 7,2M16,8C17.1,8 18,8.9 18,10V22C18,23.1 17.1,24 16,24H8C6.9,24 6,23.1 6,22V10C6,8.9 6.9,8 8,8H16M8,10V22H16V10H8M12,16L10,12H14L12,16Z"/>
  </svg>
);

export const Buff: React.FC<IconProps> = ({ className = '' }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24">
    <path d="M12,2L13.09,8.26L22,9L14.74,16.82L17,24L12,20L7,24L9.26,16.82L2,9L10.91,8.26L12,2Z"/>
  </svg>
);

export const Frozen: React.FC<IconProps> = ({ className = '' }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24">
    <path d="M12,11L14,9V5.5L16.5,8L18,6.5L14,2.5L12,4.5L10,2.5L6,6.5L7.5,8L10,5.5V9L12,11M11,13L9,15L5.5,12.5L4,14L8,18L10,16L12,18L14,16L18,20L19.5,18.5L17,16L19,14L13,11H11M15,8.5L16,7.5L18,9.5L17,10.5L15,8.5M8,7.5L9,8.5L7,10.5L6,9.5L8,7.5Z"/>
  </svg>
);

export const Burning: React.FC<IconProps> = ({ className = '' }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24">
    <path d="M17.66,11.2C17.43,10.9 17.15,10.64 16.89,10.38C16.22,9.78 15.46,9.35 14.82,8.72C13.33,7.26 13,4.85 13.95,3C13.79,3.23 13.64,3.5 13.5,3.75C13.5,4.75 13.5,5.85 13.5,6.75C13.5,8.5 14.5,9.5 15.5,10.5C15.89,10.89 16.2,11.3 16.5,11.75C16.73,12.1 16.86,12.5 16.9,12.9C16.93,13.27 16.9,13.64 16.81,14C16.65,14.64 16.31,15.26 15.81,15.75C15.09,16.5 14.09,16.9 13.09,16.9C11.74,16.9 10.5,16.11 9.89,14.89C9.59,14.32 9.5,13.66 9.5,13C9.5,12.25 9.62,11.5 9.81,10.78C10.1,9.66 10.65,8.64 11.31,7.78C11.81,7.11 12.41,6.5 13.11,6C12.4,6.16 11.7,6.5 11.1,6.9C10.5,7.35 9.96,7.9 9.5,8.5C8.5,9.75 8,11.25 8,12.75C8,13.5 8.17,14.25 8.5,14.9C9.27,16.5 10.89,17.75 12.79,17.9C14.89,18.1 16.8,16.9 17.66,15C18.17,14 18.26,12.8 17.66,11.2Z"/>
  </svg>
);

// Default export for backward compatibility
export default {
  Heart,
  Shield,
  Sword,
  Boot,
  Diamond,
  Potion,
  Scroll,
  Bag,
  Settings,
  Quest,
  Character,
  Poison,
  Buff,
  Frozen,
  Burning
};