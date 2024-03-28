# TOTP Auth 
The project was created as a convenient utility for adding top authorization to your site without changing the source code.

## Details
The project was built on python and pip so that it can be easily installed with 1 command if you have a python environment. 

### Technology support
| Technology   | With Header Rewrite | Without Header Rewrite |
|--------------|---------------------|------------------------|
| HTTP         | Yes                 | Yes                    |
| WebSocket    | No                  | Yes                    |
| EventStream  | No                  | Yes                    |

### TODO List
- [ ] Create web interface for configuration
- [ ] Light-weight version with 1 rewrite for implementing in docker containers
- [ ] Migrate from .ini config to sqlite
- [ ] Add password support
- [ ] Rate limits for protect of bruteforce
- [ ] Login page customization

## Installation

Installation from pip is easy:
```bash
pip install totp_auth
```

## Usage

All interaction goes through `totp-auth-cli`. 

### Run server

```bash
totp-auth-cli run
```

### 