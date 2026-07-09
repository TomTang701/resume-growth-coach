from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_bilingual_handoff_documents_have_required_pairs_and_sections():
    pairs = (
        ("DEVELOPMENT_LOG.md", "DEVELOPMENT_LOG.zh-CN.md", "Development Log", "开发日志"),
        ("TEST_LOG.md", "TEST_LOG.zh-CN.md", "Adversarial Test Log", "刁钻测试日志"),
        ("HANDOFF.md", "HANDOFF.zh-CN.md", "Developer Handoff", "开发交接"),
    )

    for english_name, chinese_name, english_heading, chinese_heading in pairs:
        english = (ROOT / "docs" / english_name).read_text(encoding="utf-8")
        chinese = (ROOT / "docs" / chinese_name).read_text(encoding="utf-8")

        assert english.startswith(f"# {english_heading}")
        assert chinese.startswith(f"# {chinese_heading}")
        assert len(english) > 500
        assert len(chinese) > 500

        if english_name != "TEST_LOG.md":
            assert "P0" in english and "P1" in english and "P2" in english
            assert "P0" in chinese and "P1" in chinese and "P2" in chinese
