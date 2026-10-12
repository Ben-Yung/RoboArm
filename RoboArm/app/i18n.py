"""i18n translator builder.

The `translations` table in `data/RoboArm.db` is the single source of
truth for UI text. ``TranslationsRepo.get_all`` returns a flat
``{key: text}`` dict for the active language, falling back per-row to
``zh_tw`` whenever a translation is missing. This module wraps that
dict in a ``t(key)`` callable that templates use via
``{{ t("menu.dashboard") }}``.
"""
from __future__ import annotations

from typing import Callable, Mapping


def build_translator(
    translations: Mapping[str, str],
    fallback_language: str = "zh_tw",
) -> Callable[[str], str]:
    """Return a ``t(key) -> str`` closure backed by a flat lookup table.

    The active language is read from the ``__active_lang__`` sentinel
    that ``TranslationsRepo.get_all`` inserts. The ``fallback_language``
    argument is accepted for API compatibility but the repository
    already collapses per-row fallbacks, so the closure is a direct
    dict lookup with a final ``key`` passthrough.
    """
    del fallback_language  # see docstring — kept for API compatibility.
    table: dict[str, str] = dict(translations or {})

    def t(key: str) -> str:
        if not isinstance(key, str):
            return key  # type: ignore[return-value]
        if key in table:
            return table[key]
        return key  # missing key → render the key itself, no crash.

    return t
