FROM node:24-trixie-slim AS builder

WORKDIR /src

COPY ./src ./src
COPY ./public ./public
COPY package.json vite.config.ts tsconfig.json tsconfig.node.json tsconfig.app.json index.html  ./

RUN npm install
RUN npm run build


FROM python:3.13-slim-trixie

EXPOSE 8000
WORKDIR /movera

# 安裝 gosu，它是 Debian/Ubuntu 上安全的權限切換工具
# 並清理 apt 快取以保持鏡像大小
RUN apt-get update && \
    apt-get install -y --no-install-recommends gosu && \
    rm -rf /var/lib/apt/lists/*

# 複製 entrypoint 腳本到鏡像中
COPY ./entrypoint.sh /usr/local/bin/
# 賦予它執行權限
RUN chmod +x /usr/local/bin/entrypoint.sh

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 先複製專案檔案，再複製 build 產物，避免被覆蓋
COPY . /movera
COPY --from=builder /src/dist /movera/dist

RUN uv sync --locked

# 設定 entrypoint，容器啟動時會先執行此腳本
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# CMD 會作為參數傳遞給 ENTRYPOINT
CMD ["uv", "run", "main.py"]