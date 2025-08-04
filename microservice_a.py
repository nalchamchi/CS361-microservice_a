import zmq
import json
import requests

CONFIG_FILE = "config.json"

# Toggle between 'mock' and 'usps'
MODE = "mock"  # Change to "usps" when USPS API access is approved

def load_api_key():
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return config.get("usps_api_key", "").strip()
    except (FileNotFoundError, json.JSONDecodeError):
        return ""


# Mock validation function

def validate_address_mock(address):
    # Simple rule: if "Corvallis" is in address → valid
    if "Corvallis" in address:
        
        return True, address.title()  # Standardize case
    return False, ""


# USPS API validation function

def validate_address_usps(address, api_key):
    if not api_key:
        return None, "Missing USPS API key"

    url = "https://secure.shippingapis.com/ShippingAPI.dll"
    params = {
        "API": "Verify",
        "XML": f"""
        <AddressValidateRequest USERID="{api_key}">
            <Revision>1</Revision>
            <Address ID="0">
                <Address1></Address1>
                <Address2>{address}</Address2>
                <City></City>
                <State></State>
                <Zip5></Zip5>
                <Zip4></Zip4>
            </Address>
        </AddressValidateRequest>
        """
    }

    try:
        r = requests.get(url, params=params, timeout=5)
        if r.status_code != 200:
            return None, "API request failed"

        if "<Error>" in r.text:
            return None, "Invalid address"

        def extract_tag(tag):
            start = r.text.find(f"<{tag}>") + len(tag) + 2
            end = r.text.find(f"</{tag}>")
            return r.text[start:end].strip() if start > 0 and end > 0 else ""

        addr_line = extract_tag("Address2")
        city = extract_tag("City")
        state = extract_tag("State")
        zip5 = extract_tag("Zip5")

        standardized = f"{addr_line}, {city}, {state} {zip5}".strip()
        return standardized, None

    except requests.RequestException:
        return None, "API connection error"


# Server main loop

def run_server():
    api_key = load_api_key() if MODE == "usps" else None
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")

    print(f"Property Validation Microservice running in {MODE.upper()} mode...")

    while True:
        message = socket.recv_string()
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            socket.send_string(json.dumps({"error": "Invalid JSON"}))
            continue

        address = data.get("address", "").strip()
        if not address:
            socket.send_string(json.dumps({"error": "Missing 'address' field"}))
            continue

        if MODE == "mock":
            valid, standardized = validate_address_mock(address)
            if valid:
                response = {"status": "valid", "corrected_address": standardized}
            else:
                response = {"status": "invalid", "corrected_address": ""}
        else:  # USPS mode
            standardized, err = validate_address_usps(address, api_key)
            if err:
                response = {"status": "invalid", "corrected_address": ""}
            else:
                response = {"status": "valid", "corrected_address": standardized}

        socket.send_string(json.dumps(response))
        print(f"[Server] Sent: {response}")

if __name__ == "__main__":
    run_server()
