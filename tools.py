"""tools.py - STUDENT IMPLEMENTS.  Source tools for the research agents.   Guide: GUIDE.md, part 1.

Rules for every tool:
  * runs on the HOST (not in the sandbox): API keys must never enter the sandbox;
  * returns a STRING (JSON text of compact records) and NEVER raises:
        "NO RESULTS"  when the source answers with nothing,
        "ERROR: ..."  when the source keeps failing after the retries (the agent then tries another source);
  * the docstring is the tool description the LLM reads: keep it precise (what it does, what it returns, when to use it).
Try your tools without any agent:   python tools.py
"""
import json
import os
import random
import re
import threading
import time
import xml.etree.ElementTree as ET
from urllib.parse import urlencode

import httpx  # noqa: F401
from langchain_core.tools import tool

# ---- constants (given) ----
ARXIV_URL = "https://export.arxiv.org/api/query"  # https only: http answers 301
HF_DAILY_URL = "https://huggingface.co/api/daily_papers"
HF_SEARCH_URL = "https://huggingface.co/api/papers/search"
EXA_URL = "https://mcp.exa.ai/mcp"


class RetryableError(Exception):
    """Given. Raise it inside a call to ask with_retry to wait and try again (retry_after in seconds, optional)."""

    def __init__(self, message, retry_after=None):
        super().__init__(message)
        self.retry_after = retry_after


# ---- TODO 1: retry helper ----
def with_retry(fn, *, attempts=5, base=1.0, cap=30.0):
    """Call fn(); when it raises RetryableError, wait and call it again.

    PSEUDO-CODE:
      for attempt in 0 .. attempts-1:
          try: return fn()
          except RetryableError as e:
              if this was the last attempt: raise
              delay = e.retry_after if the server told us, else exponential backoff base * 2**attempt
              cap the delay at `cap` seconds; add random jitter to the exponential case
              sleep(delay)
    Use it to wrap EVERY network call below. Also treat these as retryable: HTTP 429/500/502/503/504,
    httpx.TransportError (timeouts, connection resets). Read the Retry-After header when present.
    """
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    for attempt in range(attempts):
        try:
            return fn()
        except RetryableError as exc:
            if attempt == attempts - 1:
                raise
            if exc.retry_after is not None:
                delay = min(cap, max(0.0, float(exc.retry_after)))
            else:
                delay = min(cap, base * (2**attempt))
                delay = min(cap, delay + random.uniform(0, max(0.01, delay * 0.25)))
            time.sleep(delay)


_ARXIV_LOCK = threading.Lock()
_LAST_ARXIV_CALL = 0.0
_RETRYABLE_STATUSES = {429, 500, 502, 503, 504}


def _clean_text(value, limit=None):
    text = " ".join(str(value or "").split())
    return text[:limit] if limit else text


def _retry_after(response):
    value = response.headers.get("Retry-After")
    try:
        return float(value) if value is not None else None
    except ValueError:
        return None


def _request(method, url, **kwargs):
    def call():
        try:
            response = httpx.request(method, url, timeout=30, follow_redirects=True, **kwargs)
        except httpx.TransportError as exc:
            raise RetryableError(str(exc)) from exc
        if response.status_code in _RETRYABLE_STATUSES:
            raise RetryableError(f"HTTP {response.status_code}", _retry_after(response))
        response.raise_for_status()
        return response

    return with_retry(call)


def _result(records):
    return json.dumps(records, ensure_ascii=False) if records else "NO RESULTS"


def _error(exc, secret=None):
    message = f"{type(exc).__name__}: {exc}"
    if secret:
        message = message.replace(secret, "[REDACTED]")
    return f"ERROR: {message}"


def _paper_record(item, *, prefer_ai=False):
    paper = item.get("paper", item) if isinstance(item, dict) else {}
    paper = paper if isinstance(paper, dict) else {}
    paper_id = str(paper.get("id") or "").strip()
    if not paper_id:
        return None
    summary = paper.get("ai_summary") if prefer_ai else None
    summary = summary or paper.get("summary") or item.get("summary") or ""
    published = paper.get("publishedAt") or item.get("publishedAt") or paper.get("published") or ""
    return {
        "id": paper_id,
        "url": f"https://huggingface.co/papers/{paper_id}",
        "published": str(published)[:10],
        "title": _clean_text(paper.get("title") or item.get("title")),
        "summary": _clean_text(summary, 600),
        "upvotes": int(paper.get("upvotes") or item.get("upvotes") or 0),
        "github": paper.get("githubRepo") or item.get("githubRepo") or "",
        "stars": int(paper.get("githubStars") or item.get("githubStars") or 0),
    }


