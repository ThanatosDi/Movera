# Movera

Movera 是一個專為影音收藏家設計的智慧檔案管理工具，旨在自動化您的媒體檔案整理流程。透過與多個下載器的無縫整合，Movera 能夠在下載完成後，根據您自訂的規則，自動將檔案移動到指定資料夾並進行標準化重新命名。

它結合了 Vue 3 打造的現代化 Web UI、由 FastAPI 驅動的高效能後端 API，以及穩定的背景任務處理系統，提供了一個完整且易於使用的解決方案。

## ✨ 核心功能

- **自動化任務管理**: 建立、讀取、更新和刪除 (CRUD) 檔案移動與重新命名任務。
- **智慧重新命名**: 支援使用正則表達式 (Regex) 或字串解析 (Parse) 兩種模式來定義複雜的重新命名規則。
- **qBittorrent 整合**: 透過 Webhook 監聽 qBittorrent 的下載完成事件，觸發自動化處理流程。
- **Web UI 操作介面**: 提供一個現代化、響應式的網頁介面，讓您輕鬆管理所有任務和設定。
- **系統設定**: 可透過 UI 調整系統層級的設定。
- **任務統計**: 快速查看已啟用和已停用任務的數量。
- **詳細日誌**: 追蹤每個任務的執行情況，方便除錯與監控。

## 🛠️ 技術架構

- **後端**: Python 3.12+, [FastAPI](https://fastapi.tiangolo.com/), SQLAlchemy (搭配 SQLite), Alembic
- **前端**: Node.js 22+, [Vue.js 3](https://vuejs.org/), [Vite](https://vitejs.dev/), [Tailwind CSS](https://tailwindcss.com/), [Pinia](https://pinia.vuejs.org/), shadcn-vue
- **容器化**: Docker, Docker Compose

## 🚀 快速啟動 (使用 Docker)

對於熟悉容器化操作的使用者，使用 Docker 是最快且最推薦的啟動方式。

1.  **拉取映像 (Pull Image)**:

    從 Docker Hub 拉取最新的 Movera 映像。

    ```bash
    docker pull thanatosdi/movera:latest
    ```

2.  **準備資料夾**:

    在您選擇的位置建立兩個資料夾，用於存放 Movera 的資料庫和儲存檔案。

    ```bash
    mkdir -p ./database
    mkdir -p ./storages
    ```

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
      -v <storages_path>:/storages \
      --name movera \
      thanatosdi/movera:latest
    ```

    - `-d`: 在背景執行容器。
    - `-p <HOST_PORT>:8000`: 將您主機的 `<HOST_PORT>` 連接埠映射到容器固定的 `8000` 連接埠。例如，使用 `-p 8888:8000`，您就可以透過 `http://localhost:8888` 訪問 Movera。
    - `-v $(pwd)/database:/movera/database`: **(必要)** 將主機上存放資料庫檔案的 `database` 資料夾掛載到容器中。
    - `-v $(pwd)/storages:/movera/storages`: **(必要)** 將主機上用於存儲的 `storages` 資料夾掛載到容器中。
    - `-v <downloader_path>:/download`: **(必要)** 將主機上用於下載檔案的資料夾掛載到容器中。
    - `-v <storages_path>:/storages`: **(必要)** 將主機上用於存儲檔案的資料夾掛載到容器中。
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
        restart: unless-stopped
    ```
    - `ports` 區塊建議完整寫清楚主機內網 IP 位址，例如 `127.0.0.1:8000:8000` 與 `192.168.1.10:8000:8000` 之類的；如果只填寫 `8000:8000` 表示任何來源的主機都可以繞過防火牆 `8000` 埠進行訪問。
    </details>

5.  **訪問 Movera**:

    容器啟動後，您可以透過瀏覽器訪問 `http://localhost:<HOST_PORT>` 來開啟 Movera 的 Web UI。

6.  **下載器設定**:
    <details>
    <summary>qBittorrent</summary>
    
    將 [`scripts`](https://github.com/ThanatosDi/Movera/blob/main/scripts/qbittorrent/in-complete) 放置到 qBittorrent 中，並賦予執行權限  
    ```bash
    chmod +x in-complete
    ```
    登入您的 qBittorrent Web UI，進入 `選項` -> `下載` -> `下載完成時執行外部程式`，並填入以下指令：

    ```
    /config/scripts/in-complete http://<MOVERA_HOST_IP>/webhook/qbittorrent/on-complete "%F" "%L"
    ```

    請將 `<MOVERA_HOST_IP>` 替換為執行 Movera 容器的主機的 IP 位址，並將 `<HOST_PORT>` 替換為您在 `docker run` 指令中設定的連接埠。
    <details>
## 📚 API 端點

Movera 提供了一套完整的 RESTful API 來管理系統。您可以在應用程式啟動後，訪問 `http://localhost:8000/docs` 來查看詳細的 OpenAPI (Swagger) 文件。

- `GET /api/v1/tasks`: 獲取所有任務。
- `POST /api/v1/task`: 建立一個新任務。
- `GET /api/v1/task/{task_id}`: 獲取單一任務的詳細資訊。
- `PUT /api/v1/task/{task_id}`: 更新一個現有任務。
- `DELETE /api/v1/task/{task_id}`: 刪除一個任務。
- `GET /api/v1/settings`: 獲取所有設定。
- `PUT /api/v1/settings`: 更新多個設定。
- `POST /webhook/qbittorrent/on-complete`: qBittorrent 的 Webhook 接收端點。

## 💻 開發指南

如果您想為 Movera 貢獻程式碼或進行二次開發，請遵循以下步驟設定您的本機開發環境。

### 後端 (FastAPI)

1.  **安裝 Python**: 確保您已安裝 Python 3.12 或更高版本。
2.  **安裝 uv**: 本專案使用 `uv` 作為套件管理器。請參考 [uv 官方文件](https://github.com/astral-sh/uv) 進行安裝。
3.  **建立虛擬環境並安裝依賴**: 

    ```bash
    # 建立虛擬環境
    uv venv

    # 安裝依賴
    uv sync --locked
    ```

4.  **啟動後端伺服器**:

    ```bash
    uv run uvicorn api.main:app --reload
    ```

### 前端 (Vue)

1.  **安裝 Node.js**: 確保您已安裝 Node.js 22.x 或更高版本。
2.  **安裝依賴**: 

    ```bash
    npm install
    ```

3.  **啟動前端開發伺服器**:

    ```bash
    npm run dev
    ```

4.  **設定環境變數**:

    在前端開發伺服器中，您可以設定環境變數 `VITE_API_BASE_URL` 來指定後端 API 的基本 URL。例如：

    ```bash
    VITE_API_BASE_URL="http://localhost:8000"
    ```

設定完成後，後端 API 將運行在 `http://localhost:8000`，前端開發伺服器將運行在 `http://localhost:5173` (或 Vite 指定的其他連接埠)。
