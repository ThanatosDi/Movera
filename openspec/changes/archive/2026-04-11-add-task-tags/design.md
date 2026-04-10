## Context

Movera 目前的 Task model 僅有基本欄位（name、include、move_to 等），無任何分類機制。
使用者希望透過彩色標籤對任務進行分類，並在 Setting 頁面統一管理標籤庫。

影響層級：Model → Repository → Service → Router → Schema → Store → Component → View

## Goals / Non-Goals

**Goals:**
- 建立獨立的 Tag 資料模型，支援名稱與顏色屬性
- 透過多對多關聯表 `task_tags` 將標籤與任務關聯
- 提供完整的 Tag CRUD API
- Setting 頁面可管理全域標籤（建立、編輯、刪除）
- 任務表單可選擇既有標籤或快速新增標籤
- Sidebar 任務項目顯示標籤 Badge

**Non-Goals:**
- 不做按標籤篩選任務的功能（可未來擴展）
- 不做標籤排序或分組
- 不做標籤圖示（僅用顏色 + 文字）

## Decisions

### 1. 獨立 Tag table + 多對多關聯表

建立 `tag` 表（id, name, color）與 `task_tags` 關聯表（task_id, tag_id）。

理由：比 JSON 欄位更利於未來查詢、統計、篩選。標籤是全域資源，多個任務可共用同一標籤。
替代方案：Task 上存 JSON array — 簡單但無法全域管理標籤庫，且不利於查詢。

### 2. Tag 顏色使用預定義色票

提供 8-10 個預定義顏色選項（如 Tailwind CSS 常用色），不支援自訂 hex 值。

理由：降低 UI 複雜度，確保視覺一致性。預定義色票的儲存格式為色票名稱字串（如 `"red"`, `"blue"`, `"green"`），前端映射為對應的 Tailwind class。
替代方案：自訂 hex color picker — 過度複雜，視覺不易統一。

### 3. Task API 回應包含完整 Tag 物件

`GET /api/v1/tasks` 與 `GET /api/v1/tasks/{id}` 的回應中，`tags` 欄位為 `Tag[]` 完整物件陣列。
`POST/PUT` 的請求 body 使用 `tag_ids: string[]` 指定關聯的標籤 ID。

理由：讀取時直接取得完整標籤資訊（含名稱、顏色），避免前端再查詢。寫入時只需傳 ID 陣列。

### 4. Tag API 獨立路由

新增 `/api/v1/tags` 路由，遵循既有的 Layered Architecture（Router → Service → Repository）。

理由：與 Task API 職責分離，符合既有架構模式。

### 5. 刪除標籤或任務時自動解除關聯

刪除標籤時，`task_tags` 關聯記錄透過 cascade delete 自動清除，不影響任務本身。
刪除任務時，`task_tags` 關聯記錄同樣透過 cascade delete 自動清除，不影響標籤本身。

理由：`task_tags` 是純關聯表，任一端被刪除時關聯記錄都應自動清除，避免孤兒記錄。

## Risks / Trade-offs

- [風險] 多對多關聯增加 N+1 查詢可能 → 使用 SQLAlchemy `selectinload` 或 `joinedload` 預載入
- [風險] 同時編輯標籤與任務可能衝突 → 標籤管理與任務編輯為獨立操作，衝突機率低
- [取捨] 預定義色票限制了客製化空間 → 但簡化了 UI 與儲存，足以滿足分類需求
