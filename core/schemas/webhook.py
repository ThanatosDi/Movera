from pydantic import BaseModel, Field


class QBittorrentPayload(BaseModel):
    """
    Represents the data sent from qBittorrent's "run external program" feature.
    """

    file_path: str = Field(
        ...,
        description="The content path of the downloaded torrent (%F in qBittorrent). For multi-file torrents, this is the root directory. For single-file torrents, this is the file path.",
        examples=["/downloads/[ANi] 被驅逐出勇者隊伍的白魔導師，被 S 級冒險者撿到 - 06 [1080P][Baha][WEB-DL][AAC AVC][CHT].mp4"],
    )
    category: str | None = Field(
        None, description="The category of the downloaded torrent.", examples=["Anime"]
    )
