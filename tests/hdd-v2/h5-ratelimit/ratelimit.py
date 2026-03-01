"""
Composable, thread-safe rate limiter with multiple strategies.

Strategies:
  1. Token Bucket: steady-state rate with burst capacity
  2. Sliding Window: exact count over a rolling time window
  3. Per-Client Limiting: separate limits per client ID
  4. Global + Per-Client: compose global and per-client limits

Thread-safe, blocking (acquire) + non-blocking (try_acquire), composable,
with stale per-client cleanup. Uses time.monotonic.
"""

import abc
import threading
import time
from typing import Optional


class RateLimiter(abc.ABC):
    """Base interface for all rate limiters."""

    @abc.abstractmethod
    def _can_acquire_locked(self, client_id: Optional[str] = None) -> bool:
        """Check if acquire would succeed, WITHOUT consuming. Called under lock."""
        ...

    @abc.abstractmethod
    def _try_acquire_locked(self, client_id: Optional[str] = None) -> bool:
        """Attempt to acquire under the caller's lock. Returns True if allowed.

        Subclasses implement this WITHOUT acquiring their own lock --
        the lock is held by the caller (acquire/try_acquire/composite).
        """
        ...

    @abc.abstractmethod
    def _wait_hint_locked(self, client_id: Optional[str] = None) -> float:
        """Seconds to wait before a retry might succeed. Called under lock."""
        ...

    def try_acquire(self, client_id: Optional[str] = None) -> bool:
        """Non-blocking acquire. Returns True if permitted."""
        with self._lock:
            return self._try_acquire_locked(client_id)

    def acquire(self, client_id: Optional[str] = None, timeout: Optional[float] = None) -> bool:
        """Blocking acquire. Waits until permitted or timeout expires.

        Returns True if acquired, False if timed out.
        timeout=None means wait forever.
        """
        deadline = None if timeout is None else time.monotonic() + timeout
        while True:
            with self._lock:
                if self._try_acquire_locked(client_id):
                    return True
                hint = self._wait_hint_locked(client_id)
            # Sleep outside the lock so others can make progress.
            if deadline is not None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return False
                hint = min(hint, remaining)
            # Avoid busy-spin: sleep at least a tiny amount.
            time.sleep(max(hint, 0.001))
            if deadline is not None and time.monotonic() >= deadline:
                return False

    @property
    @abc.abstractmethod
    def _lock(self) -> threading.Lock:
        """Each subclass must provide its own lock instance."""
        ...


class TokenBucket(RateLimiter):
    """Token bucket: steady-state `rate` tokens/sec, up to `burst` tokens stored."""

    def __init__(self, rate: float, burst: int):
        self._rate = rate
        self._burst = burst
        self.__lock = threading.Lock()
        self._tokens: float = float(burst)
        self._last_refill: float = time.monotonic()

    @property
    def _lock(self) -> threading.Lock:
        return self.__lock

    def _refill(self) -> None:
        """Add tokens based on elapsed time since last refill. Called under lock."""
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self._burst, self._tokens + elapsed * self._rate)
        self._last_refill = now

    def _can_acquire_locked(self, client_id: Optional[str] = None) -> bool:
        self._refill()
        return self._tokens >= 1.0

    def _try_acquire_locked(self, client_id: Optional[str] = None) -> bool:
        self._refill()
        if self._tokens >= 1.0:
            self._tokens -= 1.0
            return True
        return False

    def _wait_hint_locked(self, client_id: Optional[str] = None) -> float:
        if self._tokens >= 1.0:
            return 0.0
        deficit = 1.0 - self._tokens
        return deficit / self._rate


class SlidingWindow(RateLimiter):
    """Sliding window: at most `max_requests` in the last `window_seconds`."""

    def __init__(self, max_requests: int, window_seconds: float):
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self.__lock = threading.Lock()
        self._timestamps: list[float] = []

    @property
    def _lock(self) -> threading.Lock:
        return self.__lock

    def _prune(self, now: float) -> None:
        """Remove timestamps older than the window. Called under lock."""
        cutoff = now - self._window_seconds
        # _timestamps is sorted; find first valid index.
        i = 0
        while i < len(self._timestamps) and self._timestamps[i] <= cutoff:
            i += 1
        if i:
            del self._timestamps[:i]

    def _can_acquire_locked(self, client_id: Optional[str] = None) -> bool:
        now = time.monotonic()
        self._prune(now)
        return len(self._timestamps) < self._max_requests

    def _try_acquire_locked(self, client_id: Optional[str] = None) -> bool:
        now = time.monotonic()
        self._prune(now)
        if len(self._timestamps) < self._max_requests:
            self._timestamps.append(now)
            return True
        return False

    def _wait_hint_locked(self, client_id: Optional[str] = None) -> float:
        if len(self._timestamps) < self._max_requests:
            return 0.0
        # Oldest entry will expire at oldest + window_seconds.
        oldest = self._timestamps[0]
        wait = (oldest + self._window_seconds) - time.monotonic()
        return max(wait, 0.0)


