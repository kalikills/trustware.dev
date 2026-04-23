from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


def load_redirects(site_root: Path) -> list[tuple[str, str, int]]:
    redirects_path = site_root / "_redirects"
    if not redirects_path.exists():
        return []

    rules: list[tuple[str, str, int]] = []
    for raw_line in redirects_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        parts = line.split()
        if len(parts) < 2:
            continue

        source = parts[0]
        target = parts[1]
        status = 302

        if len(parts) >= 3:
            try:
                status = int(parts[2])
            except ValueError:
                status = 302

        if source.startswith("/"):
            rules.append((source, target, status))

    return rules


class PreviewRequestHandler(SimpleHTTPRequestHandler):
    redirect_rules: list[tuple[str, str, int]] = []

    def do_GET(self) -> None:
        if self._handle_redirect():
            return
        super().do_GET()

    def do_HEAD(self) -> None:
        if self._handle_redirect():
            return
        super().do_HEAD()

    def _handle_redirect(self) -> bool:
        request_path = urlsplit(self.path).path

        for source, target, status in self.redirect_rules:
            if request_path != source:
                continue

            self.send_response(status)
            self.send_header("Location", target)
            self.end_headers()
            return True

        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Trustware local preview server")
    parser.add_argument("--bind", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=15000)
    parser.add_argument("--directory", default=str(Path(__file__).resolve().parent.parent))
    args = parser.parse_args()

    site_root = Path(args.directory).resolve()
    PreviewRequestHandler.redirect_rules = load_redirects(site_root)
    handler_class = partial(PreviewRequestHandler, directory=str(site_root))

    with ThreadingHTTPServer((args.bind, args.port), handler_class) as server:
        print(f"Serving Trustware preview from {site_root}")
        print(f"Listening on http://{args.bind}:{args.port}/")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
