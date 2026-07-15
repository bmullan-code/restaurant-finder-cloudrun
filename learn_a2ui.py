import sys
import os
import json
from pathlib import Path

# 1. Dynamically configure PYTHONPATH relative to this file's location in the project root
project_root = Path(__file__).resolve().parent
sdk_paths = [
    project_root / "sdk" / "a2ui_agent" / "src",
    project_root / "sdk" / "a2ui_core" / "src",
]
for path in sdk_paths:
    if path.exists():
        sys.path.insert(0, str(path))

# 2. Import A2UI SDK modules
try:
    from a2ui.parser.parser import parse_response
    from a2ui.schema.manager import A2uiSchemaManager
    from a2ui.basic_catalog.provider import BasicCatalog
except ImportError as e:
    print(f"Error: Could not import a2ui libraries. Checked paths: {[str(p) for p in sdk_paths]}")
    print(f"Details: {e}")
    sys.exit(1)

def run_learning_demo():
    print("==================================================")
    print("🏫 Learning A2UI Programmatically (Without Browser)")
    print("==================================================\n")

    # 3. Simulate raw LLM responses.
    # Payload A contains schema/syntax errors.
    payload_with_errors = """
Here is a booking card with typical LLM syntax typos:

<a2ui-json>
[
  {
    "version": "0.9",
    "createSurface": {
      "surfaceId": "booking-surface",
      "catalogId": "https://a2ui.org/specification/v0_9/catalogs/basic/catalog.json"
    }
  }
]
</a2ui-json>
"""

    # Payload B is corrected and uses precise A2UI syntax.
    payload_correct = """
Here is the fully corrected, valid card payload:

<a2ui-json>
[
  {
    "version": "v0.9",
    "createSurface": {
      "surfaceId": "booking-surface",
      "catalogId": "https://a2ui.org/specification/v0_9/catalogs/basic/catalog.json",
      "theme": {
        "primaryColor": "#D32F2F"
      }
    }
  },
  {
    "version": "v0.9",
    "updateComponents": {
      "surfaceId": "booking-surface",
      "components": [
        {
          "id": "root",
          "component": "Column",
          "children": ["title-text"]
        },
        {
          "id": "title-text",
          "component": "Text",
          "variant": "h2",
          "text": "Reservation Confirmed!"
        }
      ]
    }
  }
]
</a2ui-json>
"""

    # Initialize the validator manager for 0.9 specification
    schema_manager = A2uiSchemaManager(
        version="0.9",
        catalogs=[BasicCatalog.get_config(version="0.9")]
    )
    selected_catalog = schema_manager.get_selected_catalog()

    # ----------------------------------------------------
    print("--- SCENARIO 1: Validating Payload with Typos ---")
    parts_err = parse_response(payload_with_errors)
    a2ui_err = [p.a2ui_json for p in parts_err if p.a2ui_json][0]
    
    try:
        selected_catalog.validator.validate(a2ui_err)
        print("✅ Success!")
    except Exception as err:
        print("❌ VALIDATION FAILED AS EXPECTED!")
        print("Errors caught by backend validator:")
        print(f"  {err}")
    print("\n" + "="*50 + "\n")

    # ----------------------------------------------------
    print("--- SCENARIO 2: Validating Corrected Payload ---")
    parts_ok = parse_response(payload_correct)
    a2ui_ok = [p.a2ui_json for p in parts_ok if p.a2ui_json][0]

    try:
        selected_catalog.validator.validate(a2ui_ok)
        print("✅ SUCCESS: The payload is 100% valid against the A2UI Schema!")
        print("\nExtracted JSON structure:")
        print(json.dumps(a2ui_ok, indent=2))
    except Exception as err:
        print(f"❌ Unexpected Error: {err}")

    print("\n==================================================")
    print("🎓 End of A2UI Code-Only Learning Demo")
    print("==================================================")

if __name__ == "__main__":
    run_learning_demo()
