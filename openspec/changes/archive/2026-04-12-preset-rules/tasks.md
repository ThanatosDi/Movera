## 1. 前置準備

- [x] 1.1 新增 i18n 翻譯 key（`settingView.presetRuleCard.*`、`components.presetRuleModal.*`）
- [x] 1.2 新增前端 TypeScript schema（`PresetRule`、`PresetRuleCreate`、`PresetRuleUpdate`）
- [x] 1.3 新增後端 Exception 類別（`PresetRuleNotFound`、`PresetRuleAlreadyExists`）

## 2. 後端 Model + Migration（TDD 循環）

### 2.1 🔴 紅燈 - 撰寫 PresetRule Model 測試

- [x] 2.1.1 測試：PresetRule model 可正確建立（含所有欄位）
- [x] 2.1.2 測試：name 欄位具有唯一性約束
- [x] 2.1.3 測試：rule_type 僅接受 parse 或 regex
- [x] 2.1.4 測試：field_type 僅接受 src 或 dst
- [x] 2.1.5 執行測試，確認全部失敗

### 2.2 🟢 綠燈 - 實作 PresetRule Model

- [x] 2.2.1 建立 `backend/models/preset_rule.py`（UUID PK、name、rule_type、field_type、pattern、created_at）
- [x] 2.2.2 在 `backend/models/__init__.py` 匯出 PresetRule
- [x] 2.2.3 建立 Alembic migration
- [x] 2.2.4 執行測試，確認全部通過

### 2.3 🔵 重構 - 確認 Model 品質

- [x] 2.3.1 確認欄位註解與索引正確
- [x] 2.3.2 執行測試，確認仍然通過

## 3. 後端 Schema + Repository + Service（TDD 循環）

### 3.1 🔴 紅燈 - 撰寫 Schema 與 Repository 測試

- [x] 3.1.1 測試：PresetRuleCreate schema 驗證有效資料
- [x] 3.1.2 測試：PresetRuleCreate schema 拒絕無效 rule_type
- [x] 3.1.3 測試：PresetRuleCreate schema 拒絕無效 field_type
- [x] 3.1.4 測試：Repository CRUD 操作（create、get_all、get_by_id、update、delete）
- [x] 3.1.5 測試：Repository 支援 rule_type 和 field_type 篩選
- [x] 3.1.6 執行測試，確認全部失敗

### 3.2 🟢 綠燈 - 實作 Schema、Repository、Service

- [x] 3.2.1 在 `backend/schemas.py` 新增 PresetRule 相關 Pydantic schemas
- [x] 3.2.2 建立 `backend/repositories/preset_rule.py`（CRUD + 篩選查詢）
- [x] 3.2.3 建立 `backend/services/preset_rule_service.py`（業務邏輯、驗證）
- [x] 3.2.4 執行測試，確認全部通過

### 3.3 🔵 重構 - 確認 Service 層品質

- [x] 3.3.1 確認 Exception 處理正確（NotFound、AlreadyExists）
- [x] 3.3.2 執行測試，確認仍然通過

## 4. 後端 Router（TDD 循環）

### 4.1 🔴 紅燈 - 撰寫 Router 測試

- [x] 4.1.1 測試：GET /api/v1/preset-rules 回傳所有常用規則
- [x] 4.1.2 測試：GET /api/v1/preset-rules?rule_type=parse 篩選正確
- [x] 4.1.3 測試：GET /api/v1/preset-rules?field_type=src 篩選正確
- [x] 4.1.4 測試：POST /api/v1/preset-rules 建立成功回傳 201
- [x] 4.1.5 測試：POST 重複名稱回傳 409
- [x] 4.1.6 測試：PUT /api/v1/preset-rules/{id} 更新成功
- [x] 4.1.7 測試：DELETE /api/v1/preset-rules/{id} 刪除成功回傳 204
- [x] 4.1.8 測試：GET/PUT/DELETE 不存在的 ID 回傳 404
- [x] 4.1.9 執行測試，確認全部失敗

### 4.2 🟢 綠燈 - 實作 Router

- [x] 4.2.1 建立 `backend/routers/preset_rule.py`（CRUD 端點 + query 參數篩選）
- [x] 4.2.2 在 `backend/dependencies.py` 新增 PresetRule 依賴注入
- [x] 4.2.3 在 `backend/backend.py` 註冊 router 和 exception handler
- [x] 4.2.4 執行測試，確認全部通過

### 4.3 🔵 重構 - 確認 Router 品質

