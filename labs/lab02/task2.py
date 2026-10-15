import csv
import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

REQUIRED_HEADERS = {
    "strict-transport-security": "Strict-Transport-Security",
    "content-security-policy": "Content-Security-Policy",
    "x-frame-options": "X-Frame-Options",
    "x-content-type-options": "X-Content-Type-Options",
}


@dataclass
class ResourceAuditResult:
    url: str
    score: int
    grade: str
    status: str
    missing_headers: list[str]
    leaks: list[str]


class HeaderAuditor:
    def __init__(self, filepath: str | Path, strict: bool = False) -> None:
        self.filepath = Path(filepath)
        self.strict = strict
        self.raw_data: dict[str, dict[str, str]] = {}
        self.results: list[ResourceAuditResult] = []
        self.version_pattern = re.compile(r"\d+(\.\d+)+")

    def load_data(self) -> None:
        if not self.filepath.exists():
            raise FileNotFoundError(f"File not found: {self.filepath}")

        with self.filepath.open(mode="r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            self.raw_data = {
                item["url"]: item.get("headers", {})
                for item in data
                if isinstance(item, dict) and "url" in item
            }
        elif isinstance(data, dict):
            self.raw_data = data
        else:
            self.raw_data = {}

    def check_version_leaks(self, headers_lower: dict[str, str]) -> list[str]:
        leaks: list[str] = []

        server_val = headers_lower.get("server")
        if server_val and self.version_pattern.search(server_val):
            leaks.append(f"version in 'Server': {server_val}")

        x_powered = headers_lower.get("x-powered-by")
        if x_powered and self.version_pattern.search(x_powered):
            leaks.append(f"tech stack in 'X-Powered-By': {x_powered}")

        return leaks

    def audit_resource(self, url: str, headers: dict[str, str]) -> ResourceAuditResult:
        headers_lower = {k.lower(): v for k, v in headers.items()}
        missing_headers: list[str] = []

        for header_key, header_name in REQUIRED_HEADERS.items():
            if header_key not in headers_lower:
                missing_headers.append(header_name)

        if missing_headers:
            logger.warning(
                "Resource %s missing security headers: %s",
                url,
                ", ".join(missing_headers),
            )

        leaks = self.check_version_leaks(headers_lower)

        score = max(0, 100 - (len(missing_headers) * 20 + len(leaks) * 10))

        if score >= 85:
            grade = "A+"
            status = "PASS"
        elif score >= 60:
            grade = "C"
            status = "WARN"
        else:
            grade = "F"
            status = "FAIL"

        if self.strict and (missing_headers or leaks):
            status = "FAIL"

        return ResourceAuditResult(
            url=url,
            score=score,
            grade=grade,
            status=status,
            missing_headers=missing_headers,
            leaks=leaks,
        )

    def run_audit(self) -> list[ResourceAuditResult]:
        if not self.raw_data:
            self.load_data()

        self.results = [
            self.audit_resource(url, headers) for url, headers in self.raw_data.items()
        ]
        return self.results

    def export_csv(self, output_path: str | Path) -> None:
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        fieldnames = [
            "Resource",
            "Score",
            "Grade",
            "Status",
            "Missing_Headers",
            "Leaks",
        ]
        with out_file.open(mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in self.results:
                writer.writerow(
                    {
                        "Resource": r.url,
                        "Score": f"{r.score}/100",
                        "Grade": r.grade,
                        "Status": r.status,
                        "Missing_Headers": ", ".join(r.missing_headers)
                        if r.missing_headers
                        else "None",
                        "Leaks": "; ".join(r.leaks) if r.leaks else "None",
                    }
                )
