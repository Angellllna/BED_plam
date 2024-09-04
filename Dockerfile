FROM python:3.10-slim


WORKDIR /app-bed

COPY pyproject.toml .

RUN pip install poetry
RUN poetry install
RUN poetry run spacy download en_core_web_sm
RUN poetry run spacy download uk_core_news_sm

COPY plagiarism /app-bed/

RUN poetry run python api/algorithm/donloads.py
EXPOSE 8000

CMD ["poetry", "run", "python", "manage.py", "runserver"]
