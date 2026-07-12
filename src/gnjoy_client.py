from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import httpx


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}


@dataclass(frozen=True)
class FetchResult:
    url: str
    status_code: int
    html: str

    @property
    def byte_count(self) -> int:
        return len(self.html.encode("utf-8"))

    @property
    def text_preview(self) -> str:
        return " ".join(self.html[:500].split())


class GnjoyClient:
    def __init__(
        self,
        delay_seconds: float = 1.0,
        logger: Callable[[str], None] | None = None,
        debug_dir: Path | None = None,
    ):
        self.delay_seconds = delay_seconds
        self.logger = logger
        self.debug_dir = debug_dir
        self.client = httpx.Client(
            headers=HEADERS,
            timeout=30,
            follow_redirects=True,
        )

    def get(self, url: str, cache_name: str | None = None) -> FetchResult:
        self._log(f"URL: {url}")
        time.sleep(self.delay_seconds)

        response = self.client.get(url)
        response.raise_for_status()
        result = FetchResult(
            url=str(response.url),
            status_code=response.status_code,
            html=response.text,
        )

        self._log(
            "RETORNO: "
            f"status={result.status_code} bytes={result.byte_count} "
            f"preview={result.text_preview}"
        )

        if self.debug_dir is not None and cache_name is not None:
            self.debug_dir.mkdir(parents=True, exist_ok=True)
            (self.debug_dir / cache_name).write_text(result.html, encoding="utf-8")

        return result

    def close(self) -> None:
        self.client.close()

    def _log(self, message: str) -> None:
        if self.logger is not None:
            self.logger(message)
        print(f"[GNJOY] {message}", flush=True)
