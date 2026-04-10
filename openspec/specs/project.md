# Project 規範

## 架構與設計模式

本專案採用分層架構（Layered Architecture）搭配 Repository Pattern：

- **Backend**: Routers → Services → Repositories → Models → Database
  - 每一層只能依賴其下一層，禁止跨層呼叫（例如 Router 不可直接存取 Repository）
  - 使用依賴注入（Dependency Injection）管理層間依賴
  - Service 層負責商業邏輯，Repository 層負責資料存取
  - Router 層僅負責 HTTP 請求/回應的轉換與驗證

- **Frontend**: Views → Components → Composables → Stores → API
  - 使用 Vue 3 Composition API，禁止使用 Options API
  - Composables 封裝可重用邏輯，Stores（Pinia）管理全域狀態
  - API 層統一處理 HTTP 請求，Components 不可直接呼叫 API

## Clean Code 準則

### 函式設計
- 每個函式不超過 **30 行**（不含空行與註解）
- 嚴格遵守**單一職責原則（SRP）**：每個函式只做一件事
- 函式參數不超過 **3 個**，超過時使用物件參數（Python 用 dataclass/Pydantic model，TypeScript 用 interface/type）
- 禁止多層 `if/else` 巢狀結構，優先使用 **Early Return** 模式
- 禁止在函式中混合不同抽象層級的操作

### 類別與模組設計
- 每個檔案只包含一個主要類別或一組高度相關的函式
- Backend 的 Service 類別方法數不超過 **10 個**，超過時拆分為多個 Service
- Frontend 的 Composable 遵循單一用途原則，避免成為「萬用工具箱」

### 程式碼品質
- 禁止使用 `# type: ignore` 或 `@ts-ignore`，除非附帶說明原因的註解
- 禁止使用 `any` 型別（TypeScript），必須定義明確的型別
- 禁止 magic number，必須使用具名常數
- 禁止空的 `except` / `catch` 區塊，必須明確處理或記錄錯誤
- 避免深層巢狀（最多 **2 層**縮排邏輯），超過時提取為獨立函式

## 命名慣例

### 通用規則
- 所有命名必須具備**高度描述性**，讓讀者不需要查看實作就能理解用途
- **禁止使用模糊命名**：`temp`、`data`、`info`、`item`、`obj`、`val`、`result`、`ret`、`tmp`、`x`、`d` 等
- 布林變數/函式使用 `is`、`has`、`can`、`should` 前綴（例如：`isCompleted`、`hasPermission`）
- 集合型別使用複數名詞（例如：`tasks`、`downloadRules`）

### Python（Backend）
- 變數與函式：`snake_case`（例如：`get_active_download_rules`）
- 類別：`PascalCase`（例如：`DownloadRuleService`）
- 常數：`UPPER_SNAKE_CASE`（例如：`MAX_RETRY_COUNT`）
- 私有方法/屬性：單底線前綴 `_`（例如：`_validate_file_path`）

### TypeScript（Frontend）
- 變數與函式：`camelCase`（例如：`getActiveDownloadRules`）
- 元件：`PascalCase`（例如：`DownloadRuleList.vue`）
- 型別/介面：`PascalCase`（例如：`DownloadRuleResponse`）
- 常數：`UPPER_SNAKE_CASE`（例如：`MAX_RETRY_COUNT`）
- Composable：`use` 前綴（例如：`useDownloadRules`）
- Store：以領域命名（例如：`useTaskStore`）

### 檔案命名
- Backend Python 檔案：`snake_case.py`
- Frontend Vue 元件：`PascalCase.vue`
- Frontend TypeScript 檔案：`camelCase.ts`（工具類）或 `PascalCase.ts`（型別/類別）
- 測試檔案：與被測檔案同名加上 `_test.py`（Backend）或 `.spec.ts` / `.test.ts`（Frontend）

## 註解與文件

### 何時必須加註解
- **複雜的商業邏輯**：必須使用 JSDoc（TypeScript）或 docstring（Python）說明**「為什麼（Why）」**這樣設計，而非描述程式碼在做什麼
- **非直覺的實作決策**：如果一段程式碼的寫法不是最直覺的方式，必須說明選擇此方式的原因
- **Workaround 或已知限制**：標註 `# WORKAROUND:` 或 `// WORKAROUND:` 並說明原因與預期修復時機
- **正則表達式**：必須附帶說明匹配模式的用途

### 註解格式

**Python（Docstring）**：
```python
def move_completed_download(self, download_id: int, target_path: Path) -> MoveResult:
    """將已完成的下載檔案移動到目標路徑。

    根據任務規則比對下載名稱，決定目標子目錄結構。
    若目標已存在相同檔案，會依據 conflict_strategy 設定決定覆蓋或跳過。

    Why: 分離移動邏輯與規則比對，讓規則變更不影響檔案操作流程。
    """
```

**TypeScript（JSDoc）**：
```typescript
/**
 * 根據下載規則比對結果，組合出最終的目標路徑。
 *
 * Why: 路徑組合邏輯集中在此函式，避免多處重複且不一致的路徑拼接。
 *
 * @param matchedRule - 比對成功的下載規則
 * @param downloadName - 原始下載名稱
 * @returns 組合後的完整目標路徑
 */
```

### 禁止的註解
- 禁止描述顯而易見的程式碼行為（例如：`// 設定 count 為 0`）
- 禁止殘留已註解掉的程式碼，直接刪除並依賴版本控制
- 禁止使用 `TODO` 而不附帶 issue 編號或負責人（格式：`TODO(#123)` 或 `TODO(@username)`）
