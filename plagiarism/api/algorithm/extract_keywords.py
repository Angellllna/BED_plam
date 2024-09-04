import abc

from api.algorithm.imports import *

client = OpenAI(api_key=KEY_OPENAI)


class IExtractKeywords(abc.ABC):
    @abc.abstractmethod
    def extract_keywords(
        self,
        text: str,
        language: str,
    ) -> list[str]:
        pass


def format_search_query(text):
    lines = text.strip().split("\n")
    keywords = [line.split(". ", 1)[-1] for line in lines]
    result = " OR ".join(keywords)
    return result


def perform_ai_query(prompt, model):
    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    results = []
    try:
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                results.append(chunk.choices[0].delta.content)
        return format_search_query("".join(results))
    except Exception as e:
        logging.error(f"An error occurred during AI streaming: {e}")
        return None


class ExtractKeywords(IExtractKeywords):
    def __init__(self, model="gpt-4-turbo"):
        self.model = model

    def extract_keywords(self, text: str, language: str) -> list[str]:
        prompt = {
            "uk": f"Згенеруй 3 пошукових фраз які є загальною темою, яка складається з 4-6 слів, яку можна використовувати для пошуку статей, пов’язаних з наступним текстом: {text}",
            "en": f"Generate 3 search phrases that are a general topic consisting of 4-6 words that can be used to find articles related to the following text: {text}",
        }

        if language not in prompt:
            logging.error(f"Unsupported language: {language}")
            return None

        return perform_ai_query(prompt[language], self.model)
