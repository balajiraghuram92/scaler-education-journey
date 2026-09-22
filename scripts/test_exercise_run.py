import os
import sys
import json
import urllib.request
import urllib.error

# Determine root dir dynamically
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(script_dir, ".."))
base_dir = os.path.join(root_dir, "exercises", "java", "java-lld", "applied-machine-coding", "hotel-add-rooms")

def load_files(variant="solution"):
    paths = [
        "src/main/java/com/example/addroomshotelmanagement/repositories/InMemoryRoomRepository.java",
        "src/main/java/com/example/addroomshotelmanagement/repositories/InMemoryUserRepository.java",
        "src/main/java/com/example/addroomshotelmanagement/services/RoomServiceImpl.java"
    ]
    files = []
    for p in paths:
        full_p = os.path.join(base_dir, variant, *p.split("/"))
        with open(full_p, "r", encoding="utf-8") as f:
            files.append({
                "path": p,
                "content": f.read()
            })
    return files

def run_exercise(variant="solution", host="127.0.0.1:5000", api_key="your_api_key_here"):
    url = f"http://{host}/api/exercises/java-lld-hotel-add-rooms/run"
    payload = json.dumps({"files": load_files(variant)}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            body = resp.read().decode("utf-8")
            print(f"[{variant.upper()}] HTTP {status}:")
            print(body)
            return status, body
    except urllib.error.HTTPError as e:
        status = e.code
        body = e.read().decode("utf-8")
        print(f"[{variant.upper()}] HTTP {status} (HTTPError):")
        print(body)
        return status, body
    except Exception as e:
        print(f"[{variant.upper()}] Connection failed: {e}")
        return None, str(e)

if __name__ == "__main__":
    variant = sys.argv[1] if len(sys.argv) > 1 else "solution"
    print(f"Submitting {variant} files to exercise runner...")
    run_exercise(variant)
