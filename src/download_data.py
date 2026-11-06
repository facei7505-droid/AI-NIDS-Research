"""Download verifiable UNSW-NB15 split mirrors, never overwrite silently.

Source is a publicly hosted mirror of the two officially defined split CSVs.
Mirror is not UNSW itself. License/citation: see official UNSW dataset page.
"""
from __future__ import annotations
import argparse
import hashlib
import urllib.request
from pathlib import Path

SOURCE = "https://huggingface.co/datasets/Mouwiya/UNSW-NB15-small/resolve/main"
DATASETS = {
    "UNSW_NB15_training-set.csv": "bec7dd5ec88dc2a0ccc7a07879d338395ed7421750f675fd0339e07dfe0648fa",
    "UNSW_NB15_testing-set.csv": "734fe6642edf758f7c94d7d9149426b49d202fe8e7bf0bef47392489c3c0a559",
}


def filehash(path):
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def get_data(directory):
    directory.mkdir(parents=True, exist_ok=True)
    for name, expected in DATASETS.items():
        dest = directory / name
        if dest.is_file() and filehash(dest) == expected:
            print(f"Verified existing: {name}")
            continue
        if dest.exists():
            raise ValueError(f"Unexpected existing data: {dest}; refusing to overwrite")
        temporary = directory / f"{name}.partial"
        try:
            request = urllib.request.Request(SOURCE + "/" + name + "?download=true",
                                             headers={"User-Agent": "AI-NIDS-Research/1.0"})
            with urllib.request.urlopen(request, timeout=120) as response, temporary.open("wb") as output:
                while True:
                    block = response.read(1024 * 1024)
                    if not block:
                        break
                    output.write(block)
            actual = filehash(temporary)
            if actual != expected:
                raise ValueError(f"SHA256 mismatch for {name}: got {actual}, expected {expected}")
            temporary.rename(dest)
            print(f"Downloaded and verified: {name}, SHA256={actual}")
        finally:
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    args = parser.parse_args()
    get_data(args.data_dir)


if __name__ == "__main__":
    main()
