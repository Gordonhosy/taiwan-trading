# Deployment Guide

## Current Status
The dashboard is working via local Caddy + ngrok.

For a **permanent** public version (stable URL, no need to keep your computer on), here are the best options.

---

## Option 1: Streamlit Community Cloud (Recommended - Easiest)

We've prepared the project specifically for this.

**Steps:**

1. **Push to GitHub**
   - Create (or use) a GitHub repo for this project.
   - Make sure `data/taifex.db` is committed (it's only ~1 MB).
   - `git push`

2. **Deploy**
   - Go to https://share.streamlit.io
   - Sign in with your GitHub account
   - **New app** → select your repository
   - Branch: `main`
   - **Main file path**: `dashboards/app.py`
   - Deploy

3. **Result**
   - Permanent URL like `https://your-username-taifex-institutional.streamlit.app`
   - Dashboard runs at the root (no need for `/dashboard`)

**New in this version:**
- Sidebar has a **"🔄 Check for newer data"** button. It attempts to fetch the latest trading days directly from TAIFEX into your current browser session.
- Shows the latest data date at the top.

**Updating data long-term:**
- Best way: Run the download scripts locally, commit the updated `data/taifex.db`, push → redeploy.
- The in-app refresh is great for quick checks without redeploying.

**Notes:**
- Free tier sleeps after ~15-30 min of inactivity (wakes up in a few seconds when someone visits).
- No Caddy / ngrok / FastAPI needed for the cloud version.

---

## Other Options (if you change your mind later)

- Full Docker on Render/Railway/Fly.io (we have Dockerfile + start.sh ready)
- Cloudflare Tunnel (stable URL while still running locally)

See the full file for details.

---

## Option 3: Cloudflare Tunnel (Keep running locally or on VPS)

If you want to keep running on your own machine/VPS but with a stable nice URL:

1. Install cloudflared
2. `cloudflared tunnel login`
3. Create a tunnel and point it to your local Caddy (port 8080)
4. Get a permanent `*.yourname.com` or free `*.trycloudflare.com` (more stable than ngrok)

This avoids ngrok limits and changing URLs.

---

## Next Steps

Tell me which direction you want:

- **A)** Go with Streamlit Cloud (fastest permanent dashboard)
- **B)** Use Docker + Render/Railway (preserves more of the current architecture)
- **C)** Cloudflare Tunnel setup
- **D)** Add auto data refresh + GitHub Actions first

We can also improve the dashboard (add a refresh button, last-updated info, etc.) as part of the deployment.
