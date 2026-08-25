/**
 * Melodia Game UI Judgment & Rhythm Highway Interface (TypeScript)
 */

export type RhythmJudgement = 'PERFECT' | 'GREAT' | 'GOOD' | 'MISS';

export interface JudgementResult {
  tier: RhythmJudgement;
  damageMultiplier: number;
  timeOffsetMs: number;
  feedbackText: string;
}

export class MelodiaRhythmEngine {
  public static evaluateHit(timeOffsetMs: number): JudgementResult {
    const absOffset = Math.abs(timeOffsetMs);
    if (absOffset <= 40) {
      return { tier: 'PERFECT', damageMultiplier: 1.25, timeOffsetMs, feedbackText: 'Perfect!' };
    } else if (absOffset <= 80) {
      return { tier: 'GREAT', damageMultiplier: 1.15, timeOffsetMs, feedbackText: 'Great' };
    } else if (absOffset <= 140) {
      return { tier: 'GOOD', damageMultiplier: 1.10, timeOffsetMs, feedbackText: 'Good' };
    } else {
      return { tier: 'MISS', damageMultiplier: 1.00, timeOffsetMs, feedbackText: 'Miss' };
    }
  }
}
