export class PromptShield {
  constructor(config) {
    this.config = config;
  }

  protect(prompt) {
    return `[Protected] ${prompt}`;
  }
}
