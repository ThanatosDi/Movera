# Movera - 技術分析與開發指南

## 簡介

Movera 是一個由任務驅動的檔案管理與自動化平台。其主要設計目的是監控如下載工具（例如 qBittorrent）的完成事件，並根據使用者預先定義的規則，自動對檔案進行重新命名和移動。

專案提供了一個現代化的 Web 使用者介面，讓使用者可以輕鬆建立、管理和監控這些自動化任務。

## ✨ 核心功能

- **任務化管理**: 以「任務」為核心，每個任務定義了一套完整的檔案處理流程。
- **智慧重新命名**: 支援兩種重新命名模式：
    1.  **Parse**: 透過簡單的樣板語法（如 `{name}.{ext}`）進行匹配和格式化。
    2.  **Regex**: 使用功能強大的正規表示式進行複雜的檔名匹配和替換。
- **Webhook 整合**: 內建 Webhook 端點，可直接與 qBittorrent 等下載軟體整合，實現下載完成後的無縫自動化處理。
- **視覺化預覽**: 在建立命名規則時，提供即時的預覽功能，確保規則的正確性。
- **日誌與監控**: 每個任務的執行過程和結果都會被詳細記錄，方便追蹤與除錯。
- **Web UI 管理**: 提供一個基於 Vue.js 的單頁應用程式（SPA），用於管理所有任務、設定和查看日誌。

## 🛠️ 技術架構

Movera 採用前後端分離的現代 Web 應用架構，並透過 Docker 進行容器化部署。

