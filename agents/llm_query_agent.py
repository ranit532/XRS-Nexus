"""
LLM Query Agent: Handles prompts to Ollama via LangChain for simulation, structure creation, and data population.
"""
from langchain.llms import Ollama

class LLMQueryAgent:
    def __init__(self, model="llama2"):
        self.llm = Ollama(model=model)

    def prompt(self, text):
        return self.llm(text)
