import json
from pathlib import Path

LOCALDIR = Path(__file__).parent.resolve()

nginx_conf_template = """
server {{
    listen 4443;

{locations}

    location / {{
        return 404;
    }}
}}

map $http_upgrade $connection_upgrade {{
    # If the Upgrade header is present, set Connection to "upgrade"
    default upgrade;

    # If the Upgrade header is not present, set Connection to "close"
    '' close;
}}
"""

location_block_template = """
    location {path} {{
        # Proxy the request to the backend server running on a specific port
        proxy_pass {url};

        # Use HTTP/1.1 for the connection to the backend server
        proxy_http_version 1.1;

        # Pass the Upgrade header from the client to the backend server, necessary for WebSocket connections
        proxy_set_header Upgrade $http_upgrade;

        # Use the value of $connection_upgrade for the Connection header, determined by the map block
        proxy_set_header Connection $connection_upgrade;

        # Pass the original Host header to the backend server
        proxy_set_header Host $host;

        # Pass the client IP address to the backend server, useful for logging and analytics
        proxy_set_header X-Real-IP $remote_addr;

        # Pass the original request's IP addresses (client, proxies) to the backend server
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # Pass the scheme (http or https) used by the client to the backend server
        proxy_set_header X-Forwarded-Proto $scheme;

        # Turn off buffering to stream responses directly to the client, beneficial for WebSockets and streaming responses
        proxy_buffering off;
    }}
"""


def generate_location_blocks(path2url):
    location_blocks = ""
    for path, url in path2url.items():
        location_blocks += location_block_template.format(path=path, url=url)
    return location_blocks


def generate_nginx_conf(path2url: dict[str, str], filename: Path):
    locations = generate_location_blocks(path2url)
    nginx_conf = nginx_conf_template.format(locations=locations)

    filename.parent.mkdir(parents=True, exist_ok=True)
    filename.write_text(nginx_conf)
    print(f"NGINX configuration written to {filename}")


if __name__ == "__main__":
    config = LOCALDIR / "config/nginx/site-confs/default.conf"
    path2url = json.loads((LOCALDIR / "path2url.json").read_text())

    generate_nginx_conf(path2url, config)
