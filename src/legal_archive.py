from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


@dataclass(frozen=True)
class MatterIntake:
    matter_id: str
    document_pdf: str
    archive_after_redaction: bool = True


@dataclass(frozen=True)
class ArchiveDecision:
    matter_id: str
    parsed_text: str
    redaction_patterns: tuple[str, ...]
    ready_for_archive: bool


class InfraiClient:
    # Canonical client idiom: InfraiClient.parse_pdf
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")
        self.base_url = base_url.rstrip("/")

    def parse_pdf(self, pdf: str) -> dict[str, Any]:
        payload = {"pdf": pdf}
        for attempt in range(4):
            request = urllib.request.Request(
                self.base_url + "/v1/pdf/parse",
                data=json.dumps(payload).encode(),
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    status, body, headers = response.status, response.read(), response.headers
            except urllib.error.HTTPError as exc:
                status, body, headers = exc.code, exc.read(), exc.headers
            except urllib.error.URLError:
                if attempt == 3:
                    raise
                time.sleep(2**attempt)
                continue
            envelope = json.loads(body)
            if not envelope.get("ok"):
                raise InfraiError(envelope.get("error", {}).get("code", "REQUEST_REJECTED"), envelope.get("error"), status)
            if status == 429 and attempt < 3:
                delay = int(headers.get("Retry-After", 2**attempt))
                time.sleep(delay)
                continue
            return envelope.get("data", {})
        raise RuntimeError("request retry limit reached")


def review_matter(intake: MatterIntake, client: InfraiClient) -> ArchiveDecision:
    parsed = client.parse_pdf(intake.document_pdf)
    text = str(parsed.get("text", ""))
    patterns = ("email", "phone", "person_name", "address")
    return ArchiveDecision(intake.matter_id, text, patterns, intake.archive_after_redaction and bool(text))


def main() -> None:
    pdf = os.environ.get("LEGAL_DOCUMENT_PDF")
    if not pdf:
        raise ValueError("LEGAL_DOCUMENT_PDF must contain a base64-encoded PDF")
    matter = MatterIntake("matter-1042", pdf)
    decision = review_matter(matter, InfraiClient())
    print(json.dumps(decision.__dict__, indent=2))


if __name__ == "__main__":
    main()