class PerClientLimiter(RateLimiter):
    """Per-client rate limiting. Creates a TokenBucket per client_id.

    Periodically cleans up clients that haven't been seen for cleanup_interval seconds.
    """

    def __init__(self, rate: float, burst: int, cleanup_interval: float = 300.0):
        self._rate = rate
        self._burst = burst
        self._cleanup_interval = cleanup_interval
        self.__lock = threading.Lock()
        self._clients: dict[str, TokenBucket] = {}
        self._last_seen: dict[str, float] = {}
        self._last_cleanup: float = time.monotonic()

    @property
    def _lock(self) -> threading.Lock:
        return self.__lock

    def _get_client_bucket(self, client_id: str) -> TokenBucket:
        """Get or create a TokenBucket for the given client. Called under lock."""
        bucket = self._clients.get(client_id)
        if bucket is None:
            bucket = TokenBucket(rate=self._rate, burst=self._burst)
            self._clients[client_id] = bucket
        self._last_seen[client_id] = time.monotonic()
        return bucket

    def _cleanup_stale_locked(self) -> None:
        """Remove clients not seen for cleanup_interval seconds. Called under lock."""
        now = time.monotonic()
        if now - self._last_cleanup < self._cleanup_interval:
            return
        self._last_cleanup = now
        cutoff = now - self._cleanup_interval
        stale = [cid for cid, ts in self._last_seen.items() if ts < cutoff]
        for cid in stale:
            del self._clients[cid]
            del self._last_seen[cid]

    def _can_acquire_locked(self, client_id: Optional[str] = None) -> bool:
        if client_id is None:
            raise ValueError("PerClientLimiter requires a client_id")
        bucket = self._get_client_bucket(client_id)
        return bucket._can_acquire_locked()

    def _try_acquire_locked(self, client_id: Optional[str] = None) -> bool:
        if client_id is None:
            raise ValueError("PerClientLimiter requires a client_id")
        self._cleanup_stale_locked()
        bucket = self._get_client_bucket(client_id)
        return bucket._try_acquire_locked()

    def _wait_hint_locked(self, client_id: Optional[str] = None) -> float:
        if client_id is None:
            return 0.0
        bucket = self._clients.get(client_id)
        if bucket is None:
            return 0.0  # New client will get a fresh full bucket.
        return bucket._wait_hint_locked()


class _MultiLock:
    """Context manager that acquires multiple locks in id-sorted order."""

    def __init__(self, locks: list[threading.Lock]):
        self._locks = sorted(locks, key=id)

    def __enter__(self) -> None:
        for lock in self._locks:
            lock.acquire()

    def __exit__(self, *args: object) -> None:
        for lock in reversed(self._locks):
            lock.release()


class CompositeRateLimiter(RateLimiter):
    """Combines multiple RateLimiters. Acquire is atomic: all-or-nothing."""

    def __init__(self, limiters: list[RateLimiter]):
        self._limiters = list(limiters)
        self.__lock = threading.Lock()

    @property
    def _lock(self) -> threading.Lock:
        return self.__lock

    def _all_locks(self) -> _MultiLock:
        """Return a context manager that holds all sub-limiter locks."""
        return _MultiLock([lim._lock for lim in self._limiters])

    def _can_acquire_locked(self, client_id: Optional[str] = None) -> bool:
        """Check all sub-limiters. Assumes all sub-limiter locks are held."""
        return all(lim._can_acquire_locked(client_id) for lim in self._limiters)

    def _try_acquire_locked(self, client_id: Optional[str] = None) -> bool:
        """Atomic probe-then-commit. Assumes all sub-limiter locks are held."""
        if not self._can_acquire_locked(client_id):
            return False
        for lim in self._limiters:
            result = lim._try_acquire_locked(client_id)
            assert result, "Acquire must succeed after can_acquire passed"
        return True

    def _wait_hint_locked(self, client_id: Optional[str] = None) -> float:
        """Max wait hint across sub-limiters. Assumes all locks are held."""
        if not self._limiters:
            return 0.0
        return max(lim._wait_hint_locked(client_id) for lim in self._limiters)

    def try_acquire(self, client_id: Optional[str] = None) -> bool:
        """Non-blocking atomic acquire across all sub-limiters."""
        with self._all_locks():
            return self._try_acquire_locked(client_id)

    def acquire(self, client_id: Optional[str] = None, timeout: Optional[float] = None) -> bool:
        """Blocking atomic acquire across all sub-limiters."""
        deadline = None if timeout is None else time.monotonic() + timeout
        while True:
            with self._all_locks():
                if self._try_acquire_locked(client_id):
                    return True
                hint = self._wait_hint_locked(client_id)
            if deadline is not None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return False
                hint = min(hint, remaining)
            time.sleep(max(hint, 0.001))
            if deadline is not None and time.monotonic() >= deadline:
                return False
