# -------- BASE --------
FROM python:3.11-slim AS base

WORKDIR /password_storage

ENV PYTHONUNBUFFERED=1

COPY req.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r req.txt

COPY core core
COPY shared shared

# -------- API --------
FROM base AS api

COPY app app
COPY main_app.py .
COPY scripts scripts
CMD ["bash", "-c", "python -m scripts.add_admins && python -m scripts.make_roles && uvicorn main_app:app --host 0.0.0.0 --port 8000"]


# -------- BOT --------
FROM base AS bot

COPY bot bot
COPY main_bot.py .

CMD ["python", "main_bot.py"]

# --------  MIGRATE --------
FROM base AS migrate
COPY alembic.ini .
COPY migrations migrations
COPY app/db app/db
CMD ["alembic", "upgrade", "head"]
