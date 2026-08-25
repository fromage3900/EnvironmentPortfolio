/**
 * Melodia Editorial Look-Book Initialization (TypeScript)
 */

export interface EditorialConfig {
  pageKey: string;
  intakeEnabled?: boolean;
  heroGridEnabled?: boolean;
}

export class MelodiaEditorialManager {
  private config: EditorialConfig;

  constructor(config: EditorialConfig) {
    this.config = config;
  }

  public init(): void {
    if (typeof document === 'undefined') return;
    const shell = document.querySelector('.melodia-shell');
    if (shell) {
      shell.setAttribute('data-ts-active', 'true');
    }
  }
}
