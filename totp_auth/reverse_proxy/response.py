def generate_response_html(status_code: int, status_text: str, body: str) -> bytes:
    return (
        f"HTTP/1.1 {status_code} {status_text}\r\n"
        f"Content-Type: text/html\r\n"
        f"Content-Length: {len(body)}\r\n\r\n{body}"
    ).encode()


def generate_response_unauthorized(body: str) -> bytes:
    return generate_response_html(401, "Unauthorized", body)


def generate_response_uncaught_error(body: str) -> bytes:
    return generate_response_html(
        500, "Internal Server Error", "<h1>Internal Server Error</h1>"
    )


def generate_response_authorized(auth_token: str) -> bytes:
    body = "<html><body><h1>Authorized</h1></body></html>"
    return generate_response_html(
        200, "OK", f"{body}\r\nSet-Cookie: auth_token={auth_token}; HttpOnly"
    )