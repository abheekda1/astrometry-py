# import os
# import errno
# import hashlib
# from pathlib import Path

# try:
#     from appdirs import user_cache_dir
# except ImportError:
#     user_cache_dir = None

# # todo: make file cache {sub_file_hash: subid}

# class CacheManager:
#     """Cache manager
#     """
#     def __init__(self,
#                  appname: str = "astrometry_py",
#                  appauthor: str = "abheekda1",
#                  fallback: str = ".cache/astrometry_py"):
#         """Initialized the cache manager

#         :param appname: name of the app, defaults to "astrometry_py"
#         :type appname: str, optional
#         :param appauthor: author of the app, defaults to "abheekda1"
#         :type appauthor: str, optional
#         :param fallback: fallback cache location, defaults to ".cache/astrometry_py"
#         :type fallback: str, optional
#         """
#         if user_cache_dir:
#             base = Path(user_cache_dir(appname, appauthor))
#         else:
#             base = Path(fallback).expanduser()
#         self.base_dir = base
#         self.base_dir.mkdir(parents=True, exist_ok=True)

#     def _key_to_path(self, key: str, subdir: str, ext: str) -> Path:
#         """Convert a key, subdir and extension into a full filepath.

#         :param key: Key
#         :type key: str
#         :param subdir: Subdirectory
#         :type subdir: str
#         :param ext: Extension
#         :type ext: str
#         :return: The full filepath
#         :rtype: Path
#         """
#         h = hashlib.sha256(key.encode("utf-8")).hexdigest()
#         prefix = "".join(ch for ch in key[:20] if ch.isalnum() or ch in "._-")
#         fname = f"{prefix + '-' if prefix else ''}{h}.{ext}"
#         d = self.base_dir / subdir
#         d.mkdir(parents=True, exist_ok=True)
#         return d / fname

#     def get(self, key: str, subdir: str, ext: str) -> bytes | None:
#         """Retrieve raw bytes from cache. Returns None if missing.

#         :param key: _description_
#         :type key: str
#         :param subdir: _description_
#         :type subdir: str
#         :param ext: _description_
#         :type ext: str
#         :return: _description_
#         :rtype: bytes | None
#         """
        
#         path = self._key_to_path(key, subdir, ext)
#         if path.is_file():
#             try:
#                 return path.read_bytes()
#             except OSError:
#                 return None
#         return None

#     def set(self, key: str, subdir: str, ext: str, data: bytes) -> None:
#         """Write raw bytes to cache, overwriting if needed

#         :param key: _description_
#         :type key: str
#         :param subdir: _description_
#         :type subdir: str
#         :param ext: _description_
#         :type ext: str
#         :param data: _description_
#         :type data: bytes
#         """
#         path = self._key_to_path(key, subdir, ext)
#         tmp = path.with_suffix(path.suffix + ".tmp")
#         tmp.write_bytes(data)
#         os.replace(tmp, path)

#     def clear(self) -> None:
#         """Remove all cached files
#         """
#         for child in self.base_dir.iterdir():
#             if child.is_dir():
#                 for f in child.iterdir():
#                     try:
#                         f.unlink()
#                     except OSError:
#                         pass
#             else:
#                 try:
#                     child.unlink()
#                 except OSError:
#                     pass