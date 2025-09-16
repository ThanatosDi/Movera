FROM node:22-trixie-slim AS builder

WORKDIR /src

COPY ./src ./src

COPY ./public ./public

COPY package.json vite.config.ts tsconfig.json tsconfig.node.json tsconfig.app.json index.html  ./

RUN npm install

RUN npm run build

FROM python:3.13-slim-trixie

EXPOSE 8000
WORKDIR /movera

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY --from=builder /src/dist /movera/dist
COPY . /movera

RUN uv sync --locked

CMD ["uv", "run", "main.py"]