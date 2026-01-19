"""
wsService 單元測試
"""

import pytest
from unittest.mock import MagicMock, AsyncMock

from backend import schemas
from backend.enums.wsEventEnum import wsEventEnum
from backend.exceptions.taskException import TaskAlreadyExists, TaskNotFound
from backend.exceptions.wsException import UnHandledWebSocketEvent, PayloadValidationError
from backend.services.previewService import ParsePreviewService, RegexPreviewService
from backend.services.wsService import wsService, WSServices


@pytest.fixture
def mock_ws_services(task_service, setting_service, log_service):
    """建立 mock 的 WSServices"""
    return WSServices(
        task=task_service,
        setting=setting_service,
        log=log_service,
        parse_preview=ParsePreviewService(),
        regex_preview=RegexPreviewService(),
    )


@pytest.fixture
def ws_service_instance(mock_ws_services):
    """建立 wsService 實例"""
    return wsService(services=mock_ws_services)


class TestWsServiceEventListener:
    """測試 wsService.event_listener 方法"""

    @pytest.mark.asyncio
    async def test_event_listener_unknown_event(self, ws_service_instance):
        """測試未知事件拋出例外"""
        with pytest.raises(UnHandledWebSocketEvent):
            await ws_service_instance.event_listener(
                event="unknown:event",
                payload={},
                request_id="test-request-id",
            )

    @pytest.mark.asyncio
    async def test_event_listener_ping(self, ws_service_instance):
        """測試 ping 事件"""
        result = await ws_service_instance.event_listener(
            event=wsEventEnum.PING.value,  # 使用 .value 取得字串
            payload={},
            request_id="test-request-id",
        )

        assert result["event"] == wsEventEnum.PING.value
        assert result["success"] is True
        assert result["payload"]["message"] == "pong"
        assert result["requestId"] == "test-request-id"


class TestWsServiceHandlePing:
    """測試 wsService._handle_system_ping 方法"""

    @pytest.mark.asyncio
    async def test_handle_ping(self, ws_service_instance):
        """測試 ping 處理"""
        result = await ws_service_instance._handle_system_ping({})

        assert result["message"] == "pong"


class TestWsServiceHandleGetTasks:
    """測試 wsService._handle_get_tasks 方法"""

    @pytest.mark.asyncio
    async def test_handle_get_tasks_empty(self, ws_service_instance):
        """測試取得空任務列表"""
        result = await ws_service_instance._handle_get_tasks({})

        assert result == []

    @pytest.mark.asyncio
    async def test_handle_get_tasks_with_tasks(
        self, ws_service_instance, mock_ws_services, sample_task_data
    ):
        """測試取得任務列表"""
        mock_ws_services.task.create_task(schemas.TaskCreate(**sample_task_data))

        result = await ws_service_instance._handle_get_tasks({})

        assert len(result) == 1
        assert result[0]["name"] == sample_task_data["name"]


class TestWsServiceHandleCreateTask:
    """測試 wsService._handle_create_task 方法"""

    @pytest.mark.asyncio
    async def test_handle_create_task_success(
        self, ws_service_instance, sample_task_data
    ):
        """測試成功建立任務"""
        result = await ws_service_instance._handle_create_task(sample_task_data)

        assert result["name"] == sample_task_data["name"]
        assert result["include"] == sample_task_data["include"]

    @pytest.mark.asyncio
    async def test_handle_create_task_invalid_payload(self, ws_service_instance):
        """測試無效的 payload"""
        with pytest.raises(ValueError):
            await ws_service_instance._handle_create_task({})

    @pytest.mark.asyncio
    async def test_handle_create_task_duplicate(
        self, ws_service_instance, sample_task_data
    ):
        """測試建立重複的任務"""
        await ws_service_instance._handle_create_task(sample_task_data)

        with pytest.raises(TaskAlreadyExists):
            await ws_service_instance._handle_create_task(sample_task_data)


class TestWsServiceHandleUpdateTask:
    """測試 wsService._handle_update_task 方法"""

    @pytest.mark.asyncio
    async def test_handle_update_task_success(
        self, ws_service_instance, sample_task_data
    ):
        """測試成功更新任務"""
        created = await ws_service_instance._handle_create_task(sample_task_data)

        update_payload = {
            "id": created["id"],
            "name": "更新後的名稱",
            "include": sample_task_data["include"],
            "move_to": "/new/path",
        }
        result = await ws_service_instance._handle_update_task(update_payload)

        assert result["name"] == "更新後的名稱"
        assert result["move_to"] == "/new/path"

    @pytest.mark.asyncio
    async def test_handle_update_task_invalid_payload(self, ws_service_instance):
        """測試無效的 payload"""
        with pytest.raises(ValueError):
            await ws_service_instance._handle_update_task({})

    @pytest.mark.asyncio
    async def test_handle_update_task_not_found(
        self, ws_service_instance, sample_task_data
    ):
        """測試更新不存在的任務"""
        update_payload = {
            "id": "non-existent-id",
            "name": "任何名稱",
            "include": "關鍵字",
            "move_to": "/path",
        }

        with pytest.raises(TaskNotFound):
            await ws_service_instance._handle_update_task(update_payload)


