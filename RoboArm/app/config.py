"""RoboArm application configuration."""
from __future__ import annotations

from pathlib import Path

# Project root = .../RoboArm (the directory this file's parent's parent is in)
ROOT_DIR = Path(__file__).resolve().parent.parent
APP_DIR = ROOT_DIR / "app"
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "RoboArm.db"

DATA_DIR.mkdir(parents=True, exist_ok=True)

# UI defaults
DEFAULT_LANGUAGE = "zh_tw"
DEFAULT_FONT_SIZE = 14
DEFAULT_FONT_FAMILY = "DFKai-SB"

SUPPORTED_LANGUAGES = ("zh_tw", "en", "zh_cn")

HOST = "0.0.0.0"
PORT = 8000
