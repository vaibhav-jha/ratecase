from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI


class CustomLLM:
    models = {'gpt4': 'gpt-4-1106-preview', 'claude3': 'claude-3-haiku-20240307', 'gpt3': 'gpt-3.5-turbo-0125'}
    top_models = {'claude3': 'claude-3-opus-20240229', 'gpt4': 'gpt-4-1106-preview', 'gpt3': 'gpt-3.5-turbo-0125'}

    def show_available_models(self):
        return self.models

    def top_tier_models(self):
        return self.top_models

    def get_llm(self, option='gpt4', top=False, temperature=0.01):
        if option not in self.models.keys():
            raise ValueError(f"{option} not valid")

        if 'claude3' in option:
            model = self.models[option] if not top else self.top_models[option]
            return ChatAnthropic(model=model, temperature=temperature)
        if 'gpt4' in option:
            model = self.models[option] if not top else self.top_models[option]
            return ChatOpenAI(model=model, temperature=temperature)

        model = self.models['gpt3']
        return ChatOpenAI(model=model, temperature=temperature)
