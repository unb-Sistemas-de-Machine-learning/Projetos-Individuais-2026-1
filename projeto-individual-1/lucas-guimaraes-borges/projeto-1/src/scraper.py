from __future__ import annotations
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from utils.paths import default_events_json

_DEFAULT_URL = "https://www.metropoles.com/agenda-cultural"
_RE_NEXT = re.compile(
    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
    re.DOTALL,
)


class MetropolesAgendaScraper:
    def __init__(
        self,
        url: str = _DEFAULT_URL,
        output_path: str | Path | None = None,
        timeout: float = 60.0,
        user_agent: str = "Mozilla/5.0 (compatible; AgendaScraper/1.0)",
    ) -> None:
        self.url = url
        self.output_path = Path(output_path) if output_path else default_events_json()
        self.timeout = timeout
        self._user_agent = user_agent

    def fetch_html(self) -> str:
        req = urllib.request.Request(
            self.url,
            headers={"User-Agent": self._user_agent},
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")

    def _next_data_dict(self, html: str) -> dict[str, Any]:
        m = _RE_NEXT.search(html)
        if not m:
            raise RuntimeError("Não encontrado __NEXT_DATA__")
        return json.loads(m.group(1))

    @staticmethod
    def build_payload(agenda: dict[str, Any], source_url: str) -> dict[str, Any]:
        featured = agenda.get("featured_events") or []
        by_day = agenda.get("events") or []
        flat: list[dict[str, Any]] = []
        for fe in featured:
            r = dict(fe)
            r["_source"] = "featured"
            flat.append(r)
        for block in by_day:
            d = block.get("date")
            for ev in block.get("events") or []:
                r = dict(ev)
                r["agenda_date"] = d
                r["_source"] = "calendar"
                flat.append(r)
        return {
            "url": source_url,
            "featured_events": featured,
            "events_by_date": by_day,
            "events_flat": flat,
        }

    def scrape(self) -> dict[str, Any]:
        html = self.fetch_html()
        root = self._next_data_dict(html)
        agenda = root["props"]["pageProps"]["conteudoAgendaCultural"]
        return self.build_payload(agenda, self.url)

    def save(self, data: dict[str, Any], path: str | Path | None = None) -> None:
        out = Path(path) if path else self.output_path
        with open(out, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def run(self) -> dict[str, Any]:
        try:
            data = self.scrape()
        except urllib.error.URLError as e:
            sys.exit(f"Erro: {e}")
        except (KeyError, RuntimeError) as e:
            sys.exit(str(e))
        self.save(data)
        n = len(data["events_flat"])
        print(f"Gravado: {self.output_path} ({n} eventos)", file=sys.stderr)
        return data


agenda_scraper = MetropolesAgendaScraper()
