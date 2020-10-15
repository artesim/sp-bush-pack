from __future__ import annotations  # Allow forward reference type annotation in py3.8

import json
import shutil

from bush_packer.mission import Mission
from bush_packer.scenery import Scenery
from bush_packer.utils import LocStr
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    from typing import List


@dataclass(frozen=True)
class BushPack:
    bush_pack_id: str
    version: str
    title: LocStr
    missions: List[Mission]
    sceneries: List[Scenery]

    @classmethod
    def load(cls, src_dir: Path) -> BushPack:
        def _parse_metadata_json():
            with (src_dir / '__bush_pack__.json').open() as f:
                metadata = json.load(f)
                return {'version': metadata['version'],
                        'title': LocStr(str_id='BUSH_PACK.TITLE',
                                        alternatives=metadata['title'])}

        return cls(bush_pack_id=src_dir.name,
                   missions=[Mission.load(mission_dir)
                             for mission_dir in (src_dir / 'Missions').glob('*')],
                   sceneries=[Scenery.load(scenery_dir)
                              for scenery_dir in (src_dir / 'Sceneries').glob('*')],
                   **_parse_metadata_json())

    def build(self, out_dir: Path) -> List[Path]:
        # Remove any existing out_dir tree completely, and recreate it
        root = out_dir / self.bush_pack_id
        if root.exists():
            shutil.rmtree(root)
        root.mkdir()

        # Build the children and collect their artifacts
        artifacts = sorted([artifact
                            for mission in self.missions
                            for artifact in mission.build(out_dir=root / 'Missions')] +
                           [artifact
                            for scenery in self.sceneries
                            for artifact in scenery.build(out_dir=root / 'Sceneries')] +
                           self._build_loc_packs(root=root))

        # Generates out_dir/layout.json from the list of artifacts
        with (root / 'layout.json').open('w') as layout:
            json.dump({"content": [self._layout_artifact_infos(root, artifact)
                                   for artifact in artifacts]},
                      layout,
                      indent=True)

        # Return the full list of artifacts
        # (not used for now, just being consistent with the children, here)
        return sorted([root / 'layout.json'] + artifacts)

    @staticmethod
    def _build_loc_packs(root: Path) -> List[Path]:
        loc_pack_data = LocStr.dump_instances()
        for lang, strings_dict in loc_pack_data.items():
            with (root / f"{lang}.locPak").open('w') as f:
                json.dump({
                    'LocalisationPackage': {
                        'Language': str(lang),
                        'Strings': {str_id: strings_dict[str_id]
                                    for str_id in sorted(strings_dict.keys())}
                    }
                }, f, indent=True)

        return [root / f"{lang}.locPak" for lang in sorted(loc_pack_data.keys(), key=str)]

    @staticmethod
    def _layout_artifact_infos(root: Path, artifact: Path) -> dict:
        # TODO: test that
        # From https://github.com/flybywiresim/a32nx/blob/master/A32NX/build.py
        # file_size = os.path.getsize(file_path)
        # file_date = 116444736000000000 + int(os.path.getmtime(file_path) * 10000000.0)
        if not artifact.is_file():
            raise ValueError(f"{artifact} should have been ignored, we only care about files in layout.json")
        return {"path": artifact.relative_to(root).as_posix(),
                "size": artifact.lstat().st_size,
                "date": 116444736000000000 + artifact.lstat().st_mtime_ns}
