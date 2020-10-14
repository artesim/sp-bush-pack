import configargparse

from trio import Path


def parse_sys_args() -> configargparse.Namespace:
    parser = configargparse.Parser()
    parser.add_argument('source_dir')
    parser.add_argument('--msfs-sdk-root-dir', default=Path('C:/') / 'MSFS SDK')
    parser.add_argument('--out-dir', required=False)
    parser.add_argument('--tmp-dir', required=False)
    settings = parser.parse_args()
    settings.source_xml_project = Path(settings.source_xml_project)
    settings.msfs_sdk_root_dir = Path(settings.msfs_sdk_root_dir)
    settings.out_dir = Path(settings.out_dir) if settings.out_dir else None
    settings.tmp_dir = Path(settings.tmp_dir) if settings.tmp_dir else None
    return settings


SETTINGS = parse_sys_args()
