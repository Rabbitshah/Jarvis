"""FastAPI server. Streams the same agent events as the CLI (server-sent events)."""
from __future__ import annotations

import json
from collections import OrderedDict
from typing import Iterator

import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from .agent import Agent, ChatClient
from .config import Config, load_config
from .llm import OllamaClient
from .tools.builtin import build_registry

MAX_SESSIONS = 20


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    session_id: str = Field(default="default", max_length=64)


def create_app(cfg: Config | None = None, llm: ChatClient | None = None) -> FastAPI:
    cfg = cfg or load_config()
    client = llm or OllamaClient(cfg.ollama_url, cfg.model, cfg.timeout_seconds)
    registry = build_registry(cfg)
    sessions: "OrderedDict[str, Agent]" = OrderedDict()
    app = FastAPI(title="Jarvis", version="0.1.0")

    def get_agent(session_id: str) -> Agent:
        if session_id in sessions:
            sessions.move_to_end(session_id)
        else:
            sessions[session_id] = Agent(client, registry, cfg.system_prompt,
                                         cfg.max_tool_rounds, cfg.max_history)
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

    return app


def main() -> None:
    cfg = load_config()
    uvicorn.run(create_app(cfg), host=cfg.api_host, port=cfg.api_port)


if __name__ == "__main__":
    main()
