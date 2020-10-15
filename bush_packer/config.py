import argparse

from pathlib import Path


def _parse_sys_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('src_dir')
    parser.add_argument('dist_dir')

    cfg = parser.parse_args()
    cfg.src_dir = Path(cfg.src_dir)
    cfg.dist_dir = Path(cfg.dist_dir)
    return cfg


CFG = _parse_sys_args()  # Parsed only once, when the module is first imported
