CREATE TABLE IF NOT EXISTS app_config (
    secret_token TEXT
);

CREATE TABLE IF NOT EXISTS servers (
    id INTEGER NOT NULL PRIMARY KEY,
    listen_host TEXT NOT NULL,
    listen_port INTEGER NOT NULL,
    rewrite_host TEXT NOT NULL,
    rewrite_port INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY NOT NULL,
    username TEXT NOT NULL,
    totp_secret TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS headers_rewrite (
    id INTEGER PRIMARY KEY NOT NULL,
    value TEXT NOT NULL,
    header TEXT NOT NULL,
    server_id INTEGER NOT NULL,
    FOREIGN KEY(server_id) REFERENCES server(id)
);

CREATE TABLE IF NOT EXISTS users_access (
    user_id INTEGER NOT NULL,
    server_id INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES user(id),
    FOREIGN KEY(server_id) REFERENCES server(id)
);
