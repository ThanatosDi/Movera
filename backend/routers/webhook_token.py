from fastapi import APIRouter, Depends, HTTPException

from backend import schemas
from backend.dependencies import depends_webhook_token_service
from backend.services.webhook_token_service import WebhookTokenService

router = APIRouter(prefix="/api/v1", tags=["Webhook Tokens"])


@router.get(
    "/webhook-tokens",
    response_model=list[schemas.WebhookToken_],
    summary="列出所有 webhook token",
    description="回傳所有 webhook token 的名稱、建立時間與狀態，不包含明文 token。",
)
def list_webhook_tokens(
    service: WebhookTokenService = Depends(depends_webhook_token_service),
):
    return service.list_tokens()


@router.post(
    "/webhook-tokens",
    response_model=schemas.WebhookTokenCreated,
    status_code=201,
    summary="建立 webhook token",
    description="產生新的 webhook token，回應中的明文 token 僅顯示一次。",
)
def create_webhook_token(
    payload: schemas.WebhookTokenCreate,
    service: WebhookTokenService = Depends(depends_webhook_token_service),
):
    plaintext, token = service.create_token(payload.name)
    return schemas.WebhookTokenCreated(
        id=token.id,
        name=token.name,
        created_at=token.created_at,
        revoked_at=token.revoked_at,
        token=plaintext,
    )


@router.delete(
    "/webhook-tokens/{token_id}",
    status_code=204,
    summary="撤銷 webhook token",
    description="將指定 token 標記為已撤銷，撤銷後該 token 立即失效。",
)
def revoke_webhook_token(
    token_id: str,
    service: WebhookTokenService = Depends(depends_webhook_token_service),
):
    token = service.revoke_token(token_id)
    if token is None:
        raise HTTPException(status_code=404, detail="找不到指定的 webhook token")


@router.delete(
    "/webhook-tokens/{token_id}/permanent",
    status_code=204,
    summary="永久刪除 webhook token",
    description="將已撤銷的 token 從資料庫完全刪除。僅允許刪除已撤銷的 token。",
)
def delete_webhook_token(
    token_id: str,
    service: WebhookTokenService = Depends(depends_webhook_token_service),
):
    token = service.get_token(token_id)
    if token is None:
        raise HTTPException(status_code=404, detail="找不到指定的 webhook token")
    if token.revoked_at is None:
        raise HTTPException(
            status_code=409, detail="僅能刪除已撤銷的 token，請先撤銷"
        )
    service.delete_token(token_id)
