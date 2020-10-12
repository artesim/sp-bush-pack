import trio

from configargparse import Namespace
from trio import Path


class FsPackageTool:
    def __init__(self, cfg: Namespace):
        self.pkg_tool = cfg.msfs_sdk_root_dir / 'Tools' / 'bin' / 'fspackagetool.exe'

    async def build(self, project: Path, *, incremental: bool = True, output: Path = None, temp: Path = None):
        await trio.run_process(command=list(filter(None,
                                                   [self.pkg_tool,
                                                    project,
                                                    '-outputdir' if output else None,
                                                    f'{output}' if output else None,
                                                    '-tempdir' if temp else None,
                                                    f'{temp}' if temp else None,
                                                    '-rebuild' if not incremental else None])))
