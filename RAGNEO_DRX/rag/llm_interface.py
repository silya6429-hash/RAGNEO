import requests

from utils.logger import logger


class LLMInterface:
    """
    Интерфейс для общения с LLM через Ollama
    """

    def __init__(self):

        self.model = "mistral"

        self.ollama_url = "http://localhost:11434/api/generate"

    # ==================================
    # PROMPT BUILDER
    # ==================================

    def build_prompt(self, question: str, context: str):

        prompt = f"""
Ты помощник по документации.

Используй только информацию из контекста.

Если ответа нет в контексте — скажи что информации недостаточно.

КОНТЕКСТ:
{context}

ВОПРОС:
{question}

ОТВЕТ:
"""

        return prompt

    # ==================================
    # GENERATE ANSWER
    # ==================================

    def generate(self, question: str, context: str):

        prompt = self.build_prompt(question, context)

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        logger.info("Отправка запроса в Ollama")

        response = requests.post(
            self.ollama_url,
            json=payload
        )

        if response.status_code != 200:
            raise Exception(response.text)

        data = response.json()

        return data["response"]