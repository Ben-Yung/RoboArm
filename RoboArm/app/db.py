"""SQLite connection, schema bootstrap, and seed data."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from app.config import DB_PATH

# ---------- schema ----------

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS translations (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    key           TEXT    NOT NULL,
    zh_tw         TEXT    NOT NULL DEFAULT '',
    en            TEXT    NOT NULL DEFAULT '',
    zh_cn         TEXT    NOT NULL DEFAULT '',
    created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE(key)
);

CREATE INDEX IF NOT EXISTS idx_translations_key ON translations(key);

CREATE TABLE IF NOT EXISTS preferences (
    id            INTEGER PRIMARY KEY CHECK (id = 1),
    language      TEXT    NOT NULL DEFAULT 'zh_tw',
    font_size     INTEGER NOT NULL DEFAULT 14,
    font_family   TEXT    NOT NULL DEFAULT 'DFKai-SB 標楷體',
    updated_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);
"""


# ---------- seed ----------

SEED_TRANSLATIONS: list[tuple[str, str, str, str]] = [
    # ---- app / brand ----
    ("app.title", "RoboArm 機械臂控制系統", "RoboArm Control System", "RoboArm 机械臂控制系统"),
    ("app.subtitle", "V1.0 · 機械臂控制系統", "V1.0 · Robotic Arm Control System", "V1.0 · 机械臂控制系统"),
    ("app.version", "V1.0", "V1.0", "V1.0"),
    ("app.footer", "RoboArm © 2025", "RoboArm © 2025", "RoboArm © 2025"),

    # ---- top bar controls ----
    ("ui.language", "語言", "Language", "语言"),
    ("ui.font_size", "字體大小", "Font Size", "字体大小"),
    ("ui.font_family", "字體", "Font", "字体"),

    # ---- sidebar menu ----
    ("menu.dashboard", "主頁", "DashBoard", "主页"),
    ("menu.source", "來源資料表", "Source Table", "来源资料表"),
    ("menu.setting", "系統設定", "System Setting", "系统设定"),

    # ---- subtitles ----
    ("dashboard.subtitle", "主頁總覽", "Overview", "主页总览"),
    ("source.subtitle", "來源資料表管理", "Source Table Management", "来源资料表管理"),
    ("setting.subtitle", "系統設定", "System Setting", "系统设定"),

    # ---- placeholders ----
    ("placeholder.title", "此功能即將推出", "This feature is coming soon", "此功能即将推出"),
    ("placeholder.dashboard.desc", "DashBoard 將在後續版本提供。",
     "DashBoard will be available in a future release.",
     "DashBoard 将在后续版本提供。"),
    ("placeholder.source.desc", "Source Table 將在後續版本提供。",
     "Source Table will be available in a future release.",
     "Source Table 将在后续版本提供。"),
    ("placeholder.setting.desc", "System Setting 將在後續版本提供。",
     "System Setting will be available in a future release.",
     "System Setting 将在后续版本提供。"),
]


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


@contextmanager
def get_db() -> Iterator[sqlite3.Connection]:
    conn = _connect()
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    """Create tables, seed translations (only if empty), seed preferences."""
    with get_db() as conn:
        conn.executescript(SCHEMA_SQL)

        count = conn.execute("SELECT COUNT(*) AS n FROM translations").fetchone()["n"]
        if count == 0:
            conn.executemany(
                """
                INSERT INTO translations (key, zh_tw, en, zh_cn)
                VALUES (?, ?, ?, ?)
                """,
                SEED_TRANSLATIONS,
            )

        # Preferences always row id=1
        row = conn.execute("SELECT id FROM preferences WHERE id = 1").fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO preferences (id, language, font_size, font_family) "
                "VALUES (1, 'zh_tw', 14, 'DFKai-SB 標楷體')"
            )


# ---------- repositories ----------

class TranslationsRepo:
    @staticmethod
    def get_all(conn: sqlite3.Connection, *, language: str) -> dict[str, str]:
        """Return a flat {key: text} dict for the requested language, falling
        back to the default language when a translation is missing."""
        rows = conn.execute(
            "SELECT key, zh_tw, en, zh_cn FROM translations"
        ).fetchall()
        result: dict[str, str] = {}
        for r in rows:
            value = r[language] or ""
            if not value:
                # fall back to zh_tw
                value = r["zh_tw"] or r["en"] or r["zh_cn"] or r["key"]
            result[r["key"]] = value
        result["__active_lang__"] = language
        return result

    @staticmethod
    def upsert(conn: sqlite3.Connection, key: str, zh_tw: str, en: str, zh_cn: str) -> None:
        conn.execute(
            """
            INSERT INTO translations (key, zh_tw, en, zh_cn)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                zh_tw = excluded.zh_tw,
                en = excluded.en,
                zh_cn = excluded.zh_cn,
                updated_at = datetime('now')
            """,
            (key, zh_tw, en, zh_cn),
        )


class PreferencesRepo:
    @staticmethod
    def get(conn: sqlite3.Connection) -> dict:
        row = conn.execute(
            "SELECT language, font_size, font_family FROM preferences WHERE id = 1"
        ).fetchone()
        if row is None:
            return {"language": "zh_tw", "font_size": 14, "font_family": "DFKai-SB 標楷體"}
        return dict(row)

    @staticmethod
    def update(
        conn: sqlite3.Connection,
        *,
        language: str,
        font_size: int,
        font_family: str,
    ) -> None:
        conn.execute(
            """
            UPDATE preferences
               SET language = ?, font_size = ?, font_family = ?,
                   updated_at = datetime('now')
             WHERE id = 1
            """,
            (language, font_size, font_family),
        )


translations_repo = TranslationsRepo()
preferences_repo = PreferencesRepo()
