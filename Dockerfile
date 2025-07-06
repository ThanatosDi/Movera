FROM python:3.13-alpine3.22

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY . /src

WORKDIR /src
RUN uv sync --locked

CMD [".venv/bin/python", "main.py"]