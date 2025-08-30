from pydantic import BaseModel, Field


class QBittorrentPayload(BaseModel):
    """
    Represents the data sent from qBittorrent's "run external program" feature.
    """

    filepath: str = Field(
        ...,
        description="下載的種子檔案的內容路徑（qBittorrent 中為 %F）。對於多文件種子文件，此路徑為根目錄。對於單一文件種子文件，此路徑為文件路徑。",
        examples=[
            "/downloads/[ANi] 被驅逐出勇者隊伍的白魔導師，被 S 級冒險者撿到 - 06 [1080P][Baha][WEB-DL][AAC AVC][CHT].mp4"
        ],
    )
    category: str | None = Field(
        None, description="下載的種子的類別（qBittorrent 中為 %C）", examples=["Anime"]
    )
    tags: str | None = Field(
        None,
        description="下載的種子的標籤（qBittorrent 中為 %L）。如果有多個標籤，則以逗號分隔。",
        examples=["tag1,tag2"],
    )
