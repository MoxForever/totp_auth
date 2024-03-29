def parse_host_port(data: str) -> tuple[str, int]:
    if ":" in data:
        host, port = data.split(":", 1)
        if port.isnumeric():
            port = int(port)
        else:
            raise ValueError("Port must be number")
    else:
        host, port = data, 80

    return host, port
