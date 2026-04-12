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
- **常用規則管理** — 建立可重複使用的命名規則，在任務中快速套用
- **任務管理系統** — 建立、編輯、啟用/停用任務，批量操作
- **標籤分類** — 彩色標籤管理，快速分類任務
- **即時日誌** — 透過 WebSocket 即時查看處理狀態
- **API Key 認證** — 可選的 API Key 認證機制，保護 API 端點
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
      # - MOVERA_API_KEY=your-secret-key    # 啟用 API Key 認證（可選）
      # - MOVERA_ENABLE_DOCS=true           # 啟用 Swagger UI（可選）
    volumes:
      - /path/to/downloads:/downloads
      - /path/to/media:/media
      - ./database:/movera/database
      - ./storages:/movera/storages
    restart: unless-stopped
```

### 環境變數

| 變數                   | 預設值 | 說明                                                       |
| ---------------------- | ------ | ---------------------------------------------------------- |
| `PUID`                 | `1000` | 執行程式的使用者 ID                                        |
| `PGID`                 | `1000` | 執行程式的群組 ID                                          |
| `MOVERA_API_KEY`       | （空） | API Key 認證金鑰。設定後所有 API 與 Webhook 端點需要認證   |
| `MOVERA_ENABLE_DOCS`   | `false`| 設為 `true` 啟用 Swagger UI (`/docs`) 與 ReDoc (`/redoc`)  |
| `SQLITE_PATH`          | `./database/database.db` | SQLite 資料庫檔案路徑                        |

### Volume 說明

| 路徑               | 說明                       |
| ------------------ | -------------------------- |
| `/downloads`       | 下載器的下載目錄           |
| `/media`           | 媒體檔案的目標目錄         |
| `/movera/database` | SQLite 資料庫持久化        |
| `/movera/storages` | 應用程式設定與儲存空間     |

## API Key 認證

Movera 支援可選的 API Key 認證機制。設定 `MOVERA_API_KEY` 環境變數後，所有 `/api/*` 和 `/webhook/*` 端點都需要提供有效的 API Key。

### 認證方式

請求時在 header 中附帶 API Key，支援以下兩種方式：

```bash
# 方式一：Authorization Bearer
curl -H "Authorization: Bearer your-secret-key" http://localhost:8000/api/v1/tasks

# 方式二：X-API-Key header
curl -H "X-API-Key: your-secret-key" http://localhost:8000/api/v1/tasks
```

### 前端配置

前端會在啟動時透過 `/runtime-config.js` 自動從後端讀取 `MOVERA_API_KEY`，不需額外設定。只要在 Docker Compose 的 `environment` 中設定即可，前後端共用同一個環境變數。

### BT 下載器腳本配置

啟用認證後，需在下載器腳本中加入 API Key header。以 qBittorrent 為例：

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key" \
  -d '{"filepath": "%F"}' \
  http://movera:8000/webhook/qbittorrent/on-complete
```

> [!NOTE]
> 未設定 `MOVERA_API_KEY` 時認證關閉，所有請求不需認證即可存取（向下相容）。

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
/path/to/scripts/qBittorrent http://movera:8000/webhook/qbittorrent "%F" "%L" "%G"
```

### Transmission

編輯 `settings.json`：

```json
{
  "script-torrent-done-enabled": true,
  "script-torrent-done-filename": "/path/to/scripts/Transmission http://movera:8000/webhook/qbittorrent"
}
```

### Deluge

1. 啟用 Execute 插件：**Preferences** → **Plugins** → **Execute**
2. 新增事件：**Torrent Complete**
3. Command：

```bash
/path/to/scripts/Deluge http://movera:8000/webhook/qbittorrent
```

### rTorrent

在 `.rtorrent.rc` 中加入：

```bash
method.set_key = event.download.finished,movera,"execute2={/path/to/scripts/rTorrent,http://movera:8000/webhook/qbittorrent,$d.base_path=,$d.custom1=}"
```

### Aria2

啟動參數或 `aria2.conf`：

```bash
on-download-complete=/path/to/scripts/Aria2 http://movera:8000/webhook/qbittorrent
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

### 常用規則

在 **設定頁面** 可建立常用的重命名規則（Parse 或 Regex），之後在建立/編輯任務時，透過「套用常用規則」按鈕快速填入來源或目標欄位的 pattern，省去重複輸入。

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

# 啟用 API Key 認證（可選）
MOVERA_API_KEY=your-secret-key uv run main.py

# 或透過 .env 檔案載入環境變數
uv run --env-file=.env main.py
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

### 本地測試 API Key 認證

前端透過 `/runtime-config.js` 在 runtime 從後端讀取 `MOVERA_API_KEY`，不需在 `.env` 或 build 階段設定任何 API Key。只要後端啟動時帶有 `MOVERA_API_KEY` 環境變數，前端就會自動在請求中附帶 `X-API-Key` header：

```bash
# 終端 1：啟動後端（帶 API Key）
MOVERA_API_KEY=test-key uv run main.py

# 終端 2：啟動前端 dev server（自動 proxy /runtime-config.js 到後端）
npm run dev
```

### 測試

```bash
# 前端測試
npm run test:run

# 後端測試
uv run pytest tests/backend/ -v
```

## API 文件

API 文件預設關閉，需設定環境變數 `MOVERA_ENABLE_DOCS=true` 後啟用：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

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