class TestWsServiceHandleDeleteTask:
    """測試 wsService._handle_delete_task 方法"""

    @pytest.mark.asyncio
    async def test_handle_delete_task_success(
        self, ws_service_instance, sample_task_data
    ):
        """測試成功刪除任務"""
        created = await ws_service_instance._handle_create_task(sample_task_data)

        # 刪除任務
        await ws_service_instance._handle_delete_task({"id": created["id"]})

        # 確認已刪除
        tasks = await ws_service_instance._handle_get_tasks({})
        assert len(tasks) == 0

    @pytest.mark.asyncio
    async def test_handle_delete_task_invalid_payload(self, ws_service_instance):
        """測試無效的 payload"""
        with pytest.raises(ValueError):
            await ws_service_instance._handle_delete_task({})

    @pytest.mark.asyncio
    async def test_handle_delete_task_not_found(self, ws_service_instance):
        """測試刪除不存在的任務"""
        with pytest.raises(TaskNotFound):
            await ws_service_instance._handle_delete_task({"id": "non-existent-id"})


class TestWsServiceHandleGetSettings:
    """測試 wsService._handle_get_settings 方法"""

    @pytest.mark.asyncio
    async def test_handle_get_settings(self, ws_service_instance):
        """測試取得設定"""
        # 注意：目前 _handle_get_settings 方法體為空，會回傳 None
        result = await ws_service_instance._handle_get_settings({})

        # 根據目前的實現，會回傳 None
        assert result is None


class TestWsServiceHandleUpdateSettings:
    """測試 wsService._handle_update_settings 方法"""

    @pytest.mark.asyncio
    async def test_handle_update_settings(self, ws_service_instance, db_session):
        """測試更新設定"""
        from backend.models.setting import Setting

        # 先建立設定
        setting = Setting(key="timezone", value="Asia/Taipei")
        db_session.add(setting)
        db_session.commit()

        result = await ws_service_instance._handle_update_settings({"timezone": "UTC"})

        assert result["timezone"] == "UTC"


class TestWsServiceHandleGetLogs:
    """測試 wsService._handle_get_logs 方法"""

    @pytest.mark.asyncio
    async def test_handle_get_logs_empty(
        self, ws_service_instance, mock_ws_services, sample_task_data
    ):
        """測試取得空日誌"""
        task = mock_ws_services.task.create_task(schemas.TaskCreate(**sample_task_data))

        result = await ws_service_instance._handle_get_logs({"id": task.id})

        assert result == []

    @pytest.mark.asyncio
    async def test_handle_get_logs_with_logs(
        self, ws_service_instance, mock_ws_services, sample_task_data
    ):
        """測試取得日誌"""
        task = mock_ws_services.task.create_task(schemas.TaskCreate(**sample_task_data))
        mock_ws_services.log.create_log(
            schemas.LogCreate(task_id=task.id, level="INFO", message="測試日誌")
        )

        result = await ws_service_instance._handle_get_logs({"id": task.id})

        assert len(result) == 1
        assert result[0]["message"] == "測試日誌"


class TestWsServiceHandleCreateLog:
    """測試 wsService._handle_create_log 方法"""

    @pytest.mark.asyncio
    async def test_handle_create_log_success(
        self, ws_service_instance, mock_ws_services, sample_task_data
    ):
        """測試成功建立日誌"""
        task = mock_ws_services.task.create_task(schemas.TaskCreate(**sample_task_data))

        log_payload = {
            "task_id": task.id,
            "level": "INFO",
            "message": "測試日誌訊息",
        }
        result = await ws_service_instance._handle_create_log(log_payload)

        assert result["message"] == "測試日誌訊息"
        assert result["level"] == "INFO"

    @pytest.mark.asyncio
    async def test_handle_create_log_invalid_payload(self, ws_service_instance):
        """測試無效的 payload"""
        with pytest.raises(ValueError):
            await ws_service_instance._handle_create_log({})


class TestWsServiceHandlePreviewParse:
    """測試 wsService._handle_preview_parse 方法"""

    @pytest.mark.asyncio
    async def test_handle_preview_parse_success(self, ws_service_instance):
        """測試成功解析預覽"""
        payload = {
            "src_pattern": "{title} - {episode}.mp4",
            "text": "動畫名稱 - 01.mp4",
            "dst_pattern": "{title} - S01E{episode}.mp4",
        }
        result = await ws_service_instance._handle_preview_parse(payload)

        assert result["groups"]["title"] == "動畫名稱"
        assert result["formatted"] == "動畫名稱 - S01E01.mp4"

    @pytest.mark.asyncio
    async def test_handle_preview_parse_invalid_payload(self, ws_service_instance):
        """測試無效的 payload"""
        with pytest.raises(PayloadValidationError):
            await ws_service_instance._handle_preview_parse({})


class TestWsServiceHandlePreviewRegex:
    """測試 wsService._handle_preview_regex 方法"""

    @pytest.mark.asyncio
    async def test_handle_preview_regex_success(self, ws_service_instance):
        """測試成功正則預覽"""
        payload = {
            "src_pattern": r"(.+) - (\d+).mp4",
            "text": "動畫名稱 - 01.mp4",
            "dst_pattern": r"\1 - S01E\2.mp4",
        }
        result = await ws_service_instance._handle_preview_regex(payload)

        assert result["formatted"] == "動畫名稱 - S01E01.mp4"

    @pytest.mark.asyncio
    async def test_handle_preview_regex_invalid_payload(self, ws_service_instance):
        """測試無效的 payload"""
        with pytest.raises(PayloadValidationError):
            await ws_service_instance._handle_preview_regex({})
