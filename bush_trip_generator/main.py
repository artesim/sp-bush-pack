import configargparse
import trio

from bush_trip_generator.fspackagetool import FsPackageTool
from configargparse import Namespace
from trio import Path


async def main():
    cfg = parse_args()
    packager = FsPackageTool(cfg)
    await packager.build(cfg.source_xml_project,
                         output=cfg.out_dir,
                         temp=cfg.tmp_dir)


def parse_args() -> Namespace:
    parser = configargparse.Parser()
    parser.add_argument('source_xml_project')
    parser.add_argument('--msfs-sdk-root-dir', default=Path('C:/') / 'MSFS SDK')
    parser.add_argument('--out-dir', required=False)
    parser.add_argument('--tmp-dir', required=False)
    cfg = parser.parse_args()
    cfg.source_xml_project = Path(cfg.source_xml_project)
    cfg.msfs_sdk_root_dir = Path(cfg.msfs_sdk_root_dir)
    cfg.out_dir = Path(cfg.out_dir) if cfg.out_dir else None
    cfg.tmp_dir = Path(cfg.tmp_dir) if cfg.tmp_dir else None
    return cfg


if __name__ == '__main__':
    trio.run(main)
