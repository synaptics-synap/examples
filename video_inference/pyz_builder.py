"""
Generate .pyz archive for demo or examples
"""

from os import getcwd
from pathlib import Path
from shutil import copy2
from tempfile import TemporaryDirectory
import argparse
import zipapp


if __name__ == "__main__":
    cwd: Path = Path(getcwd())
    examples: list[str] = [f.name for f in Path(cwd / "examples").glob("*.py")]
    parser = argparse.ArgumentParser(description=__doc__)
    t_group = parser.add_mutually_exclusive_group(required=True)
    t_group.add_argument(
        "--all",
        action="store_true",
        default=False,
        help="Build all demos"
    )
    t_group.add_argument(
        "-t", "--targets",
        type=str,
        nargs="+",
        metavar="DEMO",
        default=["demo.py"],
        choices=["demo.py", *examples],
        help="Which demo(s) to build ([default] %(choices)s)"
    )
    parser.add_argument(
        "-o", "--output_dir",
        type=str,
        default=f"{getcwd()}/build",
        metavar="DIR",
        help="Output directory for builds (default: %(default)s)"
    )
    args = parser.parse_args()

    if not (output_dir := Path(args.output_dir)).exists():
        output_dir.mkdir(parents=True)

    targets: list[str] = ["demo.py", *examples] if args.all else args.targets
    for target in targets:
        with TemporaryDirectory() as td:
            td = Path(td) / "demo-python"
            for f in Path(".").rglob("*"):
                if str(f.resolve()) == __file__:
                    continue
                if f.resolve() == cwd / "demo.py":
                    continue
                if cwd / f.parent == cwd / "examples":
                    continue
                if f.suffix == ".py":
                    dst = td / f.parent
                    dst.mkdir(parents=True, exist_ok=True)
                    copy2(f, dst)
            target_src: Path = cwd / target if target == "demo.py" else cwd / "examples" / target
            copy2(target_src, td / "__main__.py")
            zipapp.create_archive(td, f"{output_dir}/{Path(target).stem}.pyz")
            print(f"Built {output_dir.resolve()}/{Path(target).stem}.pyz")
