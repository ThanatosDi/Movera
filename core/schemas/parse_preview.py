from pydantic import BaseModel, Field


# Pydantic 模型，用於定義請求主體的結構
class ParsePreviewRequest(BaseModel):
    """Parse 預覽請求的模型"""

    src_pattern: str = Field(
        ...,
        description="用於解析的模式字串",
        json_schema_extra={
            "example": "{en_title} - {cht_title} - {episode} {tags}.mp4"
        },
    )
    text: str = Field(
        ...,
        description="要被解析的文字",
        json_schema_extra={
            "example": "Neko ni Tensei Shita Ojisan S02 - 轉生為第七王子，隨心所欲的魔法學習之路 第二季 - 13 [1080P][Baha][WEB-DL][AAC AVC][CHT].mp4"
        },
    )
    dst_pattern: str = Field(
        ...,
        description="用於產生新字串的格式化字串",
        json_schema_extra={
            "example": "{en_title} - {cht_title} - S02E{episode} {tags}.mp4"
        },
    )


class ParsePreviewResponse(ParsePreviewRequest):
    groups: dict[str, str] = Field(
        ...,
        description="解析後的分組結果",
        json_schema_extra={
            "example": {
                "en_title": "Neko ni Tensei Shita Ojisan S02",
                "cht_title": "轉生為第七王子，隨心所欲的魔法學習之路 第二季",
                "episode": "13",
                "tags": "[1080P][Baha][WEB-DL][AAC AVC][CHT]",
            }
        },
    )

    formatted: str = Field(
        ...,
        description="格式化後的預覽結果",
        json_schema_extra={
            "example": "Neko ni Tensei Shita Ojisan S02 - 轉生為第七王子，隨心所欲的魔法學習之路 第二季 - S02E13 [1080P][Baha][WEB-DL][AAC AVC][CHT].mp4"
        },
    )
