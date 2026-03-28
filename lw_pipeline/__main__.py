"""Module execution entry point for lw_pipeline."""

# Authors: The Lightweight Pipeline developers
# SPDX-License-Identifier: BSD-3-Clause

def main():
    """Compatibility wrapper for entry points importing lw_pipeline.__main__.main."""
    from lw_pipeline.main import main as _main

    _main()


if __name__ == "__main__":
    main()
