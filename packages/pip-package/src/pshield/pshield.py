class PromptShield:
    def __init__(self, config):
        self.config = config

    def protect(self, prompt):
        protected_prompt = f"[Protected] {prompt}"
        return protected_prompt