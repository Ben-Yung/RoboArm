"""RoboArm V1.0 — Phase I main entry.

FastAPI + Jinja2 + Vanilla JS. Sidebar layout with three placeholder
pages (DashBoard, Source Table, System Setting). UI strings live in
the SQLite `translations` table; user preferences (language, font
family, font size) live in the `preferences` table.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import (
    APP_DIR,
    DEFAULT_FONT_FAMILY,
    DEFAULT_FONT_SIZE,
    DEFAULT_LANGUAGE,
    HOST,
    PORT,
    SUPPORTED_LANGUAGES,
)
from app.db import get_db, init_db, preferences_repo, translations_repo
from app.i18n import build_translator

# Translations are resolved per-request. We attach a `t(key)` callable
# to Jinja so templates can write {{ t("menu.dashboard") }}.

# Sidebar menu items (single source of truth for routes + i18n keys).
MENU: list[dict[str, str]] = [
    {"key": "dashboard", "url": "/dashboard", "icon": "📊"},
    {"key": "source", "url": "/source", "icon": "🗂️"},
    {"key": "setting", "url": "/setting", "icon": "⚙️"},
]

FONT_OPTIONS: list[dict[str, str]] = [
    {"name": "DFKai-SB 標楷體", "css": '"DFKai-SB", "BiauKai", "標楷體", "Microsoft JhengHei", "PingFang TC", "Noto Sans TC", serif'},
    {"name": "Microsoft JhengHei 微軟正黑體", "css": '"Microsoft JhengHei", "PingFang TC", "Noto Sans TC", sans-serif'},
    {"name": "PingFang TC 蘋方-繁", "css": '"PingFang TC", "Microsoft JhengHei", "Noto Sans TC", sans-serif'},
    {"name": "Noto Sans TC 思源黑體", "css": '"Noto Sans TC", "Microsoft JhengHei", "PingFang TC", sans-serif'},
    {"name": "PMingLiU 新細明體", "css": '"PMingLiU", "MingLiU", "SimSun", serif'},
    {"name": "MingLiU 細明體", "css": '"MingLiU", "PMingLiU", "SimSun", serif'},
]

LANGUAGE_OPTIONS: list[dict[str, str]] = [
    {"code": "zh_tw", "label": "繁體中文"},
    {"code": "en", "label": "English"},
    {"code": "zh_cn", "label": "简体中文"},
]


def _css_to_name(css_value: str) -> str:
    """Find the friendly name matching the current CSS font-family value."""
    for opt in FONT_OPTIONS:
        if opt["css"] == css_value:
            return opt["name"]
    return css_value


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="RoboArm V1.0", version="1.0.0", lifespan=lifespan)

app.mount(
    "/static",
    StaticFiles(directory=str(APP_DIR / "static")),
    name="static",
)

templates = Jinja2Templates(directory=str(APP_DIR / "templates"))


def _decode_cookie(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        from urllib.parse import unquote
        return unquote(value)
    except Exception:
        return value


def _resolve_lang(request: Request) -> str:
    """Language precedence: query ?lang= > cookie > preference > default."""
    qp_lang = request.query_params.get("lang")
    if qp_lang in SUPPORTED_LANGUAGES:
        return qp_lang
    cookie_lang = _decode_cookie(request.cookies.get("roboarm_lang"))
    if cookie_lang in SUPPORTED_LANGUAGES:
        return cookie_lang
    with get_db() as conn:
        pref = preferences_repo.get(conn)
    if pref["language"] in SUPPORTED_LANGUAGES:
        return pref["language"]
    return DEFAULT_LANGUAGE


def _resolve_prefs(language: str) -> dict[str, Any]:
    with get_db() as conn:
        pref = preferences_repo.get(conn)
    return {
        "language": language,
        "font_size": int(pref["font_size"]) if pref.get("font_size") is not None else DEFAULT_FONT_SIZE,
        "font_family": pref["font_family"] or DEFAULT_FONT_FAMILY,
    }


def _render(
    request: Request,
    template_name: str,
    *,
    page_key: str,
    context: dict[str, Any] | None = None,
    status_code: int = 200,
) -> HTMLResponse:
    ctx: dict[str, Any] = dict(context or {})
    language = ctx.pop("__language", None) or _resolve_lang(request)
    prefs = _resolve_prefs(language)

    with get_db() as conn:
        translations = translations_repo.get_all(conn, language=language)
        active_lang_row = translations.get("__active_lang__")
    if not active_lang_row:
        # First-load fallback: language column itself.
        active_lang_row = language

    t = build_translator(translations, fallback_language=DEFAULT_LANGUAGE)
    font_family_css = next(
        (opt["css"] for opt in FONT_OPTIONS if opt["name"] == prefs["font_family"]),
        FONT_OPTIONS[0]["css"],
    )

    rendered = templates.TemplateResponse(
        request,
        template_name,
        {
            "t": t,
            "active_lang": active_lang_row,
            "menu": MENU,
            "page_key": page_key,
            "font_size": prefs["font_size"],
            "font_family": prefs["font_family"],
            "font_family_css": font_family_css,
            "font_options": FONT_OPTIONS,
            "language_options": LANGUAGE_OPTIONS,
            "language": language,
            **ctx,
        },
        status_code=status_code,
    )
    # Cookie mirrors the language so it survives across tabs.
    rendered.set_cookie(
        "roboarm_lang",
        language,
        max_age=60 * 60 * 24 * 365,
        samesite="lax",
    )
    return rendered


def _set_prefs_response(
    *,
    response: Response,
    language: str,
    font_size: int,
    font_family_name: str,
) -> None:
    from urllib.parse import quote

    response.set_cookie("roboarm_lang", language, max_age=60 * 60 * 24 * 365, samesite="lax")
    response.set_cookie("roboarm_font_size", str(font_size), max_age=60 * 60 * 24 * 365, samesite="lax")
    response.set_cookie(
        "roboarm_font_family",
        quote(font_family_name, safe=""),
        max_age=60 * 60 * 24 * 365,
        samesite="lax",
    )
    with get_db() as conn:
        preferences_repo.update(
            conn,
            language=language,
            font_size=font_size,
            font_family=font_family_name,
        )


# ---------- Routes ----------

@app.get("/", response_class=HTMLResponse)
def root(request: Request) -> Response:
    return RedirectResponse(url="/dashboard", status_code=307)


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request) -> HTMLResponse:
    return _render(request, "dashboard.html", page_key="dashboard")


@app.get("/source", response_class=HTMLResponse)
def source(request: Request) -> HTMLResponse:
    return _render(request, "source.html", page_key="source")


@app.get("/setting", response_class=HTMLResponse)
def setting(request: Request) -> HTMLResponse:
    return _render(request, "setting.html", page_key="setting")


@app.post("/preferences")
def update_preferences(
    request: Request,
    language: str = Form(None),
    font_size: int = Form(None),
    font_family: str = Form(None),
) -> Response:
    # Each dropdown uses auto-submit on change, so the form may arrive with
    # only one field set. Read the others from existing cookies and only
    # overwrite what was actually submitted.
    current_lang = request.cookies.get("roboarm_lang", DEFAULT_LANGUAGE)
    current_size = int(_decode_cookie(request.cookies.get("roboarm_font_size", str(DEFAULT_FONT_SIZE))))
    current_family = _decode_cookie(request.cookies.get("roboarm_font_family", DEFAULT_FONT_FAMILY))

    if language is None:
        language = current_lang
    if font_size is None:
        font_size = current_size
    if font_family is None:
        font_family = current_family

    # Validate
    if language not in SUPPORTED_LANGUAGES:
        language = DEFAULT_LANGUAGE
    font_size = max(10, min(28, int(font_size)))
    valid_names = {opt["name"] for opt in FONT_OPTIONS}
    if font_family not in valid_names:
        font_family = DEFAULT_FONT_FAMILY

    # Re-render the same page the user was on, after saving prefs.
    referer = request.headers.get("referer", "")
    target = "/dashboard"
    for item in MENU:
        if item["url"] in referer:
            target = item["url"]
            break

    response = RedirectResponse(url=target, status_code=303)
    _set_prefs_response(
        response=response,
        language=language,
        font_size=font_size,
        font_family_name=font_family,
    )
    return response


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=False)
