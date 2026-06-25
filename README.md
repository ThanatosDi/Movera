# Movera

<p align="center">
  <strong>輕量級媒體檔案自動化管理工具</strong>
</p>

<p align="center">
  <a href="https://github.com/ThanatosDi/Movera/actions"><img src="https://github.com/ThanatosDi/Movera/actions/workflows/tests.yaml/badge.svg" alt="Tests" /></a>
  <a href="https://hub.docker.com/r/thanatosdi/movera"><img src="https://img.shields.io/docker/v/thanatosdi/movera?sort=semver&label=Docker" alt="Docker" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/ThanatosDi/Movera" alt="License" /></a>
</p>

Movera 整合多種 BT 下載器（qBittorrent、Transmission、Deluge、rTorrent、Aria2），當下載完成時自動依據預設的任務規則移動與重新命名檔案。

## 功能特色

- **多種 BT 下載器整合** — 支援 qBittorrent、Transmission、Deluge、rTorrent、Aria2
- **靈活的重命名規則** — 支援 Regex 和 Parse 兩種模式，即時預覽結果
- **預設規則** — 可建立常用的重命名模式，快速套用到任務
- **任務管理系統** — 建立、編輯、啟用/停用任務，批量操作（單次最多 100 筆）
- **標籤分類** — 彩色標籤管理，快速分類任務
- **即時日誌** — 透過 WebSocket 即時查看處理狀態
- **現代化 Web UI** — Vue 3 + Tailwind CSS 響應式界面，支援手機版面
- **多語系** — 繁體中文、English
- **PWA 支援** — 可安裝為桌面/行動應用程式
- **Docker 部署** — 支援 amd64 和 arm64 架構

## 快速開始

### Docker

```bash
docker run -d \
  --name movera \
  -p 8000:8000 \
  -e PUID=1000 \
  -e PGID=1000 \
  -v /path/to/downloads:/downloads \
  -v /path/to/media:/media \
  -v /path/to/database:/movera/database \
  -v /path/to/storages:/movera/storages \
  thanatosdi/movera:latest
```

### Docker Compose（推薦）

```yaml
services:
  movera:
    image: thanatosdi/movera:latest
    container_name: movera
    ports:
      - "8000:8000"
    environment:
      - PUID=1000
      - PGID=1000
    volumes:
      - /path/to/downloads:/downloads
      - /path/to/media:/media
      - ./database:/movera/database
      - ./storages:/movera/storages
    restart: unless-stopped
```

### 環境變數

| 變數                         | 預設值        | 說明                                            |
| ---------------------------- | ------------- | ----------------------------------------------- |
| `PUID`                       | `1000`        | 執行程式的使用者 ID                             |
| `PGID`                       | `1000`        | 執行程式的群組 ID                               |
| `ENV`                        | `production`  | 環境模式（`development` 開啟 API 文件）         |
| `ALLOWED_DIRECTORIES`        | —             | 目錄瀏覽器允許的路徑，逗號分隔（如 `/downloads,/media`） |
| `ALLOWED_SOURCE_DIRECTORIES` | —             | Webhook 來源檔案路徑白名單，逗號分隔            |
| `ALLOW_WEBUI_SETTING`        | `true`        | 是否允許透過 Web UI 修改目錄設定                |
| `MOVERA_SECRET_KEY`          | 自動產生      | JWT 簽章用的 HMAC secret，未設定時首次啟動自動產生並持久化 |
| `MOVERA_ADMIN_USERNAME`      | —             | 預設管理員帳號，資料庫無帳號時於首次啟動建立    |
| `MOVERA_ADMIN_PASSWORD`      | —             | 預設管理員密碼，需與 `MOVERA_ADMIN_USERNAME` 同時設定 |

### Volume 說明

| 路徑               | 說明                       |
| ------------------ | -------------------------- |
| `/downloads`       | 下載器的下載目錄           |
| `/media`           | 媒體檔案的目標目錄         |
| `/movera/database` | SQLite 資料庫持久化        |
| `/movera/storages` | 應用程式設定與儲存空間     |

## 身分驗證與安全

Movera 內建兩道分離的驗證機制：

### 管理 API 與 Web UI 登入

- 所有 `/api/v1/*` 管理 API 都需要登入後取得的 JWT 憑證。
- 首次啟動：
  - 若設定了 `MOVERA_ADMIN_USERNAME` 與 `MOVERA_ADMIN_PASSWORD`，會自動建立管理員帳號。
  - 否則開啟 Web UI 時會進入「初始化設定」頁，手動建立第一組帳密。
- 密碼於前端先以 SHA-256 雜湊再傳送，後端加 salt 後存於 SQLite，不保存明文。
- JWT 以 `MOVERA_SECRET_KEY` 簽發（有效期 12 小時）；變更或清除 secret 會使所有既發憑證失效，可作為緊急撤銷手段。

> [!IMPORTANT]
> 前端 SHA-256 僅避免明文密碼於網路傳輸，**不能取代傳輸層加密**。請務必將 Movera 部署於 HTTPS 反向代理之後。

### Webhook Token

- `/webhook/*` 端點採「相容式」驗證：**尚未建立任何 token 前維持開放**，不影響既有下載器腳本。
- 於設定頁建立第一個 webhook token 後，所有 webhook 請求都必須帶上 `Authorization: Bearer movera_...`，否則回應 401。
- Token 開頭為 `movera_`，僅於建立當下顯示一次（資料庫只存雜湊）；可隨時新增、命名與撤銷。

