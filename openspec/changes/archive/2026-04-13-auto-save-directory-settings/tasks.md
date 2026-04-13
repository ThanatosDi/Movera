## 1. 前置準備

- [x] 1.1 確認現有測試全部通過（`uv run pytest tests/` 和 `npx vitest run`）

## 2. 前端 — 允許目錄即時保存

### 2.1 🔴 紅燈 — 撰寫測試

- [x] 2.1.1 更新 `SettingView.spec.ts`：新增目錄後應呼叫 `updateSettings`
- [x] 2.1.2 更新 `SettingView.spec.ts`：刪除目錄後應呼叫 `updateSettings`
- [x] 2.1.3 執行測試，確認失敗

### 2.2 🟢 綠燈 — 實作即時保存

- [x] 2.2.1 將 `addDirectory()` 改為 async，新增後立即呼叫 API 保存並顯示通知
- [x] 2.2.2 將 `removeDirectory()` 改為 async，刪除後立即呼叫 API 保存並顯示通知
- [x] 2.2.3 加入失敗時回滾本地狀態的邏輯
- [x] 2.2.4 執行測試，確認通過

## 3. 前端 — 檔案來源白名單即時保存

### 3.1 🟢 綠燈 — 實作即時保存

- [x] 3.1.1 將 `addSourceDirectory()` 改為 async，新增後立即呼叫 API 保存並顯示通知
- [x] 3.1.2 將 `removeSourceDirectory()` 改為 async，刪除後立即呼叫 API 保存並顯示通知
- [x] 3.1.3 加入失敗時回滾本地狀態的邏輯
- [x] 3.1.4 執行測試，確認通過

## 4. 前端 — i18n 與清理

- [x] 4.1 新增 i18n 翻譯 key：目錄新增成功/失敗、刪除成功/失敗的通知訊息
- [x] 4.2 執行前端型別檢查 `npx vue-tsc --noEmit`

## 5. 整合測試

- [x] 5.1 執行全部前端測試 `npx vitest run`
- [x] 5.2 啟動開發伺服器，在瀏覽器中驗證：新增/刪除目錄後顯示通知
- [x] 5.3 驗證失敗情境（如 `ALLOW_WEBUI_SETTING=false` 時新增應顯示 403 錯誤通知）
