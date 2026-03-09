import requests

from utils.logger import logger


class Reranker:

    def __init__(self):

        self.model = "mistral"

        self.ollama_url = "http://localhost:11434/api/generate"

    # ==================================
    # SCORE CHUNK
    # ==================================

    def score_chunk(self, question, chunk):

        prompt = f"""
Оцени насколько текст помогает ответить на вопрос.

Вопрос:
{question}

Текст:
{chunk}

Ответь только числом от 0 до 10.
"""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(
            self.ollama_url,
            json=payload
        )

        text = response.json()["response"]

        try:
            score = float(text.strip())
        except:
            score = 0

        return score

    # ==================================
    # RERANK
    # ==================================

    def rerank(self, question, chunks):

        logger.info("Запуск reranker")

        scored = []

        for chunk in chunks:

            score = self.score_chunk(
                question,
                chunk["text"]
            )

            scored.append((score, chunk))

        scored.sort(
            key=lambda x: x[0],
            reverse=True
        )

        return [c for s, c in scored]