啟用 webhook token 後，需在下載器呼叫中加上 Authorization 標頭，例如 qBittorrent：

```bash
/path/to/scripts/qBittorrent http://movera:8000/webhook/qbittorrent/on-complete "%F" "%L" "%G" --header "Authorization: Bearer movera_你的token"
```

> [!NOTE]
> 請依各下載器腳本的參數格式調整帶入 Authorization 標頭的方式。

## BT 下載器整合

將 `scripts/` 目錄下的腳本複製到下載器可存取的位置，並設定下載完成時執行。

| 下載器       | 測試狀態 |
| ------------ | -------- |
| qBittorrent  | ✅        |
| Transmission | ⚠️        |
| Deluge       | ⚠️        |
| rTorrent     | ⚠️        |
| Aria2        | ⚠️        |

### qBittorrent

設定 → **下載** → **種子完成時執行外部程式**：

```bash
/path/to/scripts/qBittorrent http://movera:8000/webhook/qbittorrent/on-complete "%F" "%L" "%G"
```

### Transmission

編輯 `settings.json`：

```json
{
  "script-torrent-done-enabled": true,
  "script-torrent-done-filename": "/path/to/scripts/Transmission http://movera:8000/webhook/on-complete"
}
```

### Deluge

1. 啟用 Execute 插件：**Preferences** → **Plugins** → **Execute**
2. 新增事件：**Torrent Complete**
3. Command：

```bash
/path/to/scripts/Deluge http://movera:8000/webhook/on-complete
```

### rTorrent

在 `.rtorrent.rc` 中加入：

```bash
method.set_key = event.download.finished,movera,"execute2={/path/to/scripts/rTorrent,http://movera:8000/webhook/on-complete,$d.base_path=,$d.custom1=}"
```

### Aria2

啟動參數或 `aria2.conf`：

```bash
on-download-complete=/path/to/scripts/Aria2 http://movera:8000/webhook/on-complete
```

> [!NOTE]
> 所有腳本都在 `scripts/` 目錄下，請根據你的環境修改 URL 和路徑。

## 任務規則

### Parse 模式

使用命名佔位符來解析檔名：

| 來源模式 | `{title} - {episode}.mp4`         |
| -------- | --------------------------------- |
| 輸入檔名 | `公爵千金的家庭教師 - 01.mp4`     |
| 目標模式 | `{title} - S01E{episode}.mp4`     |
| 輸出檔名 | `公爵千金的家庭教師 - S01E01.mp4` |

### Regex 模式

使用正規表達式和反向引用：

| 來源模式 | `(.+) - (\d{2}).+\.mp4`               |
| -------- | ------------------------------------- |
| 輸入檔名 | `公爵千金的家庭教師 - 01 [1080P].mp4` |
| 目標模式 | `\1 - S01E\2.mp4`                     |
| 輸出檔名 | `公爵千金的家庭教師 - S01E01.mp4`     |

也支援命名群組：

| 來源模式 | `(?P<title>\w+) - (?P<episode>\d{2})(v2)? (.+)\.mp4` |
| -------- | ---------------------------------------------------- |
| 輸入檔名 | `公爵千金的家庭教師 - 01 [1080P].mp4`                |
| 目標模式 | `\g<title> - S01E\g<episode> \4.mp4`                 |
| 輸出檔名 | `公爵千金的家庭教師 - S01E01 [1080P].mp4`            |

## 本地開發

### 系統需求

- Python 3.13+
- Node.js 22+
- [uv](https://github.com/astral-sh/uv)（Python 套件管理）

### 後端

```bash
# 安裝依賴
uv sync

# 啟動開發伺服器
uv run main.py
```

### 前端

```bash
# 安裝依賴
npm install

# 啟動開發伺服器
npm run dev

# 型別檢查 + 建置生產版本
npm run build
```

> [!NOTE]
> 開發時前後端使用不同 Port，可在根目錄建立 `.env` 設定 `VITE_WEBSOCKET_BASE_URL` 來指定 WebSocket 伺服器（後端）的 URL。

### 測試

```bash
# 前端測試
npm run test:run

# 後端測試
uv run pytest tests/backend/ -v
```

## API 文件

啟動伺服器後，設定環境變數 `ENV=development` 即可存取 API 文件：

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

> [!NOTE]
> 預設 production 模式不開放 API 文件。

## 技術棧

### 後端

- [FastAPI](https://fastapi.tiangolo.com/) — Python Web 框架
- [SQLAlchemy 2](https://www.sqlalchemy.org/) — ORM
- [Alembic](https://alembic.sqlalchemy.org/) — 資料庫遷移
- [Uvicorn](https://www.uvicorn.org/) — ASGI 伺服器
- [Pydantic v2](https://docs.pydantic.dev/) — 資料驗證
- [Loguru](https://github.com/Delgan/loguru) — 日誌

### 前端

- [Vue 3](https://vuejs.org/) — Composition API
- [Tailwind CSS 4](https://tailwindcss.com/) — CSS 框架
- [Pinia](https://pinia.vuejs.org/) — 狀態管理
- [Vue Router](https://router.vuejs.org/) — 路由
- [Vue I18n](https://vue-i18n.intlify.dev/) — 國際化
- [Reka UI](https://reka-ui.com/) — 無障礙 UI 元件
- [Vitest](https://vitest.dev/) — 測試框架

## 授權條款

[MIT License](LICENSE)
