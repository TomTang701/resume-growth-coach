import pytest

from tools.browser_smoke import resolve_browser_name


@pytest.mark.parametrize("value", ["chromium", "firefox", "webkit"])
def test_resolve_browser_name_accepts_supported_engines(value: str) -> None:
    assert resolve_browser_name(value) == value


def test_resolve_browser_name_rejects_unknown_engine() -> None:
    with pytest.raises(ValueError, match="Unsupported browser"):
        resolve_browser_name("safari")