# ---- TODO 2: arXiv ----
@tool
def arxiv_search(query: str, max_results: int = 10) -> str:
    """Search arXiv papers by keywords, newest first. Returns a JSON list of {id, url, published, title, summary}."""
    # PSEUDO-CODE:
    #   keep only word characters of `query` -> terms; no terms -> "NO RESULTS" (do not call the network)
    #   respect arXiv etiquette: at least 3 seconds between two arXiv calls (remember the time of the last call)
    #   GET ARXIV_URL params: search_query="all:t1 AND all:t2 ...", sortBy=submittedDate, sortOrder=descending,
    #       max_results=clamp(max_results, 1, 30)           (wrap in with_retry)
    #   parse the Atom XML: each <entry> -> {id (last part of <id> after /abs/), url, published[:10], title, summary}
    #       collapse whitespace/newlines in title and summary; cut summary to ~600 chars
    #   no entries -> "NO RESULTS"; else json.dumps(records, ensure_ascii=False)
    #   any exception -> "ERROR: <type>: <message>"
    global _LAST_ARXIV_CALL
    try:
        terms = re.findall(r"[\w-]+", query or "", flags=re.UNICODE)
        terms = [term for term in terms if term.upper() not in {"AND", "OR", "NOT"}]
        if not terms:
            return "NO RESULTS"
        params = {
            "search_query": " AND ".join(f"all:{term}" for term in terms),
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "start": 0,
            "max_results": max(1, min(int(max_results), 30)),
        }

        def call():
            global _LAST_ARXIV_CALL
            with _ARXIV_LOCK:
                delay = 3.0 - (time.monotonic() - _LAST_ARXIV_CALL)
                if delay > 0:
                    time.sleep(delay)
                try:
                    response = httpx.get(ARXIV_URL, params=params, timeout=30, follow_redirects=True)
                except httpx.TransportError as exc:
                    _LAST_ARXIV_CALL = time.monotonic()
                    raise RetryableError(str(exc)) from exc
                _LAST_ARXIV_CALL = time.monotonic()
            if response.status_code in _RETRYABLE_STATUSES:
                raise RetryableError(f"HTTP {response.status_code}", _retry_after(response))
            response.raise_for_status()
            return response

        response = with_retry(call, attempts=7, cap=60)
        root = ET.fromstring(response.content)
        ns = {"a": "http://www.w3.org/2005/Atom"}
        records = []
        for entry in root.findall("a:entry", ns):
            raw_id = (entry.findtext("a:id", default="", namespaces=ns).split("/abs/")[-1])
            paper_id = re.sub(r"v\d+$", "", raw_id)
            if not paper_id:
                continue
            records.append({
                "id": paper_id,
                "url": f"https://arxiv.org/abs/{paper_id}",
                "published": entry.findtext("a:published", default="", namespaces=ns)[:10],
                "title": _clean_text(entry.findtext("a:title", default="", namespaces=ns)),
                "summary": _clean_text(entry.findtext("a:summary", default="", namespaces=ns), 600),
            })
        return _result(records)
    except Exception as exc:  # tools must never raise
        return _error(exc)


# ---- TODO 3: Hugging Face ----
@tool
def hf_daily_papers(limit: int = 30, date: str = "", keyword: str = "") -> str:
    """Hugging Face Daily Papers = what is trending in AI research. Returns a JSON list of
    {id, url, published, title, summary, upvotes, github, stars} sorted by upvotes. `date` is YYYY-MM-DD (empty = latest).
    `keyword` filters title/summary; there is no topic search on this endpoint (use hf_search_papers for a topic)."""
    # PSEUDO-CODE:
    #   GET HF_DAILY_URL params: limit (clamp 1..100) and date (only when given)      (with_retry)
    #   response = list of items {"paper": {id, title, summary, upvotes, githubRepo, githubStars, publishedAt}, ...}
    #   map every item to the record shape above (skip items without paper.id); url = https://huggingface.co/papers/<id>
    #   keyword -> keep records whose title+summary contains it (case-insensitive); sort by upvotes descending
    try:
        params = {"limit": max(1, min(int(limit), 100))}
        if date:
            params["date"] = date
        data = _request("GET", HF_DAILY_URL, params=params).json()
        records = [_paper_record(item) for item in data if isinstance(item, dict)]
        records = [record for record in records if record]
        if keyword:
            needle = keyword.casefold()
            records = [r for r in records if needle in (r["title"] + " " + r["summary"]).casefold()]
        records.sort(key=lambda r: r["upvotes"], reverse=True)
        return _result(records)
    except Exception as exc:
        return _error(exc)


@tool
def hf_search_papers(query: str, limit: int = 10) -> str:
    """Search Hugging Face papers by topic. Returns a JSON list of
    {id, url, published, title, summary, upvotes, github, stars}."""
    # PSEUDO-CODE:
    #   GET HF_SEARCH_URL params: q=query, limit (clamp 1..50)                         (with_retry)
    #   same item shape as the daily endpoint; prefer paper["ai_summary"] over paper["summary"] when present
    try:
        if not str(query or "").strip():
            return "NO RESULTS"
        data = _request("GET", HF_SEARCH_URL, params={"q": query, "limit": max(1, min(int(limit), 50))}).json()
        records = [_paper_record(item, prefer_ai=True) for item in data if isinstance(item, dict)]
        return _result([record for record in records if record])
    except Exception as exc:
        return _error(exc)


