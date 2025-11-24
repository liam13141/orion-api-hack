from fastapi import FastAPI, HTTPException
from api.PyrionDrift import OrionDriftAPI
import os
from fastapi.responses import HTMLResponse

app = FastAPI(
    title="PyrionDrift API Server",
    description="Full FastAPI server exposing all Orion Drift endpoints",
    version="1.0.0"
)

# Load API key from environment variable (Render dashboard)
API_KEY = os.getenv("ORION_API_KEY")
if not API_KEY:
    raise Exception("ORION_API_KEY environment variable is missing!")

api = OrionDriftAPI(API_KEY)


# ==============================
# USER ENDPOINTS
# ==============================

@app.get("/users")
def get_users(include_roles: bool = False, include_permissions: bool = False, page_size: int = 100, page: int = 1):
    return api.get_users(include_roles, include_permissions, page_size, page)

@app.get("/users/{user_id}")
def get_user(user_id: str, include_roles: bool = False, include_permissions: bool = False, include_bans: bool = False):
    return api.get_user(user_id, include_roles, include_permissions, include_bans)

@app.post("/users")
def create_user(data: dict):
    return api.create_or_update_user(data)

@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    return api.delete_user(user_id)

@app.post("/users/login")
def login(data: dict):
    return api.log_in(data)

@app.post("/users/login-server")
def login_server(data: dict):
    return api.log_in_server(data)

@app.post("/users/{user_id}/api-key")
def create_api_key(user_id: str):
    return api.create_user_api_key(user_id)


# ==============================
# STATION ENDPOINTS
# ==============================

@app.get("/dev", response_class=HTMLResponse)
def dev_page():
    return """
    <html>
    <head>
        <title>PyrionDrift Dev Panel</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #111;
                color: #fff;
                padding: 20px;
            }
            h1 {
                color: #4ec9b0;
            }
            .section {
                background: #1a1a1a;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }
            input, textarea {
                width: 100%;
                padding: 10px;
                margin: 5px 0;
                background: #222;
                color: white;
                border: 1px solid #333;
                border-radius: 6px;
            }
            button {
                background: #4ec9b0;
                color: #111;
                padding: 10px 15px;
                border: none;
                font-size: 15px;
                border-radius: 6px;
                cursor: pointer;
                margin-top: 10px;
            }
            button:hover {
                background: #3ba18b;
            }
            pre {
                background: #000;
                padding: 15px;
                border-radius: 6px;
                overflow-x: auto;
                max-height: 400px;
            }
        </style>

        <script>
            async function callEndpoint(method, url, body=null) {
                let options = { method: method };
                
                if (body) {
                    options.headers = {"Content-Type": "application/json"};
                    options.body = JSON.stringify(JSON.parse(body));
                }

                const res = await fetch(url, options);
                const text = await res.text();

                document.getElementById("output").innerText = text;
            }
        </script>
    </head>

    <body>
        <h1>PyrionDrift DEV PANEL</h1>

        <div class="section">
            <h2>Get User</h2>
            User ID:
            <input id="user_id" placeholder="Example: 123456789">
            <button onclick="callEndpoint('GET', '/users/' + document.getElementById('user_id').value)">Fetch</button>
        </div>

        <div class="section">
            <h2>Create Station</h2>
            JSON Body:
            <textarea id="station_body" rows="5">{ "name": "Test Station", "longitude": -73.9, "latitude": 40.7 }</textarea>
            <button onclick="callEndpoint('POST', '/stations', document.getElementById('station_body').value)">Create</button>
        </div>

        <div class="section">
            <h2>Ban User</h2>
            Station ID:
            <input id="ban_station" placeholder="Station ID">
            User ID:
            <input id="ban_user" placeholder="User ID">
            Duration:
            <input id="ban_duration" placeholder="Example: 1d">
            Reason:
            <input id="ban_reason" placeholder="Example: breaking rules">
            <button onclick="
                callEndpoint(
                    'POST',
                    '/stations/' + document.getElementById('ban_station').value +
                    '/ban/' + document.getElementById('ban_user').value +
                    '?duration=' + document.getElementById('ban_duration').value +
                    '&reason=' + document.getElementById('ban_reason').value
                )
            ">Ban User</button>
        </div>

        <h2>Output</h2>
        <pre id="output">Output will appear here…</pre>

    </body>
    </html>
    """

