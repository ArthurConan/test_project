FROM python:3.9.6-slim

EXPOSE 8000

WORKDIR /app

# Common code
COPY . .

RUN pip install pipenv && \
  pipenv install --system --deploy --skip-lock


CMD uvicorn --workers 16 main:app --host 0.0.0.0 --port 8000