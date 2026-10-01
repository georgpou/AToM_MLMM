"""Deterministic, finite JSON artifacts with atomic replacement."""
import json
import os
from pathlib import Path
import tempfile


def write_json(path, document):
    text = json.dumps(document, indent=2, sort_keys=True, allow_nan=False) + '\n'
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                         delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(text)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def read_json(path):
    def reject_constant(value):
        raise ValueError(f'nonfinite JSON constant: {value}')
    return json.loads(Path(path).read_text(), parse_constant=reject_constant)
