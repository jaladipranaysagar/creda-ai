"""Explainable, offline heuristics for an early defensive MVP."""

import re
from dataclasses import dataclass
from urllib.parse import urlparse


URL_PATTERN = re.compile(r"(?:https?://|www\.)[^\s<>\"]+", re.IGNORECASE)
SUSPICIOUS_TERMS = {
    "urgent": 12,
    "verify your account": 20,
    "account suspended": 20,
    "account locked": 18,
    "password": 8,
    "otp": 12,
    "one time password": 12,
    "gift card": 18,
    "crypto": 10,
    "bitcoin": 10,
    "wire transfer": 18,
    "bank details": 16,
    "claim now": 12,
    "limited time": 8,
    "click here": 8,
    "you have won": 18,
    "refund": 8,
}
SUSPICIOUS_TLDS = {"zip", "mov", "top", "xyz",
                   "click", "country", "gq", "tk", "work"}
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "rb.gy", "is.gd", "cutt.ly"}


@dataclass
class Finding:
    label: str
    detail: str
    points: int


def _add(findings: list[Finding], label: str, detail: str, points: int) -> None:
    findings.append(Finding(label, detail, points))


def analyze(content: str) -> tuple[int, str, str, list[Finding]]:
    """Return score, level, category, and human-readable reasons for submitted content."""
    value = content.strip()
    lower = value.lower()
    findings: list[Finding] = []

    matched_terms = [term for term in SUSPICIOUS_TERMS if term in lower]
    if matched_terms:
        points = min(sum(SUSPICIOUS_TERMS[term] for term in matched_terms), 35)
        _add(findings, "Social-engineering language",
             f"Detected: {', '.join(matched_terms[:4])}.", points)

    if re.search(r"\b(?:act now|immediately|within \d+ hours?|final warning)\b", lower):
        _add(findings, "Pressure tactic",
             "The message tries to create urgency or fear.", 14)
    if re.search(r"\b(?:password|pin|cvv|security code|login credentials)\b", lower):
        _add(findings, "Sensitive-data request",
             "It mentions information legitimate services should not request by message.", 18)
    if value.count("!") >= 3 or re.search(r"\b[A-Z]{5,}\b", value):
        _add(findings, "Manipulative formatting",
             "Excessive exclamation marks or all-caps wording can signal pressure.", 7)

    urls = URL_PATTERN.findall(value)
    for raw_url in urls[:3]:
        normalized = raw_url if raw_url.lower().startswith(
            "http") else f"https://{raw_url}"
        parsed = urlparse(normalized)
        host = (parsed.hostname or "").lower()
        suffix = host.rsplit(".", 1)[-1] if "." in host else ""
        if parsed.scheme == "http":
            _add(findings, "Unencrypted link",
                 f"{raw_url} uses HTTP rather than HTTPS.", 12)
        if host in SHORTENERS:
            _add(findings, "Shortened link",
                 f"{host} hides the final destination.", 18)
        if re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", host):
            _add(findings, "Raw IP address",
                 "The link uses an IP address instead of a recognizable domain.", 22)
        if "xn--" in host:
            _add(findings, "Look-alike domain",
                 "The link uses punycode, which can impersonate familiar names.", 24)
        if suffix in SUSPICIOUS_TLDS:
            _add(findings, "Higher-risk domain ending",
                 f".{suffix} is frequently abused in low-cost scam campaigns.", 12)
        if host.count("-") >= 2 or len(host.split(".")[0]) > 28:
            _add(findings, "Unusual domain structure",
                 "The domain has a pattern commonly seen in disposable phishing sites.", 9)

    score = min(sum(f.points for f in findings), 100)
    if score >= 60:
        level, category = "high", "Likely scam or phishing"
    elif score >= 30:
        level, category = "medium", "Suspicious content"
    else:
        level, category = "low", "No strong warning signs"
    return score, level, category, findings
