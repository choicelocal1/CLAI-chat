version: '3.8'

services:
  api:
    build:
      context: ./api
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      - FLASK_APP=app.py
      - FLASK_ENV=development
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/clai_chat
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=local-dev-secret
      - JWT_SECRET_KEY=local-dev-jwt-secret
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./api/src:/app
    depends_on:
      - db
      - redis

  db:
    image: postgres:13
    environment:
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=clai_chat
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6
    ports:
      - "6379:6379"

volumes:
  postgres_data:
