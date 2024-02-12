
from __future__ import annotations

__author__ = "Vadym Stupakov"
__maintainer__ = "Vadym Stupakov"
__email__ = "vadim.stupakov@gmail.com"

from pathlib import Path
from flask import Flask, request, Response, redirect
import requests
import json
from urllib.parse import urljoin
from argparse import ArgumentParser


def get_proxy_config(p: Path):
    return json.loads(p.read_text())

def get_target_url(path, prefix, base_url):
    # Ensure base_url ends with '/'
    base_url = base_url.rstrip('/') + '/'

    proxied_path = path[len(prefix):] if path.startswith(prefix) else path
    target_url = urljoin(base_url, proxied_path.lstrip('/'))
    return target_url

def build_app(proxy_config: dict[str, str]):
    app = Flask(__name__)

    @app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
    def proxy(path):
        for prefix, base_url in proxy_config.items():
            if path.startswith(prefix):
                target_url = get_target_url(path, prefix, base_url)

                headers = {key: value for (key, value) in request.headers if key != 'Host'}
                headers['X-Forwarded-Host'] = request.host
                headers['X-Forwarded-For'] = request.remote_addr

                # Make the proxied request
                resp = requests.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    data=request.get_data(),
                    cookies=request.cookies,
                    allow_redirects=False)

                # Forward the response, including cookies
                excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
                headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
                response = Response(resp.content, resp.status_code, headers)
                for cookie in resp.cookies:
                    response.set_cookie(cookie.name, cookie.value, path=f"/{prefix}", secure=cookie.secure, httponly=cookie.httponly)
                return response

        return 'Service not found', 404

    return app

def serve(app: Flask, host, port, debug):
    kw = dict(host=host, port=port)
    if debug:
        return app.run(**kw, debug=debug)
    else:
        from waitress import serve
        return serve(app, **kw, threads=100)

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--ip", type=str, required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--cfg_path", type=Path, default=Path(__file__).parent / "path2url.json")
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    return args

def main():
    args = parse_args()
    cfg = get_proxy_config(args.cfg_path)


    app = build_app(proxy_config=cfg)
    serve(app, args.ip, args.port, args.debug)


if __name__ == '__main__':
    main()