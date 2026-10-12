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
│   ├── main.py              # FastAPI app factory + startup
│   ├── config.py            # Paths, defaults
│   ├── db.py                # SQLite3 connection + schema bootstrap
│   ├── i18n.py              # Translation loader + helper
│   ├── routes/
│   │   ├── pages.py         # /, /source-table, /system-setting
│   │   ├── api_i18n.py      # /api/i18n/...
│   │   └── api_settings.py  # /api/settings/...
│   ├── templates/
│   │   ├── base.html        # Sidebar + topbar layout
│   │   ├── dashboard.html
│   │   ├── source_table.html
│   │   └── system_setting.html
│   └── static/
│       ├── css/app.css
│       └── js/app.js
├── data/RoboArm.db          # created on first run
├── tests/
│   └── test_phase1.py
├── requirements.txt
└── .gitignore
```

## Run

```bash
pip install -r requirements.txt
python -m app.main
# open http://localhost:8000
```

## Phase I scope (this commit)

1. Sidebar layout with three menu items:
   - **主頁 / DashBoard**
   - **來源資料表 / Source Table**
   - **系統設定 / System Setting**
2. i18n: all UI text served from a `translations` table (zh_tw / en / zh_cn), switchable via a top-bar dropdown.
3. UI settings: language, font size (default `14`), font family (default `DFKai-SB`).
4. Each page is a placeholder card with the text "此功能即將推出 / This feature is coming soon / 此功能即将推出".

## Phase I non-goals

- No git init / commit / push (per explicit instruction).
- No GitHub repository created.
- No Cloudflare tunnel or public exposure.
- No Flask.
- No charts, KPIs, robot status, alarms, real I/O, or vendor SDKs.
