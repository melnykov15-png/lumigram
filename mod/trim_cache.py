#!/usr/bin/env python3
"""Shrinks the Bazel disk cache so it fits into the free GitHub Actions cache (10 GB per repo).

Usage: python3 mod/trim_cache.py <cache-dir> <max-gigabytes>
Removes the least recently used files first.
"""
import os
import sys


def main():
    cache_dir, max_gb = sys.argv[1], float(sys.argv[2])
    if not os.path.isdir(cache_dir):
        print("trim_cache: no cache at " + cache_dir)
        return
    files = []
    total = 0
    for dirpath, _, names in os.walk(cache_dir):
        for name in names:
            path = os.path.join(dirpath, name)
            try:
                st = os.stat(path)
            except OSError:
                continue
            files.append((max(st.st_atime, st.st_mtime), st.st_size, path))
            total += st.st_size
    limit = int(max_gb * 1024 ** 3)
    print("trim_cache: %.2f GB in %d files, limit %.2f GB" % (total / 1024 ** 3, len(files), max_gb))
    files.sort()
    removed = 0
    for _, size, path in files:
        if total <= limit:
            break
        try:
            os.remove(path)
        except OSError:
            continue
        total -= size
        removed += 1
    print("trim_cache: removed %d files, now %.2f GB" % (removed, total / 1024 ** 3))


if __name__ == "__main__":
    main()
