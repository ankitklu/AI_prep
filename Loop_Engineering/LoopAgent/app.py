from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from starlette.requests import Request
import uvicorn

from Loop_Engineering.LoopAgent.backend import run_workflow

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title = "Self-correcting Multi Agent Demo")

app.mount("/static", StaticFiles(directory= BASE_DIR/"static"), name = "static")
templates = Jinja2Templates(directory = BASE_DIR/"templates")


class RunRequest(BaseModel):
    """Payload sent by the UI."""
    topic: str = Field(..., min_length=1, max_length=300, description="Topic to explain")


@app.get("/")
def index(request: Request):
    """Serve the UI."""
    return templates.TemplateResponse(request, "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


# Plain `def` (not async): run_workflow is blocking, so FastAPI runs it in a threadpool.
@app.post("/api/run")
def run(req: RunRequest):
    """Run the writer -> reviewer -> reviser loop and return every step."""
    topic = req.topic.strip()
    if not topic:
        raise HTTPException(status_code=422, detail="Topic cannot be empty.")

    try:
        return run_workflow(topic)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow failed: {e}")


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
