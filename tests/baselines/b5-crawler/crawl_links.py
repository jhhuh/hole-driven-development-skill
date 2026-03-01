"""Breadth-first link crawler using only the standard library."""

from collections import deque
from html.parser import HTMLParser
from urllib.parse import urljoin, urldefrag, urlparse
from urllib.request import urlopen, Request
from urllib.robotparser import RobotFileParser
from urllib.error import URLError, HTTPError
import socket


class _LinkExtractor(HTMLParser):
    """Extract href values from <a> tags."""

    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, value in attrs:
                if name == "href" and value:
                    self.links.append(value)


def _fetch_robots(scheme, netloc, timeout):
    """Return a RobotFileParser for the given origin, or None on failure."""
    rp = RobotFileParser()
    robots_url = f"{scheme}://{netloc}/robots.txt"
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception:
        return None
    return rp


def _is_html(response):
    """Check whether the response Content-Type is HTML."""
    ct = response.headers.get("Content-Type", "")
    return "text/html" in ct


def crawl_links(url, max_depth=2):
    """
    Given a starting URL, crawl all links up to max_depth levels deep.
    Return a dict mapping each visited URL to the list of URLs it links to.
    Respect robots.txt. Skip non-HTML content types.
    Use only the standard library (urllib, html.parser).
    """
    user_agent = "PythonCrawler/1.0"
    timeout = 10
    result = {}
    # (url, depth) pairs
    queue = deque([(url, 0)])
    visited = set()
    # Cache robots parsers per origin (scheme://netloc)
    robots_cache = {}

    while queue:
        current_url, depth = queue.popleft()

        # Strip fragment
        current_url, _ = urldefrag(current_url)

        if current_url in visited:
            continue
        visited.add(current_url)

        parsed = urlparse(current_url)

        # Only crawl http(s)
        if parsed.scheme not in ("http", "https"):
            continue

        # Check robots.txt
        origin = (parsed.scheme, parsed.netloc)
        if origin not in robots_cache:
            robots_cache[origin] = _fetch_robots(parsed.scheme, parsed.netloc, timeout)
        rp = robots_cache[origin]
        if rp and not rp.can_fetch(user_agent, current_url):
            continue

        # Fetch the page
        try:
            req = Request(current_url, headers={"User-Agent": user_agent})
            with urlopen(req, timeout=timeout) as resp:
                if not _is_html(resp):
                    continue
                body = resp.read().decode("utf-8", errors="replace")
        except (URLError, HTTPError, socket.timeout, UnicodeDecodeError, OSError):
            continue

        # Extract links
        parser = _LinkExtractor()
        try:
            parser.feed(body)
        except Exception:
            continue

        child_urls = []
        for href in parser.links:
            absolute = urljoin(current_url, href)
            absolute, _ = urldefrag(absolute)
            child_urls.append(absolute)

        result[current_url] = child_urls

        # Enqueue children if within depth limit
        if depth < max_depth:
            for child in child_urls:
                if child not in visited:
                    queue.append((child, depth + 1))

    return result
