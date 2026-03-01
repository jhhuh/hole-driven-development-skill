"""
Web crawler: given a starting URL, crawl all links up to max_depth levels deep.
Returns dict mapping each visited URL to its outgoing links.
Respects robots.txt. Skips non-HTML content types.
"""

import collections
import urllib.parse
import urllib.request
import urllib.robotparser
from html.parser import HTMLParser


# ---------------------------------------------------------------------------
# Sub-component: robots.txt checker
# ---------------------------------------------------------------------------
def _make_robot_checker(url):
    """Return a urllib.robotparser.RobotFileParser for the given URL's domain.
    Expects: RobotFileParser (loaded, ready for .can_fetch())
    """
    parsed = urllib.parse.urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception:
        # If robots.txt is unreachable, allow everything (per convention).
        rp.allow_all = True
    return rp


# ---------------------------------------------------------------------------
# Sub-component: fetch page
# ---------------------------------------------------------------------------
def _fetch_page(url):
    """Fetch *url*, return its HTML body as str, or None if non-HTML / error.
    Must check Content-Type header; only proceed for text/html.
    Expects: str | None
    """
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "crawl_links/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content_type = resp.headers.get("Content-Type", "")
            if "text/html" not in content_type:
                return None
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.read().decode(charset, errors="replace")
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Sub-component: parse links from HTML
# ---------------------------------------------------------------------------
def _parse_links(html, base_url):
    """Extract all <a href=...> links from *html*, resolve relative URLs
    against *base_url*, and return only http/https URLs.
    Expects: list[str]
    """
    class _LinkParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.links = []

        def handle_starttag(self, tag, attrs):
            if tag == "a":
                for name, value in attrs:
                    if name == "href" and value:
                        self.links.append(value)

    parser = _LinkParser()
    try:
        parser.feed(html)
    except Exception:
        pass

    resolved = []
    for href in parser.links:
        full = urllib.parse.urljoin(base_url, href)
        # Strip fragment
        parts = urllib.parse.urlparse(full)
        if parts.scheme in ("http", "https"):
            clean = urllib.parse.urlunparse(parts._replace(fragment=""))
            resolved.append(clean)
    return resolved


# ---------------------------------------------------------------------------
# Sub-component: robots.txt permission check (uses cached checkers)
# ---------------------------------------------------------------------------
def _is_allowed(url, robot_cache):
    """Return True if robots.txt allows fetching *url*.
    Uses *robot_cache* (dict[str, RobotFileParser]) to avoid re-fetching.
    Expects: bool
    """
    parsed = urllib.parse.urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    if origin not in robot_cache:
        robot_cache[origin] = _make_robot_checker(url)
    return robot_cache[origin].can_fetch("crawl_links/1.0", url)


# ---------------------------------------------------------------------------
# Main crawl loop
# ---------------------------------------------------------------------------
def crawl_links(url, max_depth=2):
    """
    Given a starting URL, crawl all links up to max_depth levels deep.
    Return a dict mapping each visited URL to the list of URLs it links to.
    Respect robots.txt. Skip non-HTML content types.
    """
    result = {}           # dict[str, list[str]]
    robot_cache = {}       # dict[str, RobotFileParser]
    visited = set()
    queue = collections.deque()
    queue.append((url, 0))

    while queue:
        current_url, depth = queue.popleft()
        if current_url in visited:
            continue
        visited.add(current_url)

        if not _is_allowed(current_url, robot_cache):
            continue

        html = _fetch_page(current_url)
        if html is None:
            # Non-HTML or fetch error -- record but don't parse links.
            result[current_url] = []
            continue

        links = _parse_links(html, current_url)
        result[current_url] = links

        if depth < max_depth:
            for link in links:
                if link not in visited:
                    queue.append((link, depth + 1))

    return result
