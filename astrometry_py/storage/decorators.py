# import functools
# import os
# import hashlib
# import shelve
# import asyncio
# import logging
# import threading

# def hash_cache(fn=None, *, path_index: int = 1):
#     """_summary_

#     :param fn: _description_, defaults to None
#     :type fn: _type_, optional
#     :param path_index: _description_, defaults to 1
#     :type path_index: int, optional
#     :raises TypeError: _description_
#     :raises TypeError: _description_
#     :return: _description_
#     :rtype: _type_
#     """
#     # Allow decorator without args
#     if fn is None:
#         return lambda f: hash_cache(f, path_index=path_index)

#     cache_dir = os.path.expanduser("~/.cache/hash_cache")
#     os.makedirs(cache_dir, exist_ok=True)
#     db_path = os.path.join(cache_dir, f"{fn.__name__}.db")
#     lock = threading.RLock()
#     logger = logging.getLogger(fn.__module__)

#     def compute_key(file_path: str) -> str:
#         hasher = hashlib.sha256()
#         with open(file_path, "rb") as f:
#             for chunk in iter(lambda: f.read(8192), b""):
#                 hasher.update(chunk)
#         return hasher.hexdigest()

#     # Async wrapper
#     if asyncio.iscoroutinefunction(fn):
#         @functools.wraps(fn)
#         async def async_wrapper(*args, **kwargs):
#             try:
#                 file_path = os.fspath(args[path_index])
#             except IndexError:
#                 raise TypeError(f"hash_cache needs argument at index {path_index}")
#             key = compute_key(file_path)

#             # Attempt cache read
#             with lock:
#                 with shelve.open(db_path, writeback=False) as shelf:
#                     if key in shelf:
#                         logger.debug("hash_cache hit for %s", file_path)
#                         return shelf[key]

#             # Cache miss: call function
#             result = await fn(*args, **kwargs)

#             # Persist result
#             with lock:
#                 with shelve.open(db_path, writeback=False) as shelf:
#                     shelf[key] = result

#             return result

#         return async_wrapper

#     # Sync wrapper
#     @functools.wraps(fn)
#     def sync_wrapper(*args, **kwargs):
#         try:
#             file_path = os.fspath(args[path_index])
#         except IndexError:
#             raise TypeError(f"hash_cache needs argument at index {path_index}")
#         key = compute_key(file_path)

#         with lock:
#             with shelve.open(db_path, writeback=False) as shelf:
#                 if key in shelf:
#                     logger.debug("hash_cache hit for %s", file_path)
#                     return shelf[key]

#         result = fn(*args, **kwargs)

#         with lock:
#             with shelve.open(db_path, writeback=False) as shelf:
#                 shelf[key] = result

#         return result

#     return sync_wrapper