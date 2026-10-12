# RoboArm

Robotic Arm Control System (機械臂控制系統 / 机械臂控制系统)

Version: **V1.0** · Phase I

## Stack

- Language: **Python 3.12**
- Web framework: **FastAPI** + **Uvicorn**
- Templating: **Jinja2**
- Frontend: **Vanilla JavaScript** (no build step)
- Database: **SQLite3** (default), `data/RoboArm.db` — with stubs for JSON / YAML / Supabase (Phase II+)
- i18n: backed by a `translations` SQLite table seeded with `zh_tw` / `en` / `zh_cn` on first boot

> Flask is intentionally **not** used.

## Project layout

```text
RoboArm/
├── app/
│   ├── main.py              # FastAPI app + all routes
│   ├── config.py            # Paths, defaults, language list
│   ├── db.py                # SQLite3 connection + schema bootstrap + seed
│   ├── i18n.py              # Translation loader + Jinja helper
│   ├── templates/
│   │   ├── base.html        # Sidebar + topbar + live font stage
│   │   ├── dashboard.html
│   │   ├── source.html
│   │   └── setting.html
│   └── static/
│       ├── css/app.css
│       └── js/app.js
├── data/
│   ├── .gitkeep
│   └── RoboArm.db           # created on first run (gitignored)
├── docs/                    # Phase I screenshots
├── requirements.txt
└── .gitignore
```

## Run

```bash
pip install -r requirements.txt
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
# open http://localhost:8000
```

The first start will create `data/RoboArm.db` and seed the `translations`
table with the three languages (zh_tw / en / zh_cn) and the
`user_preferences` table with one default row (id=1).

## Preferences

User prefs are stored in a single `user_preferences` row and mirrored to a
`roboarm_prefs` cookie so the page renders with the right language, font
size, and font family on every request.

- Language: `zh_tw` (default) / `en` / `zh_cn`
- Font size: integer px, default `14`, range 10–28
- Font family: any name from the `FONT_FAMILIES` list in `app/config.py`,
  default `DFKai-SB 標楷體`

The selected font is applied through a CSS custom property
(`--app-font-family`) so the change is visible across the entire page.

## Phase I scope (this commit)

1. Sidebar layout with three menu items:
   - **主頁 / DashBoard**
   - **來源資料表 / Source Table**
   - **系統設定 / System Setting**
2. i18n: all UI text served from a `translations` table (zh_tw / en / zh_cn), switchable via a top-bar dropdown.
3. UI settings: language, font size (default `14`), font family (default `DFKai-SB`).
4. Each page is a placeholder card with the text "此功能即將推出 / This feature is coming soon / 此功能即将推出".

## Deployment

The dev server runs behind a Cloudflare-style reverse proxy. The public URL
is **https://roboarm-hkben.zocomputer.io** (set in Phase I, see
`docs/01_dashboard_zh_tw.png` for proof). The repo is published at
<https://github.com/Ben-Yung/RoboArm>.

## Phase I non-goals

- No charts, KPIs, robot status, alarms, real I/O, or vendor SDKs.
- No Flask.
- No JSON / YAML / Supabase persistence (those are Phase II+).
