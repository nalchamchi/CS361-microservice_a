import zmq
import json

def run_client():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    # Test addresses
    test_addresses = [
        "123 SE Main St, Corvallis, OR 97333",
        "999 Fake Street, Sunderland, OR 97330",
        "450 SW 3rd St, Corvallis, OR 97333"
    ]

    for addr in test_addresses:
        # Send request to server
        request_data = {"address": addr}
        socket.send_string(json.dumps(request_data))
        print(f"\n[Client] Sent address: {addr}")

        # Receive response
        message = socket.recv_string()
        try:
            response_data = json.loads(message)
        except json.JSONDecodeError:
            print("[Client] Invalid JSON response")
            continue

        # Show validation result
        if response_data.get("status") == "valid":
            print(f"[Client] VALID - Standardized: {response_data.get('corrected_address')}")
        else:
            print(f"[Client] INVALID - Could not validate")

if __name__ == "__main__":
    run_client()
