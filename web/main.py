from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
import os

app = FastAPI(title="TAIFEX Institutional Analytics Showcase")

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = Environment(loader=FileSystemLoader(template_dir))
template = jinja_env.get_template("index.html")

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    # Relative path because we use a reverse proxy (Caddy) in front
    html = template.render(streamlit_url="/dashboard")
    return HTMLResponse(content=html)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
