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

# 安裝 gosu，它是 Debian/Ubuntu 上安全的權限切換工具
# 並清理 apt 快取以保持鏡像大小
RUN apt-get update && \
    apt-get install -y --no-install-recommends gosu && \
    rm -rf /var/lib/apt/lists/*

# 設定你要的 gosu 版本
ENV GOSU_VERSION=1.19

RUN set -eux; \
# save list of currently installed packages for later so we can clean up
	savedAptMark="$(apt-mark showmanual)"; \
	apt-get install --update -y --no-install-recommends ca-certificates gnupg wget; \
	\
	dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')"; \
	wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch"; \
	wget -O /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch.asc"; \
	\
# verify the signature
	export GNUPGHOME="$(mktemp -d)"; \
	gpg --batch --keyserver hkps://keys.openpgp.org --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4; \
	gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu; \
	gpgconf --kill all; \
	rm -rf "$GNUPGHOME" /usr/local/bin/gosu.asc; \
	\
# clean up fetch dependencies
	apt-mark auto '.*' > /dev/null; \
	[ -z "$savedAptMark" ] || apt-mark manual $savedAptMark; \
	apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false; \
	apt-get dist-clean; \
	\
	chmod +x /usr/local/bin/gosu;

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