- [x] 4.3.1 確認 API 回應格式與現有端點一致
- [x] 4.3.2 執行測試，確認仍然通過

## 5. 前端 presetRuleStore（TDD 循環）

### 5.1 🔴 紅燈 - 撰寫 presetRuleStore 測試

- [x] 5.1.1 測試：fetchPresetRules 取得所有常用規則
- [x] 5.1.2 測試：fetchPresetRules 支援 rule_type 和 field_type 篩選參數
- [x] 5.1.3 測試：createPresetRule 建立常用規則
- [x] 5.1.4 測試：updatePresetRule 更新常用規則
- [x] 5.1.5 測試：deletePresetRule 刪除常用規則
- [x] 5.1.6 執行測試，確認全部失敗

### 5.2 🟢 綠燈 - 實作 presetRuleStore

- [x] 5.2.1 建立 `src/stores/presetRuleStore.ts`（CRUD + 篩選）
- [x] 5.2.2 執行測試，確認全部通過

### 5.3 🔵 重構 - 優化 Store

- [x] 5.3.1 確認 error handling 與 loading state 正確
- [x] 5.3.2 執行測試，確認仍然通過

## 6. 設定頁面常用規則管理區塊（TDD 循環）

### 6.1 🔴 紅燈 - 撰寫管理區塊測試

- [x] 6.1.1 測試：顯示常用規則列表（含名稱、規則類型、欄位類型、規則內容）
- [x] 6.1.2 測試：無規則時顯示空狀態提示
- [x] 6.1.3 測試：新增表單包含名稱、規則類型選擇、欄位類型選擇、規則內容輸入
- [x] 6.1.4 測試：刪除規則呼叫 store 的 deletePresetRule
- [x] 6.1.5 執行測試，確認全部失敗

### 6.2 🟢 綠燈 - 實作設定頁面常用規則區塊

- [x] 6.2.1 在 `SettingView.vue` 新增常用規則 Card 區塊（列表顯示 + 新增表單）
- [x] 6.2.2 在 `Header.vue` 的 `onMounted` 中加入 `presetRuleStore.fetchPresetRules()`
- [x] 6.2.3 執行測試，確認全部通過

### 6.3 🔵 重構 - 優化 UI

- [x] 6.3.1 確認樣式與 Tag 管理區塊一致
- [x] 6.3.2 確認 i18n 翻譯正確
- [x] 6.3.3 執行測試，確認仍然通過

## 7. PresetRuleModal 與 TaskForm 整合（TDD 循環）

### 7.1 🔴 紅燈 - 撰寫 Modal 與整合測試

- [x] 7.1.1 測試：Modal 接收 ruleType 和 fieldType props 並顯示對應規則
- [x] 7.1.2 測試：無對應規則時顯示空狀態
- [x] 7.1.3 測試：點擊規則後 emit select 事件並關閉 Modal
- [x] 7.1.4 測試：TaskForm 在 rename_rule 選擇後顯示套用按鈕
- [x] 7.1.5 測試：TaskForm 在 rename_rule 未選擇時隱藏套用按鈕
- [x] 7.1.6 執行測試，確認全部失敗

### 7.2 🟢 綠燈 - 實作 Modal 與整合

- [x] 7.2.1 建立 `src/components/PresetRuleModal.vue`（篩選顯示、選擇 emit）
- [x] 7.2.2 修改 `TaskForm.vue`，在 src_filename 和 dst_filename 旁新增套用按鈕
- [x] 7.2.3 點擊按鈕開啟 Modal，選擇後填入對應欄位
- [x] 7.2.4 執行測試，確認全部通過

### 7.3 🔵 重構 - 優化互動

- [x] 7.3.1 確認 Modal 樣式與現有 Dialog 元件一致
- [x] 7.3.2 確認套用按鈕在建立任務頁面與編輯頁面都正常運作
- [x] 7.3.3 執行測試，確認仍然通過

## 8. 整合測試與品質檢查

- [x] 8.1 執行完整後端測試套件，確認無回歸
- [x] 8.2 執行完整前端測試套件，確認無回歸
- [x] 8.3 執行 vue-tsc 型別檢查，確認無錯誤
- [ ] 8.4 使用 MCP Chrome DevTools 進行 E2E 測試：驗證設定頁面常用規則管理流程
- [ ] 8.5 使用 MCP Chrome DevTools 進行 E2E 測試：驗證任務頁面套用常用規則流程
