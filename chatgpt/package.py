#!/usr/bin/env python3
"""Build an asset-free, deterministic portable plugin ZIP outside this folder."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import zipfile

FILES = ("plugin.json", "mcp.json", "README.md", "skills/kural-dry-run/SKILL.md")


def package(output: Path) -> dict:
    root = Path(__file__).resolve().parent
    output = output.expanduser().resolve()
    if output == root or root in output.parents:
        raise ValueError("ZIP output must be outside the plugin folder")
    if output.suffix != ".zip":
        raise ValueError("ZIP output must end in .zip")
    if not output.parent.is_dir():
        raise ValueError("ZIP output parent directory must already exist")
    # Read the complete allowlist first; never package assets or unknown files.
    entries = []
    for name in sorted(FILES):
        source = root / name
        if source.is_symlink() or source.resolve() != source:
            raise ValueError(f"Symlinks are not accepted: {name}")
        entries.append((name, source.read_bytes()))
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, content in entries:
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content)
    return {"output": str(output), "files": [name for name, _ in entries],
            "sha256": sha256(output.read_bytes()).hexdigest()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path,
                        help="ZIP file outside this plugin folder; existing file is replaced")
    args = parser.parse_args()
    try:
        print(json.dumps(package(args.output), indent=2))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
