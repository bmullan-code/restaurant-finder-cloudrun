#%%
import sys
import os
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# 1. Configure PYTHONPATH relative to this file's location
project_root = Path(__file__).resolve().parent
sdk_paths = [
    project_root / "sdk" / "a2ui_agent" / "src",
    project_root / "sdk" / "a2ui_core" / "src",
]
for path in sdk_paths:
    if path.exists():
        sys.path.insert(0, str(path))

# 2. Load .env file for Vertex AI/Gemini API credentials
load_dotenv(dotenv_path=project_root / ".env", override=True)

try:
    from google.adk.agents.llm_agent import LlmAgent
    from google.adk.models import Gemini
    from google.adk.runners import Runner
    from google.adk.artifacts import InMemoryArtifactService
    from google.adk.sessions import InMemorySessionService
    from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
    from google.genai import types
    from a2ui.schema.manager import A2uiSchemaManager
    from a2ui.basic_catalog.provider import BasicCatalog
    from a2ui.parser.parser import parse_response
    from a2ui.schema.constants import VERSION_0_9
except ImportError as e:
    print(f"Error: Could not import required libraries.")
    print(f"Details: {e}")
    sys.exit(1)

# Ensure GEMINI_API_KEY or suitable credentials exist
if not os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    print("⚠️ WARNING: Neither GEMINI_API_KEY nor GOOGLE_APPLICATION_CREDENTIALS was detected in your .env.")
    print("Please make sure you have loaded the proper API keys to connect to Google Gemini.")

async def run_gemini_a2ui_learning_flow():
    print("==================================================")
    print("🤖 Learning A2UI + Google Gemini Flow")
    print("==================================================\n")

    # 1. Initialize the A2UI Schema Manager (using v0.9 specification)
    version = VERSION_0_9
    schema_manager = A2uiSchemaManager(
        version=version,
        catalogs=[
            BasicCatalog.get_config(
                version=version,
                examples_path=f"agent/examples/{version}", # points to agent examples folder
            )
        ]
    )
    selected_catalog = schema_manager.get_selected_catalog()

    # 2. Build the system prompt dynamically
    # This automatically injects the structural schema rules and design components!
    print("📝 Step 1: Generating System Prompt dynamically...")
    system_instruction = schema_manager.generate_system_prompt(
        role_description="You are a premium restaurant finder agent. You MUST answer using the booking-surface UI component.",
        ui_description="Use the booking-surface component to help users book a table.",
        include_schema=True,
        include_examples=True,
        validate_examples=True
    )
    print("✅ System prompt successfully generated and validated!")
    print(f"       (Prompt size: {len(system_instruction)} characters of rich design instruction)\n")

    # 3. Create the Google ADK LLM Agent powered by Gemini
    # We will use gemini-2.5-flash as the standard, premium, reliable model for agent testing
    print("🧠 Step 2: Instantiating Gemini agent with ADK...")
    agent = LlmAgent(
        model=Gemini(model="gemini-2.5-flash"),
        name="restaurant_finder_learning_agent",
        description="A lightweight learning agent.",
        instruction=system_instruction,
    )
    
    # In ADK, agents are run inside a Runner which manages sessions and memory
    runner = Runner(
        app_name="learn_a2ui_app",
        agent=agent,
        artifact_service=InMemoryArtifactService(),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
    )
    print("✅ Agent and Runner created successfully!\n")

    # 4. Define the query
    sample_query = "USER_WANTS_TO_BOOK: I want to book a table for 4 people at Chez Panisse tonight at 8 PM."
    print(f"💬 Step 3: Sending user prompt to Gemini:")
    print(f"       User Query: \"{sample_query}\"")
    print("       (Please wait while Gemini generates the A2UI layout...)\n")

    try:
        # Create a session to run our conversation
        session_id = "demo_session_123"
        await runner.session_service.create_session(
            app_name="learn_a2ui_app",
            user_id="demo_user",
            session_id=session_id,
            state={"expression": "{expression}"}
        )

        user_message = types.Content(
            role="user",
            parts=[types.Part.from_text(text=sample_query)]
        )

        # Iterate over the async generator returned by runner.run_async()
        raw_text_parts = []
        async for event in runner.run_async(
            user_id="demo_user",
            session_id=session_id,
            new_message=user_message,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        raw_text_parts.append(part.text)
                        # Stream raw tokens live in the panel
                        print(part.text, end="", flush=True)
        
        print("\n")
        raw_text = "".join(raw_text_parts)
        
        print("📥 Step 4: Full response compiled from stream:")
        print("-" * 50)
        print(raw_text)
        print("-" * 50 + "\n")

        # 5. Extract and Validate the A2UI blocks from the text
        print("🔍 Step 5: Parsing and Validating A2UI Payload...")
        parsed_parts = parse_response(raw_text)
        
        a2ui_blocks = [part.a2ui_json for part in parsed_parts if part.a2ui_json]

        if not a2ui_blocks:
            print("❌ No A2UI block found in Gemini's response.")
        else:
            for idx, block in enumerate(a2ui_blocks):
                print(f"\n--- Checking A2UI Block {idx + 1} ---")
                try:
                    # Validate against schema rules
                    selected_catalog.validator.validate(block)
                    print("✅ VALIDATION SUCCESS: The generated card complies with A2UI rules!")
                    print("\n🎁 Renderable JSON Schema Structure:")
                    print(json.dumps(block, indent=2))
                except Exception as val_error:
                    print("❌ Validation failed on the generated payload:")
                    print(f"   Details: {val_error}")

    except Exception as e:
        print(f"❌ Execution failed: {e}")

    print("\n==================================================")
    print("🎓 End of A2UI + Gemini Integration Demo")
    print("==================================================")

# ----------------------------------------------------
# 🚀 Jupyter / Interactive Cell Run Support
# ----------------------------------------------------
#%%
# In VS Code Interactive Window, we can run the coroutine on the active loop without top-level await syntax
if "ipykernel" in sys.modules:
    asyncio.ensure_future(run_gemini_a2ui_learning_flow())

# Fallback for running as a standard script in terminal
if __name__ == "__main__" and "ipykernel" not in sys.modules:
    try:
        asyncio.run(run_gemini_a2ui_learning_flow())
    except RuntimeError:
        # Fallback if there is a running loop in another host IDE setup
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_gemini_a2ui_learning_flow())
