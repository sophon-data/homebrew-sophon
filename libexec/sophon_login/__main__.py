"""Entry point: `python3 -m sophon_login <subcommand>`."""

from __future__ import annotations

import sys

from sophon_login.commands import cmd_login, cmd_logout


def main(argv: list[str]) -> int:
    if not argv:
        sys.stderr.write("sophon-login: missing subcommand (login|logout)\n")
        return 2
    sub, rest = argv[0], argv[1:]
    if sub == "login":
        return cmd_login(rest)
    if sub == "logout":
        return cmd_logout(rest)
    sys.stderr.write(f"sophon-login: unknown subcommand '{sub}'\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