- **後端 (Backend)**
    - **框架**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
    - **資料庫 ORM**: [SQLAlchemy](https://www.sqlalchemy.org/)
    - **資料庫遷移**: [Alembic](https://alembic.sqlalchemy.org/)
    - **Web 伺服器**: [Uvicorn](https://www.uvicorn.org/)
    - **套件管理**: [uv](https://github.com/astral-sh/uv)

- **前端 (Frontend)**
    - **框架**: [Vue.js 3](https://vuejs.org/) (使用 Composition API)
    - **語言**: [TypeScript](https://www.typescriptlang.org/)
    - **建置工具**: [Vite](https://vitejs.dev/)
    - **狀態管理**: [Pinia](https://pinia.vuejs.org/)
    - **UI 元件庫**: [Tailwind CSS](https://tailwindcss.com/) 搭配 class-variance-authority (類似 Shadcn UI 的風格)
    - **路由**: [Vue Router](https://router.vuejs.org/)
    - **國際化**: [Vue I18n](https://vue-i18n.intlify.dev/)

- **資料庫**
    - 預設使用 **SQLite**，資料庫檔案儲存於 `database/` 目錄下，方便輕量部署。

- **容器化**
    - **Docker** 與 **Docker Compose**，簡化了部署和環境一致性。

## 🚀 快速啟動 (使用 Docker)

1.  **前置需求**:
    - [Docker](https://www.docker.com/get-started)
    - [Docker Compose](https://docs.docker.com/compose/install/)

2.  **設定環境變數**:
    專案使用 `PUID` 和 `PGID` 來設定容器內檔案的擁有者。在專案根目錄建立 `.env` 檔案：

    ```bash
    # .env
    PUID=1000
    PGID=1000
    ```
    *你可以透過在終端執行 `id` 命令來取得你目前的 PUID 和 PGID。*

3.  **執行容器 (Run Container)**:

    執行以下指令來啟動 Movera 容器。請根據您的需求修改 `<HOST_PORT>`。

    <details>
    <summary>docker</summary>
        
    ```bash
    docker run -d \
      -p <HOST_PORT>:8000 \
      -v $(pwd)/database:/movera/database \
      -v $(pwd)/storages:/movera/storages \
      -v <downloader_path>:/download \
      --name movera \
      thanatosdi/movera:latest
    ```

    - `-d`: 在背景執行容器。
    - `-p <HOST_PORT>:8000`: 將您主機的 `<HOST_PORT>` 連接埠映射到容器固定的 `8000` 連接埠。例如，使用 `-p 8888:8000`，您就可以透過 `http://localhost:8888` 訪問 Movera。
    - `-v $(pwd)/database:/movera/database`: **(必要)** 將主機上存放資料庫檔案的 `database` 資料夾掛載到容器中。
    - `-v $(pwd)/storages:/movera/storages`: **(必要)** 將主機上用於存儲的 `storages` 資料夾掛載到容器中。
    - `-v <downloader_path>:/download`: **(必要)** 將主機上用於下載檔案的資料夾掛載到容器中。
    </details>
    
    <details>
    <summary>docker compose</summary>
        
    ```yaml
    services:
      movera:
        image: thanatosdi/movera:latest
        container_name: movera
        ports:
          - "<HOST_PORT>:8000"
        volumes:
          - ./database:/movera/database
          - ./storages:/movera/storages
          - <downloader_path>:/download
        restart: unless-stopped
    ```
    - `ports` 區塊建議完整寫清楚主機內網 IP 位址，例如 `127.0.0.1:8000:8000` 與 `192.168.1.10:8000:8000` 之類的；如果只填寫 `8000:8000` 表示任何來源的主機都可以繞過防火牆 `8000` 埠進行訪問。
    </details>

4.  **存取應用**:
    服務啟動後，你可以透過瀏覽器存取 `http://localhost:8000` 來使用 Movera。

## 📚 API 端點

所有 API 端點皆以 `/api/v1` 為前綴。

#### `/tasks` - 任務管理

- `GET /tasks`: 獲取所有任務列表。
- `GET /task/{task_id}`: 獲取指定 ID 的任務詳情。
- `POST /task`: 建立一個新任務。
- `PUT /task/{task_id}`: 更新指定 ID 的任務。
- `DELETE /task/{task_id}`: 刪除指定 ID 的任務。
- `GET /tasks/stats`: 獲取任務統計數據（啟用/停用數量）。

#### `/log` - 日誌管理

- `GET /log/{task_id}`: 獲取指定任務的所有日誌。

#### `/settings` - 設定管理

- `GET /settings`: 獲取所有設定。
- `GET /setting/{key}`: 獲取指定鍵名的設定。
- `PUT /settings`: 更新多個設定。
- `PUT /setting/{key}`: 更新指定鍵名的設定。

#### `/parse-preview` - 規則預覽

- `POST /parse-preview`: 提供來源文字、匹配規則和目標格式，回傳預覽結果。

#### `/webhook` - Webhook 整合

- `GET /webhook/status`: 檢查 Webhook 服務狀態。
- `POST /webhook/qbittorrent/on-complete`: 接收 qBittorrent 下載完成的通知。

#### `/health` - 健康檢查

- `GET /api/v1/health`: 檢查 API 服務是否正常運行。

## 💻 開發指南

### 前置需求

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (建議的 Python 套件管理器)
- Node.js 20+
- [npm](https://www.npmjs.com/) 或相容的套件管理器

### 後端開發

1.  **安裝依賴**:
    ```bash
    uv sync
    ```

2.  **執行資料庫遷移**:
    ```bash
    uv run alembic upgrade head
    ```

3.  **啟動開發伺服器**:
    ```bash
    uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
    ```
    伺服器將在 `http://localhost:8000` 上運行，並在程式碼變更時自動重載。

### 前端開發

1.  **進入前端目錄並安裝依賴**:
    ```bash
    npm install
    ```

2. **設定環境變數**:  
   在前端開發伺服器中，您可以設定環境變數(.env) `VITE_API_BASE_URL` 來指定後端 API 的基本 URL。例如：

    ```bash
    VITE_API_BASE_URL="http://localhost:8000"
    ```

3.  **啟動開發伺服器**:
    ```bash
    npm run dev
    ```
    Vite 開發伺服器將啟動，你可以在終端輸出的位址（通常是 `http://localhost:5173`）上看到前端介面。

### 執行測試

專案使用 `pytest` 進行測試。

```bash
pytest
```
