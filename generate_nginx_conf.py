from pathlib import Path

LOCALDIR = Path(__file__).parent.resolve()

path2url = {
    "/netron": "http://localhost:8080",
    # "/anotherpath": "http://localhost:9090",
    # Add more path mappings as needed
}

nginx_conf_template = """
server {{
    listen 4443;

{locations}

    location / {{
        return 404;
    }}
}}
"""

location_block_template = """
    location {path} {{
        rewrite ^{path}(/.*)$ $1 break;
        proxy_pass {url};
        include /config/nginx/proxy.conf;  # Includes common proxy settings
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
    filename = LOCALDIR / "config/nginx/site-confs/default.conf"
    generate_nginx_conf(path2url)
