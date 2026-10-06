"""
Shared pytest fixtures.

- `sample_outputs`: parse tests/fixtures/dummydataoutput.txt (4 blok JSON hasil
  endpoint asli: /macro, /sectors, /stocks, /full-report) jadi dict per endpoint.
- `client`: FastAPI TestClient dengan dependency get_db di-override ke SQLite
  in-memory supaya test jalan tanpa Postgres/Redis/internet.
"""
import json
import re
from pathlib import Path

import pytest

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "dummydataoutput.txt"


def _parse_fixture() -> dict:
    """Parse file fixture: blok '/path\n{json}' berulang."""
    text = FIXTURE_PATH.read_text(encoding="utf-8")
    blocks = re.split(r"\n(?=/api/v1/)", text)
    out = {}
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        first_nl = block.index("\n")
        path = block[:first_nl].strip()
        payload = json.loads(block[first_nl:].strip())
        out[path] = payload
    return out


@pytest.fixture(scope="session")
def sample_outputs() -> dict:
    return _parse_fixture()
