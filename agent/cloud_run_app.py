# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Serve the restaurant A2A agent and the built Lit client on one port."""

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env", override=True)

# Resolve and add local SDK source paths automatically relative to project root
project_root = Path(__file__).resolve().parent.parent
sdk_paths = [
    project_root / "sdk" / "a2ui_agent" / "src",
    project_root / "sdk" / "a2ui_core" / "src",
]
for path in sdk_paths:
    if path.exists():
        sys.path.insert(0, str(path))

# Fallback for manual PYTHONPATH overrides
if "PYTHONPATH" in os.environ:
    for path in os.environ["PYTHONPATH"].split(os.pathsep):
        if path and path not in sys.path:
            sys.path.insert(0, path)

import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from agent import RestaurantAgent
from agent_executor import RestaurantAgentExecutor
from starlette.staticfiles import StaticFiles


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    """Create the combined A2A and frontend ASGI application."""
    if os.getenv("GOOGLE_GENAI_USE_VERTEXAI") != "TRUE" and not os.getenv(
        "GEMINI_API_KEY"
    ):
        raise RuntimeError(
            "Set GEMINI_API_KEY or configure GOOGLE_GENAI_USE_VERTEXAI=TRUE."
        )

    agent_url = os.environ["AGENT_URL"].rstrip("/")
    agent = RestaurantAgent(base_url=agent_url)
    request_handler = DefaultRequestHandler(
        agent_executor=RestaurantAgentExecutor(agent),
        task_store=InMemoryTaskStore(),
    )
    app = A2AStarletteApplication(
        agent_card=agent.agent_card,
        http_handler=request_handler,
    ).build()

    app.mount("/static", StaticFiles(directory="images"), name="agent-static")

    # Mount this last so the A2A routes registered above retain precedence.
    default_frontend_path = project_root / "frontend"
    if not default_frontend_path.exists():
        default_frontend_path = Path("/app/frontend")
    frontend_dir = Path(os.getenv("FRONTEND_DIR", default_frontend_path))
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    logger.info("Starting combined A2UI demo on port %d", port)
    uvicorn.run(app, host="0.0.0.0", port=port)
