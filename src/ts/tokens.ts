/**
 * Melodia Design System Tokens Interface (TypeScript)
 */

export interface MelodiaTokenPalette {
  primaryGold: string;
  ivoryBase: string;
  plumDeep: string;
  lavenderSoft: string;
  sakuraRose: string;
  astralNight: string;
  irisPurple: string;
}

export const MELODIA_TOKENS: MelodiaTokenPalette = {
  primaryGold: 'var(--primitive-gold-500)',
  ivoryBase: 'var(--primitive-ivory-100)',
  plumDeep: 'var(--primitive-plum-900)',
  lavenderSoft: 'var(--primitive-lavender-100)',
  sakuraRose: 'var(--primitive-sakura-300)',
  astralNight: 'var(--primitive-astral-900)',
  irisPurple: 'var(--primitive-iris-500)',
};

export interface SpacingScale {
  space4: string;
  space8: string;
  space16: string;
  space24: string;
  space32: string;
  space48: string;
  space64: string;
  space96: string;
  space128: string;
}

export const MELODIA_SPACING: SpacingScale = {
  space4: '4px',
  space8: '8px',
  space16: '16px',
  space24: '24px',
  space32: '32px',
  space48: '48px',
  space64: '64px',
  space96: '96px',
  space128: '128px',
};
