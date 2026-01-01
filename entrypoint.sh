#!/bin/sh
set -e

logger(){
    local message="$@"
    echo "[Entrypoint] $message"
}

# 從環境變數讀取 PUID 和 PGID，若不存在則使用預設值 1000
PUID=${PUID:-1000}
PGID=${PGID:-1000}

# 驗證 PUID/PGID 為有效數字且不為 0（防止以 root 身份執行）
if ! echo "$PUID" | grep -qE '^[1-9][0-9]*$'; then
    echo "[Entrypoint] 錯誤：PUID 必須為大於 0 的正整數，目前值為 '$PUID'"
    exit 1
fi

if ! echo "$PGID" | grep -qE '^[1-9][0-9]*$'; then
    echo "[Entrypoint] 錯誤：PGID 必須為大於 0 的正整數，目前值為 '$PGID'"
    exit 1
fi

logger "啟動檢查：UID=$PUID, GID=$PGID"

# --- 群組處理 ---
if getent group $PGID > /dev/null; then
    EXISTING_GROUP_NAME=$(getent group $PGID | cut -d: -f1)
    logger "GID $PGID 已存在，將群組 '$EXISTING_GROUP_NAME' 更名為 'movera'"
    groupmod -n movera "$EXISTING_GROUP_NAME"
else
    logger "建立新群組 'movera'，GID 為 $PGID"
    groupadd -g $PGID movera
fi

# --- 使用者與家目錄處理 ---
if getent passwd $PUID > /dev/null; then
    # 使用者已存在，進行修改
    EXISTING_USER_NAME=$(getent passwd $PUID | cut -d: -f1)
    logger "修改現有使用者 '$EXISTING_USER_NAME' (UID: $PUID) 為 'movera'"

    # 重新命名使用者
    usermod -l movera "$EXISTING_USER_NAME"

    # 設定主要群組，並指定/建立家目錄
    usermod -g movera -d /home/movera movera
else
    # 使用者不存在，建立使用者並同時建立家目錄 (-m)
    logger "建立新使用者 'movera' (UID: $PUID) 並建立家目錄"
    useradd -u $PUID -g movera -s /bin/false -m movera
fi

# 無論如何，都確保家目錄存在且權限正確
mkdir -p /home/movera
chown movera:movera /home/movera

# 授權工作目錄給新使用者
# 這是必要的，因為 COPY 指令會以 root 身份複製檔案
logger "變更 /movera 目錄擁有者為 'movera'..."
chown -R movera:movera /movera

logger "權限設定完成。以 'movera' 使用者身份執行主程式..."

# 使用 gosu (一個安全的 sudo/su 替代品)
# 將執行權限從 root 切換到 movera 使用者，然後執行傳遞給此腳本的所有參數 ($@)
exec gosu movera "$@"
