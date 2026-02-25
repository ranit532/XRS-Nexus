"""
Chatbot Agent: Provides conversational interface to query lineage, quality, and structure.
"""
from langchain.chains import ConversationChain
from langchain.llms import Ollama

class ChatbotAgent:
    def __init__(self, model="llama2"):
        self.llm = Ollama(model=model)
        self.conversation = ConversationChain(llm=self.llm)

    def chat(self, message):
        return self.conversation.run(message)
