import json
import time
from pathlib import Path

APPROVALS_DIR = Path(__file__).parent / "approvals"
APPROVALS_DIR.mkdir(exist_ok=True)

print("watching for approval requests... (Ctrl+C to stop)")

seen = set()
while True:
    for request_path in APPROVALS_DIR.glob("*.request.json"):
        if request_path in seen:
            continue
        seen.add(request_path)

        data = json.loads(request_path.read_text())
        print("\n--- APPROVAL NEEDED ---")
        print("tool:", data["tool"])
        print("arguments:", data["arguments"])
        answer = input("approve? (y/n): ").strip().lower()

        request_id = request_path.stem.split(".")[0]
        response_path = APPROVALS_DIR / f"{request_id}.response.json"
        response_path.write_text(json.dumps({"approved": answer == "y"}))

    time.sleep(1)