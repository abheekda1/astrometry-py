import functools
import os
import hashlib
import shelve
import atexit
import asyncio
import logging

def hash_cache(fn):
    """
    Decorator that caches coroutine results based on the SHA-256 hash
    of the file at the second argument, and persists that cache to disk.

    Logs a DEBUG message whenever a cache hit occurs.
    """
    # Prepare on-disk shelf
    cache_dir = os.path.expanduser("~/.cache/hash_cache")
    os.makedirs(cache_dir, exist_ok=True)
    db_path = os.path.join(cache_dir, f"{fn.__name__}.db")
    shelf = shelve.open(db_path, writeback=False)
    atexit.register(shelf.close)

    logger = logging.getLogger(fn.__module__)

    if asyncio.iscoroutinefunction(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            if len(args) < 2:
                raise TypeError("hash_cache needs at least (self, file_path)")
            file_path = os.fspath(args[1])

            # Compute SHA-256 hash of the file
            hasher = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)
            key = hasher.hexdigest()

            # Cache lookup
            if key in shelf:
                logger.debug("hash_cache hit for %s", file_path)
                return shelf[key]

            # Miss → call original and store
            result = await fn(*args, **kwargs)
            shelf[key] = result
            shelf.sync()
            return result

        return wrapper

    else:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if len(args) < 1:
                raise TypeError("hash_cache(sync) needs (file_path, ...)")
            file_path = os.fspath(args[0])

            hasher = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)
            key = hasher.hexdigest()

            if key in shelf:
                logger.debug("hash_cache hit for %s", file_path)
                return shelf[key]

            result = fn(*args, **kwargs)
            shelf[key] = result
            shelf.sync()
            return result

        return wrapper
