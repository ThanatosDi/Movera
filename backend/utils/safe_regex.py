"""安全正則表達式工具模組。

Why: 使用者提供的正則表達式可能包含惡意 pattern（如 `(a+)+b`），
導致 catastrophic backtracking 造成 CPU 耗盡。此模組透過長度限制
與執行逾時保護，防止 ReDoS 攻擊。
"""

import multiprocessing
import re

_DEFAULT_MAX_LENGTH = 500
_DEFAULT_TIMEOUT = 3  # 秒


class RegexTimeoutError(ValueError):
    """正則表達式執行逾時例外。

    Why: 繼承 ValueError 讓既有的錯誤處理程式碼可以自然捕獲。
    """

    def __init__(self, timeout: float):
        super().__init__(f"正則表達式執行逾時（超過 {timeout} 秒），可能包含惡意 pattern")
        self.timeout = timeout


def safe_compile(
    pattern: str,
    flags: int = re.IGNORECASE,
    max_length: int = _DEFAULT_MAX_LENGTH,
) -> re.Pattern:
    """編譯正則表達式，加入長度限制。

    Raises:
        ValueError: pattern 長度超過上限。
        re.error: pattern 語法無效。
    """
    if len(pattern) > max_length:
        raise ValueError(f"正則表達式長度超過上限 {max_length} 字元")
    return re.compile(pattern, flags)


def _worker_search(pattern_str: str, flags: int, string: str, conn):
    """子行程中執行 re.search 並回傳結果。"""
    try:
        compiled = re.compile(pattern_str, flags)
        match = compiled.search(string)
        if match:
            conn.send(("match", match.group(0), match.groups(), match.groupdict(), match.start(), match.end()))
        else:
            conn.send(("none",))
    except Exception as e:
        conn.send(("error", str(e)))
    finally:
        conn.close()


def _worker_sub(pattern_str: str, flags: int, repl: str, string: str, conn):
    """子行程中執行 re.sub 並回傳結果。"""
    try:
        compiled = re.compile(pattern_str, flags)
        result = compiled.sub(repl, string)
        conn.send(("result", result))
    except Exception as e:
        conn.send(("error", str(e)))
    finally:
        conn.close()


class _MatchProxy:
    """模擬 re.Match 的最小介面，讓呼叫端無需修改。"""

    def __init__(self, full_match: str, groups: tuple, groupdict: dict, start: int, end: int):
        self._full_match = full_match
        self._groups = groups
        self._groupdict = groupdict
        self._start = start
        self._end = end

    def group(self, n: int = 0) -> str | None:
        if n == 0:
            return self._full_match
        if 1 <= n <= len(self._groups):
            return self._groups[n - 1]
        return None

    def groups(self) -> tuple:
        return self._groups

    def groupdict(self) -> dict:
        return self._groupdict

    def start(self) -> int:
        return self._start

    def end(self) -> int:
        return self._end


def safe_search(
    pattern: re.Pattern,
    string: str,
    timeout: float = _DEFAULT_TIMEOUT,
) -> _MatchProxy | None:
    """在逾時保護下執行 re.search。

    透過子行程執行，確保 GIL 不會阻擋逾時。回傳 _MatchProxy 物件
    模擬 re.Match 的 group()/groups()/groupdict() 介面。

    Raises:
        RegexTimeoutError: 執行逾時。
    """
    parent_conn, child_conn = multiprocessing.Pipe()
    proc = multiprocessing.Process(
        target=_worker_search,
        args=(pattern.pattern, pattern.flags, string, child_conn),
    )
    proc.start()
    proc.join(timeout=timeout)

    if proc.is_alive():
        proc.kill()
        proc.join()
        raise RegexTimeoutError(timeout)

    if parent_conn.poll():
        data = parent_conn.recv()
        if data[0] == "match":
            _, full_match, groups, groupdict, start, end = data
            return _MatchProxy(full_match, groups, groupdict, start, end)
        elif data[0] == "error":
            raise re.error(data[1])
        else:
            return None
    return None


def safe_sub(
    pattern: re.Pattern,
    repl: str,
    string: str,
    timeout: float = _DEFAULT_TIMEOUT,
) -> str:
    """在逾時保護下執行 re.sub。

    透過子行程執行，確保 GIL 不會阻擋逾時。

    Raises:
        RegexTimeoutError: 執行逾時。
    """
    parent_conn, child_conn = multiprocessing.Pipe()
    proc = multiprocessing.Process(
        target=_worker_sub,
        args=(pattern.pattern, pattern.flags, repl, string, child_conn),
    )
    proc.start()
    proc.join(timeout=timeout)

    if proc.is_alive():
        proc.kill()
        proc.join()
        raise RegexTimeoutError(timeout)

    if parent_conn.poll():
        data = parent_conn.recv()
        if data[0] == "result":
            return data[1]
        elif data[0] == "error":
            raise re.error(data[1])

    return string
