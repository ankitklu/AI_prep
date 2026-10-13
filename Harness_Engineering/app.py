import json
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from graph import SupportState, run_support_system, support_graph

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Harness Engineering - Support Agent",
    description="Multi-agent customer support pipeline built with LangGraph.",
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


class AskResponse(BaseModel):
    route: str
    answer: str
    trace: list[str]


def initial_state(question: str) -> SupportState:
    return {
        "question": question,
        "route": "",
        "draft": "",
        "final_answer": "",
        "blocked": False,
        "trace": [],
    }


def sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/ask", response_model=AskResponse)
def ask(payload: AskRequest):
    """Run the whole graph and return the final result in one response."""
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    try:
        return run_support_system(question)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/ask/stream")
def ask_stream(question: str):
    """
    Stream the graph execution node by node using Server-Sent Events.
    Each LangGraph node emits a `step` event as soon as it finishes,
    so the UI can show the pipeline progressing in real time.
    """
    question = question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    def event_generator():
        state = dict(initial_state(question))
        started = time.perf_counter()
        last = started

        yield sse("start", {"question": question})

        try:
            for chunk in support_graph.stream(initial_state(question), stream_mode="updates"):
                for node, update in chunk.items():
                    now = time.perf_counter()
                    update = update or {}
                    state.update(update)
                    yield sse("step", {
                        "node": node,
                        "update": {k: v for k, v in update.items() if k != "trace"},
                        "trace": state.get("trace", []),
                        "duration_ms": round((now - last) * 1000),
                    })
                    last = now

            yield sse("done", {
                "route": state.get("route") or "blocked",
                "blocked": state.get("blocked", False),
                "draft": state.get("draft", ""),
                "answer": state.get("final_answer", ""),
                "trace": state.get("trace", []),
                "total_ms": round((time.perf_counter() - started) * 1000),
            })
        except Exception as exc:
            yield sse("failure", {"message": str(exc)})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
