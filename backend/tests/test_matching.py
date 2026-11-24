from app.main import extract_skills


def test_extracts_known_skills_case_insensitively():
    found = extract_skills("Built APIs with Python, FastAPI and PostgreSQL.")
    assert found == ["fastapi", "postgresql", "python"]


def test_does_not_match_partial_words():
    assert "java" not in extract_skills("JavaScript developer")


def test_unknown_text_returns_no_skills():
    assert extract_skills("A motivated candidate who enjoys learning") == []
