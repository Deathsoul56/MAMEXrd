#!/usr/bin/env python3
"""Package a built MAMEXrd.exe into a release-ready zip for MAMEXrd.

Usage (from repo root, after building with Nuitka into ./build):
    python scripts/package_release.py
    python scripts/package_release.py --version 0.1 --build-dir build

The resulting archive contains only what's needed to run the frontend on a
clean machine: MAMEXrd is a Nuitka --onefile build (self-contained, no Qt
DLLs to deploy) that must simply be dropped next to mame.exe.
"""

import argparse
import re
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

BUILD_CMD = (
    "python -m nuitka --standalone --onefile --enable-plugin=pyqt6 "
    "--windows-console-mode=disable --windows-icon-from-ico=resources\\MAMEX.ico "
    "--output-dir=build --output-filename=MAMEXrd.exe --assume-yes-for-downloads main.py"
)


def detect_version() -> str:
    about_dialog = REPO_ROOT / "ui" / "about_dialog.py"
    text = about_dialog.read_text(encoding="utf-8")
    match = re.search(r'MAMEXRD_VERSION\s*=\s*"v?([^"]+)"', text)
    if not match:
        raise SystemExit(f"Could not find MAMEXRD_VERSION in {about_dialog}")
    return match.group(1)


def find_exe(build_dir: Path) -> Path:
    candidate = build_dir / "MAMEXrd.exe"
    if candidate.is_file():
        return candidate
    raise SystemExit(
        f"Could not find MAMEXrd.exe in {build_dir}. Build it first with:\n"
        f"  {BUILD_CMD}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default=None, help="Release version (default: read from ui/about_dialog.py)")
    parser.add_argument("--build-dir", default="build", help="Nuitka output directory (default: build)")
    parser.add_argument("--arch", default="win64", help="Archive name suffix (default: win64)")
    args = parser.parse_args()

    version = args.version or detect_version()
    build_dir = (REPO_ROOT / args.build_dir).resolve()
    exe_path = find_exe(build_dir)

    staging_name = f"MAMEXrd-v{version}-{args.arch}"
    staging_dir = REPO_ROOT / staging_name
    if staging_dir.exists():
        try:
            shutil.rmtree(staging_dir)
        except PermissionError as exc:
            raise SystemExit(
                f"Could not remove {staging_dir} ({exc}).\n"
                "Close MAMEXrd.exe and any Explorer/zip window with that "
                "folder open, then try again."
            ) from exc
    staging_dir.mkdir(parents=True)

    shutil.copy2(exe_path, staging_dir / exe_path.name)
    shutil.copy2(REPO_ROOT / "LICENSE", staging_dir / "LICENSE")
    shutil.copy2(REPO_ROOT / "CHANGES.md", staging_dir / "CHANGES.md")

    archive_path = shutil.make_archive(str(staging_dir), "zip", root_dir=REPO_ROOT, base_dir=staging_name)

    print(f"Packaged: {archive_path}")


if __name__ == "__main__":
    main()
