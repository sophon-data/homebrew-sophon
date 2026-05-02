# homebrew-sophon

Homebrew tap for [Sophon](https://github.com/sophon-data/sophon).

## Install

```bash
brew install sophon-data/sophon/sophon
sophon login    # one-time, prompts for a GitHub PAT (read:packages scope)
sophon start
```

Open **http://app.localhost:8080**.

(`*.localhost` resolves to `127.0.0.1` in every modern browser per RFC 6761 — no DNS or `/etc/hosts` setup needed.)

## Commands

| Command | What it does |
|---|---|
| `sophon login` | Authenticate Docker with `ghcr.io` (one-time, asks for GitHub PAT) |
| `sophon start` | Pull images and bring the stack up |
| `sophon stop` | Stop containers, keep the database volume |
| `sophon update` | Pull latest images and recreate containers |
| `sophon logs [service]` | Tail logs (e.g. `sophon logs backend`) |
| `sophon status` | List running services |
| `sophon uninstall` | Stop containers and delete the local database volume |

## Requirements

- macOS or Linux
- [Docker Desktop](https://www.docker.com/products/docker-desktop) (or Docker Engine + Compose v2)
- A GitHub account with access to the `sophon-data` org's container registry. If you can't pull `ghcr.io/sophon-data/sophon-backend`, ask Jake to add you.
- ~2 GB free disk for images and Postgres data

## Linux: secure your PAT

Docker stores GHCR credentials in `~/.docker/config.json`. On macOS with Docker Desktop they go to the Keychain. **On Linux without a credential helper, your PAT is written to that file in plaintext.** Install `docker-credential-pass` (or `docker-credential-secretservice`) and configure Docker to use it before running `sophon login`. See [Docker's credential-store docs](https://docs.docker.com/engine/reference/commandline/login/#credential-stores).

## Privacy

The backend mounts `~/.claude/projects` **read-only**. All parsed data lives in a local Docker volume (`sophon_postgres-data`). Nothing leaves your machine. Both published ports (`8080`, `8001`) bind to `127.0.0.1` only.

## Uninstall

```bash
sophon uninstall    # stop and wipe the database volume
brew uninstall sophon
brew untap sophon-data/sophon
```
