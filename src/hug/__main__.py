"""Application entry point."""
import logging
import sys
from pathlib import Path

# Add src to path if running directly
src_path = Path(__file__).resolve().parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from hug.app import HugApp


def setup_logging():
    """Configure basic logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    setup_logging()
    app = HugApp(sys.argv)
    sys.exit(app.run())


if __name__ == "__main__":
    main()
