import os
import shutil


def clear_cache():
    cache_dir = "cache"
    if os.path.exists(cache_dir) and os.path.isdir(cache_dir):
        shutil.rmtree(cache_dir)


if __name__ == "__main__":
    clear_cache()
