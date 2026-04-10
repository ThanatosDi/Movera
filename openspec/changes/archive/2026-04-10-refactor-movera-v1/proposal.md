## Why

Movera v1 專案（`h:/VSCode/Python/Movera`）已具備完整功能，但在程式碼品質、命名一致性、架構遵循度上存在多項技術債。主要問題包括：

1. **Backend 命名違反 PEP 8**：Service 模組使用 camelCase（如 `taskService.py`），不符合 Python snake_case 慣例
2. **邏輯 Bug**：`utils/rename.py` 中 `ParseRenameRule` 與 `RegexRenameRule` 存在變數作用域錯誤，當 `filepath` 為 Path 物件時會觸發 `NameError`
3. **依賴注入不一致**：`preview` 路由直接實例化 Service，未使用 `Depends()` 模式
4. **Worker 全域狀態**：`worker.py` 使用全域可變狀態管理服務實例，非執行緒安全
5. **型別安全不足**：Backend 多處缺少回傳型別提示；Frontend 使用 `Record<string, any>` 與不安全的型別轉換
6. **SRP 違規**：`PathService`、`SettingService` 承擔多重職責
7. **Frontend 元件過長**：`TaskDetailView.vue`（326 行）需要拆分
8. **命名不一致**：Frontend 事件處理器混用 `btn*`、`handle*`、`on*` 前綴；Schema 介面使用 snake_case

此重構旨在將 v1 程式碼提升至 v2 的 `project.md` 規範標準，確保 Clean Code、一致的命名慣例、完善的文件註解。

## What Changes

### Backend
- [ ] 重新命名 Service 模組檔案為 snake_case（`taskService.py` → `task_service.py`）
- [ ] 修復 `utils/rename.py` 中的變數作用域 Bug
- [ ] 統一所有 Router 使用 `Depends()` 依賴注入（修復 preview 路由）
- [ ] 重構 `worker.py` 全域狀態為適當的依賴注入模式
- [ ] 補齊所有函式的回傳型別提示
- [ ] 拆分 `PathService` 為 `PathValidator` + `DirectoryScanner`
- [ ] 拆分 `SettingService` 的驗證邏輯為獨立模組
- [ ] 移除未使用的 import（`func` in models/task.py、`os` in pathService.py）
- [ ] 為複雜商業邏輯補充 docstring（說明 Why）
- [ ] 消除 magic number，使用具名常數

### Frontend
- [ ] 拆分 `TaskDetailView.vue` 為子元件（`TaskEditForm`、`TaskLogsPanel`、`TaskDeleteDialog`）
- [ ] 統一事件處理器命名為 `handle*` 前綴
- [ ] 移除 `Record<string, any>`，建立明確的 `ToastOptions` 型別
- [ ] 建立 `ApiError` 型別，取代不安全的 `as` 型別轉換
- [ ] 為 Pinia Store 補充 JSDoc 文件
- [ ] 修正 `SidebarItem.vue` 的冗餘 `task` 前綴命名

## Capabilities

### New Capabilities
- `coding-standards`: 定義並實施 Clean Code 準則、命名慣例、註解規範，作為專案開發的基礎約束

### Modified Capabilities

（無現有 spec 需要修改）

## Impact

- **Backend 所有模組**：Service 檔案重新命名影響所有 import 路徑（routers/、dependencies.py、tests/）
- **Frontend 元件**：TaskDetailView 拆分影響路由與父元件引用
- **測試**：需同步更新所有受影響的 import 路徑與測試案例
- **無 API 變更**：此次重構為純內部改動，不影響 API 契約或資料庫結構
- **無 Breaking Change**：對外部使用者（下載器 webhook 整合）完全透明
