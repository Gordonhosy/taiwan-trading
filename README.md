# analytics-platform

## Current Project State (as of last session)

This project exposes two local services through **one public URL**:

- **FastAPI Showcase** (`web/main.py` + `web/templates/index.html`) — runs on port 8001
- **Streamlit Dashboard** (`dashboards/app.py`) — runs on port 8501 with base path `/dashboard`

**Architecture for public access:**
- Caddy (reverse proxy on port 8080) routes:
  - `/` → FastAPI showcase
  - `/dashboard` → Streamlit
- ngrok tunnels only port 8080 → single public `https://*.ngrok.io` link
- The "View Interactive Dashboard" button in the showcase uses a relative `/dashboard` link so it works on the public URL.

Files to look at:
- `Caddyfile` — reverse proxy rules
- `web/main.py` — sets the dashboard link to `/dashboard`
- `README.md` (this file) — full run instructions
- `ngrok.yml` — kept for reference (currently not used in the single-link flow)

---

## TAIFEX Institutional Traders (Futures)

See `PROGRESS.md` for the latest data coverage, dashboard status, and how to resume work.

Latest snapshot:
```
python scripts/download_taifex.py
```

Historical (GET on Chinese query page):
```
python scripts/download_historical_institutional.py --start 2026-01-01 --end 2026-11-10
```
Uses https://www.taifex.com.tw/cht/3/futContractsDate?queryDate=YYYY/MM/DD
Saves raw HTML to data/raw/, appends deduped rows to data/taifex.db table institutional_futures.
Current coverage (as of Nov 2026): 224 trading days from 2026-01-01 to 2026-11-10, ~16k rows, 25 contracts.
Requires: pandas, requests, lxml (usually in env).

Launch dashboard:
```
streamlit run dashboards/app.py
```
(Requires streamlit + plotly; uses sidebar filters, net position charts, and filtered table.)

## Public Showcase Page (FastAPI)

Simple homepage introducing the analytics and linking to the live dashboard.

**Current recommended local run (for single public URL setup):**

Use these in separate terminals:

```powershell
cd C:\Users\User\analytics-platform
.\.venv\Scripts\Activate.ps1
# 1. Streamlit with sub-path
streamlit run dashboards/app.py --server.baseUrlPath=/dashboard --server.address 0.0.0.0

# 2. FastAPI
.\.venv\Scripts\python -m uvicorn web.main:app --host 0.0.0.0 --port 8001

# 3. Caddy reverse proxy (reads Caddyfile)
caddy run
```

**Local access (with Caddy running):**
- Showcase + Dashboard: http://localhost:8080
- Direct (if skipping Caddy): http://localhost:8001 and http://localhost:8501

**Access from another device on the same network:**
1. Find your PC's IP:
   ```powershell
   ipconfig | findstr "IPv4 Address"
   ```
2. On another device use:
   - `http://YOUR-IP:8080`   ← Main entry (showcase + dashboard button)
   - `http://YOUR-IP:8080/dashboard` ← Direct to dashboard

Make sure Windows Firewall allows port 8080 (and 8001/8501 if accessing directly).

## Exposing to the Internet (Public Access via Tunnel)

To make both the FastAPI showcase and Streamlit dashboard accessible from the internet using **a single public link**, we use a reverse proxy (Caddy) + one ngrok tunnel.

This way you only need one public URL (e.g. `https://abc123.ngrok.io`), and the "View Dashboard" button will work correctly.

### New Recommended Setup (Single Public Link)

**1. Download Caddy** (one-time)

Download the Windows version from https://caddyserver.com/download (or use winget if available).

Place `caddy.exe` in your project folder or in PATH.

**2. Start order** (use 4 terminals):

Terminal 1 – Streamlit (with subpath):
```powershell
cd C:\Users\User\analytics-platform
.\.venv\Scripts\Activate.ps1
streamlit run dashboards/app.py --server.baseUrlPath=/dashboard --server.address 0.0.0.0
```

Terminal 2 – FastAPI showcase:
```powershell
cd C:\Users\User\analytics-platform
.\.venv\Scripts\python -m uvicorn web.main:app --host 0.0.0.0 --port 8001
```

Terminal 3 – Caddy reverse proxy:
```powershell
cd C:\Users\User\analytics-platform
caddy run
```
(Caddy will read the `Caddyfile` in this folder and run on port 8080)

Terminal 4 – ngrok (single tunnel):
```powershell
cd C:\Users\User\analytics-platform
& "C:\Users\User\ngrok.exe" http 8080
```

**Public link:**

Use the `https://...ngrok.io` URL that ngrok prints.

- `https://your-url.ngrok.io` → Showcase page
- `https://your-url.ngrok.io/dashboard` → Streamlit dashboard

The button on the showcase page will now correctly open the dashboard on the same public URL.

### Alternative without Caddy (two separate links)

See the old multi-tunnel instructions in previous versions of this README if you prefer two separate public URLs.

### Free Tier Limitations

- **ngrok free**:
  - Public URLs change every time you restart the tunnel (unless you upgrade for reserved domains).
  - Limited concurrent connections and sessions.
  - Suitable for demos and occasional sharing.

- **Cloudflare quick tunnels**:
  - Random URL each run.
  - No persistent named subdomains without a Cloudflare account + tunnel setup.
  - Good performance, but sessions may have timeouts.

### Security Considerations

- Anyone who has the public URL can access your local servers and data.
- The data here is public TAIFEX market data (low sensitivity), but treat the URLs as public.
- **Do not** leave tunnels running unattended for long periods.
- Add protection if sharing widely:
  - Streamlit: Add `--server.enableCORS=false` and consider basic auth via config or proxy.
  - FastAPI: Implement simple token auth or use Cloudflare Access (free tier limited).
- Keep your local apps updated.
- ngrok/Cloudflare add TLS, but the connection to your machine is from their edge.

Restart tunnels as needed using the commands above.

Note: The old multi-tunnel `ngrok.yml` is kept for reference but is not used in the current single-link (Caddy) setup.

## Permanent Deployment (Streamlit Community Cloud)

For a stable public URL without running anything locally:

1. Push this repo to GitHub (include `data/taifex.db`).
2. Go to https://share.streamlit.io
3. Deploy from `dashboards/app.py`
4. The dashboard will be available at a permanent `https://...streamlit.app` address.

See `DEPLOY.md` for full details and other options.

The app now includes a "🔄 Check for newer data" button in the sidebar (fetches recent days into the current session).
