#!/usr/bin/env python3
"""Copy the pre-rendered front page to the competition output path.

Stdlib only, no network.  Reads entry.png from this repository, writes it to
$MAKEFUN_OUTPUT_DIR or /output/entry.png, verifies the copy's sha256 against
the source, prints the digest, and exits 0.
"""

import hashlib
import os
import pathlib
import shutil
import sys


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    src = pathlib.Path(__file__).resolve().parent / "entry.png"
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    out = pathlib.Path(out_dir) / "entry.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, out)
    a, b = sha256(src), sha256(out)
    if a != b:
        print("sha256 mismatch: %s != %s" % (a, b))
        return 1
    print(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())