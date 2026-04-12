from pathlib import Path


def validate_path_within(path: str | Path, allowed_bases: list[str | Path]) -> bool:
    """驗證路徑經過 resolve 後是否位於任一允許的基底目錄內。

    Why: 集中式路徑穿越防護，供 SPA 路由、Webhook worker、
    Task service 統一呼叫，確保一致性。

    Args:
        path: 待驗證的路徑
        allowed_bases: 允許的基底目錄列表

    Returns:
        True 如果路徑位於任一基底目錄內，否則 False
    """
    resolved = Path(path).resolve()
    for base in allowed_bases:
        base_resolved = Path(base).resolve()
        try:
            resolved.relative_to(base_resolved)
            return True
        except ValueError:
            continue
    return False


def sanitize_filename(name: str) -> str:
    """驗證檔名不含路徑穿越字元。

    拒絕含有 '..'、'/'、'\\' 或空字串的檔名。

    Args:
        name: 待驗證的檔名

    Returns:
        驗證通過的原始檔名

    Raises:
        ValueError: 檔名不合法時
    """
    if not name:
        raise ValueError("檔名不可為空")
    if ".." in name:
        raise ValueError(f"檔名含有不合法的路徑穿越字元: {name!r}")
    if "/" in name or "\\" in name:
        raise ValueError(f"檔名含有不合法的路徑分隔符: {name!r}")
    return name
