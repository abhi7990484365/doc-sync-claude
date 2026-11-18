"""Allow `python -m doc_sync`."""

import sys

from doc_sync.cli import main

if __name__ == "__main__":
    sys.exit(main())
