import asyncio
from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile

from app.services.parsing import decode_text, extract_input_text, read_limited


def make_upload(filename: str, content: bytes) -> UploadFile:
    return UploadFile(filename=filename, file=BytesIO(content))


def test_pasted_text_is_preferred_and_normalized_without_a_file():
    content, source_type, filename = asyncio.run(extract_input_text("  First\r\n\r\n\r\n Second  ", None))

    assert content == "First\n\nSecond"
    assert source_type == "text"
    assert filename is None


def test_txt_upload_decodes_utf8_bom_and_preserves_filename():
    upload = make_upload("resume.txt", b"\xef\xbb\xbfFirst\r\n\r\n\r\nSecond")

    content, source_type, filename = asyncio.run(extract_input_text(None, upload))

    assert content == "First\n\nSecond"
    assert source_type == "txt"
    assert filename == "resume.txt"


def test_read_limited_returns_only_the_limit_sentinel_byte():
    upload = make_upload("resume.txt", b"abcdef")

    content = asyncio.run(read_limited(upload, limit=3, chunk_size=2))

    assert content == b"abcd"


def test_decode_text_falls_back_to_cp1252_for_legacy_uploads():
    assert decode_text(b"Ren\xe9") == "René"


@pytest.mark.parametrize(
    ("filename", "content", "expected_detail"),
    [
        ("resume.docx", b"content", "Only .txt and .pdf"),
        ("resume.txt", b"", "empty or could not be parsed"),
    ],
)
def test_invalid_uploads_return_clear_validation_errors(filename: str, content: bytes, expected_detail: str):
    with pytest.raises(HTTPException) as error:
        asyncio.run(extract_input_text(None, make_upload(filename, content)))

    assert error.value.status_code == 400
    assert expected_detail in error.value.detail