@app.get("/stations")
def list_stations(include_config: bool = False, include_deployments: bool = False,
                   include_offline_stations: bool = True, page_size: int = 100, page: int = 1):
    return api.get_stations(include_config, include_deployments, include_offline_stations, page_size, page)

@app.get("/stations/{station_id}")
def get_station(station_id: str, include_config: bool = True, include_deployments: bool = True):
    return api.get_station(station_id, include_config, include_deployments)

@app.post("/stations")
def create_station(data: dict):
    return api.create_station(data)

@app.patch("/stations/{station_id}")
def update_station(station_id: str, data: dict):
    return api.update_station(station_id, data)

@app.delete("/stations/{station_id}")
def delete_station(station_id: str):
    return api.delete_station(station_id)


# ==============================
# CONFIG ENDPOINTS
# ==============================

@app.get("/stations/{station_id}/config")
def get_station_config(station_id: str):
    return api.get_station_config(station_id)

@app.post("/stations/{station_id}/config")
def set_config(station_id: str, data: dict):
    return api.set_station_config(station_id, data)

@app.delete("/stations/{station_id}/config")
def delete_config(station_id: str, data: dict):
    return api.delete_station_config(station_id, data)


# ==============================
# EVENT ENDPOINTS
# ==============================

@app.get("/stations/{station_id}/events")
def station_events(station_id: str, get_past_events: bool = False):
    return api.get_station_events(station_id, get_past_events)

@app.post("/stations/{station_id}/events")
def create_event(station_id: str, data: dict):
    return api.create_station_event(station_id, data)

@app.get("/events/{event_id}")
def get_event(event_id: str):
    return api.get_event(event_id)

@app.patch("/stations/{station_id}/events/{event_id}")
def update_event(station_id: str, event_id: str, data: dict):
    return api.update_station_event(station_id, event_id, data)

@app.delete("/stations/{station_id}/events/{event_id}")
def delete_event(station_id: str, event_id: str):
    return api.delete_station_event(station_id, event_id)


# ==============================
# ROLE ENDPOINTS
# ==============================

@app.post("/stations/{station_id}/roles/{role_id}/assign/{user_id}")
def add_role(station_id: str, user_id: str, role_id: str):
    return api.add_role_to_user(station_id, user_id, role_id)

@app.delete("/stations/{station_id}/roles/{role_id}/remove/{user_id}")
def remove_role(station_id: str, user_id: str, role_id: str):
    return api.remove_role_from_user(station_id, user_id, role_id)

@app.post("/stations/{station_id}/roles")
def create_role(station_id: str, data: dict):
    return api.create_role(station_id, data)

@app.delete("/stations/{station_id}/roles/{role_id}")
def delete_role(station_id: str, role_id: str):
    return api.delete_role(station_id, role_id)


# ==============================
# BAN ENDPOINTS
# ==============================

@app.post("/stations/{station_id}/ban/{user_id}")
def ban_user(station_id: str, user_id: str, duration: str, reason: str):
    return api.ban_user(station_id, user_id, duration, reason)

@app.patch("/stations/{station_id}/ban/{user_id}")
def unban_user(station_id: str, user_id: str):
    return api.unban_user(station_id, user_id)

@app.get("/stations/{station_id}/bans")
def list_bans(station_id: str, include_revoked: bool = False, include_expired: bool = False):
    return api.get_station_bans(station_id, include_revoked, include_expired)

