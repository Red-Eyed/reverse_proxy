# Reverse Proxy Configuration Tool

This tool allows you to quickly configure and deploy a reverse proxy using NGINX within a Docker container. The configuration is driven by a simple JSON file (`path2url.json`) which maps paths to URLs for the reverse proxy to forward requests to.

## Getting Started

Follow these steps to configure and run your reverse proxy.

### Prerequisites

Ensure you have the following installed:
- Docker
- Docker Compose
- Python (if you need to generate a new NGINX configuration)

### Configuration

1. Clone the repository:
```bash
git clone https://github.com/Red-Eyed/reverse_proxy.git
cd reverse_proxy
```

2. Edit the `path2url.json` file to define your path to URL mappings. The format is as follows:
```json
{
  "/path1": "http://example1.com",
  "/path2": "http://example2.com"
}
```
This configuration will forward requests from `http://yourdomain.com/path1/` to `http://example1.com` and `http://yourdomain.com/path2/` to `http://example2.com`.

### Generate NGINX Configuration

Run the Python script to generate the NGINX configuration file based on your `path2url.json`:

```bash
python generate_nginx_conf.py
```

This will create or overwrite the `default.conf` file in the `nginx` directory, used by NGINX in the Docker container.

### Running the Reverse Proxy

Use Docker Compose to build and start the reverse proxy:

```bash
docker-compose up -d
```

This command will build the Docker image (if necessary) and start the reverse proxy container in detached mode. Your reverse proxy is now up and running, forwarding requests based on your configuration.

## Stopping the Service

To stop the reverse proxy, use the following Docker Compose command:

```bash
docker-compose down
```

## Contributing

Contributions to improve this tool are welcome. Please feel free to submit issues and pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
