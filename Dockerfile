FROM node:24-trixie-slim AS builder

WORKDIR /src

COPY ./src ./src
COPY ./public ./public
COPY package.json package-lock.json vite.config.ts tsconfig.json tsconfig.node.json tsconfig.app.json index.html ./

RUN npm ci
RUN npm run build


FROM python:3.14-slim-trixie

EXPOSE 8000
WORKDIR /movera

# 降權工具使用 setpriv（util-linux，base image 已內建，無需額外安裝）
# 不使用 gosu：Debian 的 gosu 為靜態連結 Go 執行檔，會把整份 Go 標準庫
# 的已知 CVE 帶進鏡像（實際不可利用，但掃描結果難以維護）

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
