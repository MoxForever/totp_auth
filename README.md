# TOTP Auth 
The project was created as a convenient utility for adding TOTP authorization to your site without changing your project.

### Technology support
| Technology   | With Header Rewrite | Without Header Rewrite |
|--------------|---------------------|------------------------|
| HTTP         | Yes                 | Yes                    |
| WebSocket    | No                  | Yes                    |
| EventStream  | No                  | Yes                    |

### TODO List
- [ ] Create web interface for configuration
- [ ] Light-weight version with 1 rewrite for implementing in docker containers
- [x] Migrate from .ini config to sqlite
- [ ] Add classic password support
- [ ] Rate limits for protect of bruteforce
- [ ] Login page customization

## Installation

Installation from pip is easy:
```bash
pip install totp_auth
```

## Usage

All interaction goes through `totp-auth`. 

### Run server

```bash
totp-auth run
```

### 