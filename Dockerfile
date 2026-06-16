FROM python:3.12-slim

WORKDIR /app

ENV PIP_DEFAULT_TIMEOUT=120 \
    PIP_RETRIES=10 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY requirements.txt .

# Install in two layers — smaller downloads per step, better cache on retry
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
      fastapi sqlalchemy psycopg2-binary alembic pydantic-settings python-dotenv redis kafka-python

RUN pip install --no-cache-dir uvicorn

COPY . .

RUN chmod +x /app/scripts/start.sh

EXPOSE 8000

CMD ["/app/scripts/start.sh"]
