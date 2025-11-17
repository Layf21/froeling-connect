import json
from pathlib import Path

import pytest


@pytest.fixture
def load_json():
    """Load captured JSON responses from tests/responses/."""

    def _loader(name: str):
        path = Path(__file__).parent / 'responses' / name
        with open(path, encoding='utf-8') as f:
            return json.load(f)

    return _loader
