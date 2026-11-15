"""FastAPI server. Streams the same agent events as the CLI (server-sent events)."""
from __future__ import annotations

import json
from collections import OrderedDict
from typing import Iterator

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .agent import Agent, ChatClient
from .config import ROOT, Config, load_config
from .llm import OllamaClient
from .memory.context import make_context_fn
from .memory.remember import Proposals
from .security import LocalOnly
from .tools.builtin import build_registry

MAX_SESSIONS = 20


class ConfirmRequest(BaseModel):
    session_id: str = Field(default="default", pattern=r"^[A-Za-z0-9_-]{1,64}$")
    id: str = Field(min_length=1, max_length=32)
    approve: bool


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    session_id: str = Field(default="default", pattern=r"^[A-Za-z0-9_-]{1,64}$")


def create_app(cfg: Config | None = None, llm: ChatClient | None = None) -> FastAPI:
    cfg = cfg or load_config()
    client = llm or OllamaClient(cfg.ollama_url, cfg.model, cfg.timeout_seconds, cfg.embed_model)
    context_fn = make_context_fn(cfg, client.embed) if hasattr(client, "embed") else None
    registry = build_registry(cfg)
    sessions: "OrderedDict[str, Agent]" = OrderedDict()
    app = FastAPI(title="Jarvis", version="0.1.0")
    app.add_middleware(LocalOnly, port=cfg.api_port, extra_origins=cfg.api_allowed_origins)

    def get_agent(session_id: str) -> Agent:
        if session_id in sessions:
            sessions.move_to_end(session_id)
        else:
            proposals = Proposals(cfg, getattr(client, "embed", None))
            session_registry = build_registry(cfg, getattr(client, "embed", None), proposals)
            sessions[session_id] = Agent(client, session_registry, cfg.system_prompt,
                                         cfg.max_tool_rounds, cfg.max_history, context_fn, proposals)
            while len(sessions) > MAX_SESSIONS:
                sessions.popitem(last=False)
        return sessions[session_id]

    @app.get("/health")
    def health() -> dict:
        reachable = client.ping() if hasattr(client, "ping") else True
        return {"status": "ok", "ollama": reachable, "model": cfg.model, "tools": registry.names()}

    @app.post("/chat")
    def chat(req: ChatRequest) -> StreamingResponse:
        agent = get_agent(req.session_id)

        def events() -> Iterator[str]:
            for ev in agent.chat(req.message):
                yield f"data: {json.dumps(ev)}\n\n"

        return StreamingResponse(events(), media_type="text/event-stream")

    @app.post("/confirm")
    def confirm(req: ConfirmRequest) -> dict:
        agent = sessions.get(req.session_id)
        if agent is None or agent.proposals is None:
            raise HTTPException(status_code=404, detail="unknown session")
        msg = agent.proposals.approve(req.id) if req.approve else agent.proposals.reject(req.id)
        return {"message": msg}

    dist = ROOT / "web" / "dist"
    if dist.is_dir():  # mounted last so /health, /chat and /confirm win
        app.mount("/", StaticFiles(directory=dist, html=True), name="web")
    return app


def main() -> None:
    cfg = load_config()
    uvicorn.run(create_app(cfg), host=cfg.api_host, port=cfg.api_port)


if __name__ == "__main__":
    main()
