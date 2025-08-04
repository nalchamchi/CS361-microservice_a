# Property Validation Microservice

This microservice validates U.S. addresses and returns a standardized version of the address in JSON format.  
It supports two modes:
- **Mock Mode**: Simple keyword check for "Corvallis" (for demo purposes)
- **USPS API Mode**: Real address validation using the USPS Address Validation API

---

## 1. Communication Contract

### Request Format (JSON)
```json
{
  "address": "123 SE Main St, Corvallis, OR 97333"
}
```

### Response Format (JSON)
```json
{
  "status": "valid",
  "corrected_address": "123 Se Main St, Corvallis, Or 97333"
}
```

**Fields**
- `status`: `"valid"` or `"invalid"`
- `corrected_address`: Standardized version of the address if valid, empty string if invalid

---

## 2. How to Request Data

### Example (Python)
```python
import zmq
import json

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

request_data = {"address": "123 SE Main St, Corvallis, OR 97333"}
socket.send_string(json.dumps(request_data))
response = json.loads(socket.recv_string())
print(response)
```

---

## 3. How to Receive Data

The microservice sends a JSON string response.  
Example:
```json
{"status": "valid", "corrected_address": "123 Se Main St, Corvallis, Or 97333"}
```

---

## 4. Running the Microservice

### Install dependencies
```bash
pip install zmq requests
```

### Run the server (Mock Mode)
```bash
python microservice_a.py
```

### Run the client
```bash
python test_client.py
```

---

## 5. Switching to USPS API Mode

1. Obtain USPS API key from [USPS Web Tools](https://www.usps.com/business/web-tools-apis/welcome.htm)
2. Create a `config.json` file:
```json
{
  "usps_api_key": "YOUR_USPS_API_KEY"
}
```
3. In `microservice_a.py`, change:
```python
MODE = "mock"
```
to:
```python
MODE = "usps"
```

---

## 6. Example Output (Mock Mode)
```
[Client] Sent address: 123 SE Main St, Corvallis, OR 97333
[Client] VALID - Standardized: 123 Se Main St, Corvallis, Or 97333

[Client] Sent address: 999 Fake Street, Sunderland, OR 97330
[Client] INVALID - Could not validate

[Client] Sent address: 450 SW 3rd St, Corvallis, OR 97333
[Client] VALID - Standardized: 450 Sw 3Rd St, Corvallis, Or 97333
```

---

## 7. Notes
- Current demo uses Mock Mode (keyword `"Corvallis"`) for address validation.
- USPS API Mode requires USPS API key approval.
