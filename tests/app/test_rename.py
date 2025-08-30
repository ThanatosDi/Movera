from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from app.modules.rename import ParseRenameRule, RegexRenameRule, Rename


@pytest.fixture
def filepath(tmp_path: Path) -> Path:
    return "H:/Downloads/anime/[ANi]公爵千金的家庭教師 - 01 [1080p][CHT].mp4"


def test_regex_rename_rule(mocker: MockerFixture, filepath: Path):
    src_rule = "(.+公爵千金的家庭教師 - )(\\d{2})( .+)\\.mp4"
    dst_rule = "\\1S01E\\2\\3.mp4"

    expected_new_path = Path(
        "H:/Downloads/anime/[ANi]公爵千金的家庭教師 - S01E01 [1080p][CHT].mp4"
    )
    rename_mock = mocker.patch(
        "app.modules.rename.Path.rename", return_value=expected_new_path
    )

    renamer = RegexRenameRule(filepath=filepath, src=src_rule, dst=dst_rule)
    new_path = renamer.rename()

    assert new_path == expected_new_path
    rename_mock.assert_called_once_with(Path(filepath), expected_new_path)


def test_parse_rename_rule(mocker: MockerFixture, filepath: Path):
    src_rule = "[{fansub}]{title} - {episode} {tags}.mp4"
    dst_rule = "[{fansub}]{title} - S01E{episode} {tags}.mp4"

    expected_new_path = Path(
        "H:/Downloads/anime/[ANi]公爵千金的家庭教師 - S01E01 [1080p][CHT].mp4"
    )
    rename_mock = mocker.patch(
        "app.modules.rename.Path.rename", return_value=expected_new_path
    )

    renamer = ParseRenameRule(filepath=filepath, src=src_rule, dst=dst_rule)
    new_path = renamer.rename()

    assert new_path == expected_new_path
    rename_mock.assert_called_once_with(Path(filepath), expected_new_path)


def test_rename_dispatcher_with_regex(mocker: MockerFixture, filepath: Path):
    """測試 Rename 類別在 regex 規則下的分派與呼叫。"""
    src_rule = "(.+公爵千金的家庭教師 - )(\\d{2})( .+)\\.mp4"
    dst_rule = "\\1S01E\\2\\3.mp4"

    expected_new_path = Path(
        "H:/Downloads/anime/[ANi]公爵千金的家庭教師 - S01E01 [1080p][CHT].mp4"
    )
    rename_mock = mocker.patch(
        "app.modules.rename.Path.rename", return_value=expected_new_path
    )

    renamer = Rename(filepath=filepath, src=src_rule, dst=dst_rule, rule="regex")
    new_path = renamer.execute_rename()

    assert new_path == expected_new_path
    rename_mock.assert_called_once_with(Path(filepath), expected_new_path)


def test_rename_dispatcher_with_parse(mocker: MockerFixture, filepath: Path):
    """測試 Rename 類別在 parse 規則下的分派與呼叫。"""
    src_rule = "[{fansub}]{title} - {episode} {tags}.mp4"
    dst_rule = "[{fansub}]{title} - S01E{episode} {tags}.mp4"

    expected_new_path = Path(
        "H:/Downloads/anime/[ANi]公爵千金的家庭教師 - S01E01 [1080p][CHT].mp4"
    )
    rename_mock = mocker.patch(
        "app.modules.rename.Path.rename", return_value=expected_new_path
    )

    renamer = Rename(filepath=filepath, src=src_rule, dst=dst_rule, rule="parse")
    new_path = renamer.execute_rename()

    assert new_path == expected_new_path
    rename_mock.assert_called_once_with(Path(filepath), expected_new_path)


def test_rename_invalid_rule(filepath: Path):
    """測試 Rename 類別在無效規則下的錯誤處理。"""
    src_rule = "invalid_rule"
    dst_rule = "invalid_rule"

    with pytest.raises(ValueError):
        Rename(
            filepath=filepath, src=src_rule, dst=dst_rule, rule="invalid_rule"
        ).execute_rename()
