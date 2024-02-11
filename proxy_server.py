import logging
from pathlib import Path
from flask import Flask, request, Response, redirect
import requests
import json
import socketio
from urllib.parse import urljoin, urlparse


def get_proxy_config(p: Path):
    return json.loads(p.read_text())

def serve(proxy_config: dict[str, str], host: str, port: str):
    app = Flask(__name__)
    sio = socketio.Client()

    def log_request(path, destination=None):
        if destination:
            logging.info(f"Redirecting request for {path} to {destination}")
        else:
            logging.info(f"Received unmatched request for {path}")

    @app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
    def proxy(path):
        for prefix, base_url in proxy_config.items():
            if path.startswith(prefix):
                # Correctly route the request based on prefix
                if not base_url.endswith('/'):
                    base_url += '/'
                proxied_path = path[len(prefix):] if path.startswith(prefix) else path
                target_url = urljoin(base_url, proxied_path)

                resp = requests.request(
                    method=request.method,
                    url=target_url,
                    headers={key: value for (key, value) in request.headers if key != 'Host'},
                    data=request.get_data(),
                    cookies=request.cookies,
                    allow_redirects=False)

                # Handle redirects
                if resp.status_code in (301, 302, 303, 307, 308):
                    location = resp.headers.get('Location', '')
                    if location.startswith('/'):
                        # Assuming the application is mounted at the root of the domain
                        new_location = f"/{prefix}{location}"
                        return redirect(new_location, code=resp.status_code)

                # Forward the response
                excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection', 'location']
                headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
                response = Response(resp.content, resp.status_code, headers)
                return response

        log_request(path)
        return 'Service not found', 404


    @app.route('/test', methods=['GET'])
    def test_route():
        return 'Test route is working', 200



    # WebSocket Proxy - Example for establishing a WebSocket connection to a service
    @sio.event
    def connect():
        print('Successfully connected to the backend WebSocket service.')

    @sio.event
    def disconnect():
        print('Disconnected from the backend WebSocket service.')
    

    app.run(host=host, port=port, debug=True)  # Run the Flask app

if __name__ == '__main__':
    cfg_path = Path(__file__).parent / "path2url.json"
    cfg = get_proxy_config(cfg_path)

    serve(host="192.168.1.77", port=5000, proxy_config=cfg)