# ---- TODO 4: web search / fetch through the Exa MCP endpoint ----
@tool
def web_search(query: str, objective: str = "", num_results: int = 5) -> str:
    """Search the web (Exa). Describe the ideal page in natural language. Returns clean text of the top results with URLs."""
    # PSEUDO-CODE:
    #   call the MCP tool "web_search_exa" with arguments {query, objective, numResults}
    #       (objective is REQUIRED by Exa: when empty, build one from the query)
    #   see GUIDE.md part 1.4 for how to call an MCP server over plain HTTP (JSON-RPC "tools/call") and read the answer
    #   read optional env EXA_API_KEY; when present it is sent to the Exa endpoint.
    #       (see GUIDE.md 1.4 for where it goes) => the key then appears in exception text: redact it before returning "ERROR: ..."
    #   WATCH OUT: read GUIDE.md 1.4 about how Exa signals "rate limited" on the free tier, and retry on it
    if not str(query or "").strip():
        return "NO RESULTS"
    return _exa_call("web_search_exa", {
        "query": query,
        "objective": objective or f"Find reliable, relevant sources about {query}",
        "numResults": max(1, min(int(num_results), 10)),
    })


@tool
def web_fetch(url: str) -> str:
    """Read the full content of one web page (e.g. an arXiv abstract page) as markdown. Long pages are truncated."""
    # PSEUDO-CODE: MCP tool "web_fetch_exa" with arguments {"urls": [url]}; truncate the text to ~12000 chars
    if not re.match(r"^https?://", str(url or "")):
        return "ERROR: ValueError: url must start with http:// or https://"
    result = _exa_call("web_fetch_exa", {"urls": [url]})
    return result if result.startswith("ERROR:") or result == "NO RESULTS" else result[:12000]


def _exa_call(name, arguments):
    key = (os.getenv("EXA_API_KEY") or "").strip()
    endpoint = EXA_URL + (("?" + urlencode({"exaApiKey": key})) if key else "")
    payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": arguments}}

    def call():
        try:
            response = httpx.post(endpoint, json=payload,
                                  headers={"Accept": "application/json, text/event-stream"}, timeout=60)
        except httpx.TransportError as exc:
            raise RetryableError(str(exc)) from exc
        if response.status_code in _RETRYABLE_STATUSES:
            raise RetryableError(f"HTTP {response.status_code}", _retry_after(response))
        response.raise_for_status()
        events = []
        content_type = response.headers.get("content-type", "")
        if "text/event-stream" in content_type or response.text.lstrip().startswith("data:"):
            for line in response.text.splitlines():
                if line.startswith("data:"):
                    events.append(json.loads(line[5:].strip()))
        else:
            events.append(response.json())
        if not events:
            raise ValueError("empty MCP response")
        data = events[-1]
        if data.get("error"):
            raise RuntimeError(str(data["error"]))
        result = data.get("result") or {}
        meta = result.get("_meta") or {}
        parts = [part.get("text", "") for part in result.get("content", [])
                 if isinstance(part, dict) and part.get("type") == "text"]
        text = "\n".join(part for part in parts if part).strip()
        rate_blob = (json.dumps(meta, ensure_ascii=False) + " " + text).casefold()
        if (("rate" in rate_blob and "limit" in rate_blob)
                or any(marker in rate_blob for marker in ("too many requests", "429"))):
            retry_after = meta.get("retryAfter") or meta.get("retry_after")
            raise RetryableError("Exa rate limited", retry_after)
        if result.get("isError"):
            raise RuntimeError(text or "MCP tool failed")
        return text or "NO RESULTS"

    try:
        return with_retry(call, attempts=7, base=2, cap=60)
    except Exception as exc:
        return _error(exc, key)


# ---- TODO 5: registry (the researcher subagent gets exactly these) ----
SOURCE_TOOLS = [arxiv_search, hf_daily_papers, hf_search_papers, web_search, web_fetch]


if __name__ == "__main__":
    for name, fn, args in [
        ("arxiv_search", arxiv_search, {"query": "world model", "max_results": 3}),
        ("hf_daily_papers", hf_daily_papers, {"limit": 20}),
        ("hf_search_papers", hf_search_papers, {"query": "world model", "limit": 3}),
        ("web_search", web_search, {"query": "survey paper on world models", "num_results": 2}),
        ("web_fetch", web_fetch, {"url": "https://arxiv.org/abs/1803.10122"}),
    ]:
        try:
            print(f"== {name}\n{fn.invoke(args)[:400]}\n")
        except NotImplementedError as exc:
            print(f"== {name}: not implemented yet ({exc})\n")
