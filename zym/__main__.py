"""Allow ``python -m zym`` to launch the interpreter."""

from zym.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
