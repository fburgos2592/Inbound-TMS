"""Unit tests for the PlantUML encoding and URL-building helpers.

These tests exercise pure functions only (no Streamlit, no network).
"""

import pytest

from inbound_tms_diagram_app import plantuml_encode, plantuml_url

# ---------------------------------------------------------------------------
# plantuml_encode
# ---------------------------------------------------------------------------

_PLANTUML_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"

TINY_DIAGRAM = "@startuml\nA -> B\n@enduml"
TINY_ENCODED = "SoWkIImgAStDuN9KqBLJSE9oICrB0N81"


def test_encode_known_value():
    """Encoding must be deterministic and match a pre-computed reference."""
    assert plantuml_encode(TINY_DIAGRAM) == TINY_ENCODED


def test_encode_idempotent():
    """Encoding the same text twice must produce the same result."""
    assert plantuml_encode(TINY_DIAGRAM) == plantuml_encode(TINY_DIAGRAM)


def test_encode_output_uses_plantuml_alphabet():
    """Every character in the encoded output must belong to the PlantUML alphabet."""
    encoded = plantuml_encode(TINY_DIAGRAM)
    for ch in encoded:
        assert ch in _PLANTUML_ALPHABET, f"Unexpected character {ch!r} in encoded output"


def test_encode_nonempty_for_nonempty_input():
    """Non-empty PlantUML text must produce a non-empty encoded string."""
    assert len(plantuml_encode(TINY_DIAGRAM)) > 0


def test_encode_different_inputs_produce_different_outputs():
    """Two different diagrams must not collide to the same encoded string."""
    other = "@startuml\nB -> A\n@enduml"
    assert plantuml_encode(TINY_DIAGRAM) != plantuml_encode(other)


# ---------------------------------------------------------------------------
# plantuml_url
# ---------------------------------------------------------------------------

SERVER = "https://www.plantuml.com/plantuml"


def test_url_svg_format():
    url = plantuml_url(SERVER, "svg", TINY_DIAGRAM)
    assert url.startswith(f"{SERVER}/svg/")
    assert TINY_ENCODED in url


def test_url_png_format():
    url = plantuml_url(SERVER, "png", TINY_DIAGRAM)
    assert url.startswith(f"{SERVER}/png/")
    assert TINY_ENCODED in url


def test_url_strips_trailing_slash_from_server():
    url = plantuml_url(SERVER + "/", "svg", TINY_DIAGRAM)
    assert "//" not in url.replace("https://", "")


def test_url_case_insensitive_format():
    """fmt should be normalised to lowercase."""
    url = plantuml_url(SERVER, "SVG", TINY_DIAGRAM)
    assert "/svg/" in url


def test_url_invalid_format_raises():
    with pytest.raises(ValueError, match="fmt must be"):
        plantuml_url(SERVER, "gif", TINY_DIAGRAM)


def test_url_invalid_format_pdf_raises():
    with pytest.raises(ValueError):
        plantuml_url(SERVER, "pdf", TINY_DIAGRAM)
