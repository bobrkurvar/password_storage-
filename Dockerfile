FROM python:3.11-slim AS base
WORKDIR /password_storage
COPY req.txt .
RUN pip install --no-cache-dir -r req.txt
COPY core core
COPY shared shared

FROM base AS app
COPY app app
COPY main_app.py .
CMD ["uvicorn", "main_app:app", "--host", "0.0.0.0", "--port", "8000"]


FROM base AS bot
COPY bot bot
COPY main_bot.py .
CMD ["python", "main_bot.py"]


FROM base AS migrate
COPY alembic.ini .
COPY migrations migrations
COPY app/db app/db
CMD ["alembic", "upgrade", "head"]

FROM base AS runner
COPY app/adapters app/adapters
COPY app/domain app/domain
COPY app/infra/security.py app/infra/security.py
COPY app/db app/db
COPY scripts/add_admins.py .
COPY scripts/make_roles.py .
CMD ["sh", "-c", "python -m make_roles && python -m add_admins"]

