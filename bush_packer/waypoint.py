from __future__ import annotations  # Allow forward reference type annotation in py3.8

import json
import re
import shutil

from bush_packer.utils import LocStr, Lang
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple, Union


@dataclass(frozen=True)
class Waypoint:
    leg_index: int
    wpt_index: int
    wpt_id: str
    description: LocStr = None
    image_src: Optional[Path] = None

    @property
    def as_start_wpt_block(self) -> str:
        return f'<ATCWaypointStart id="{self.wpt_id}" />'

    @property
    def as_end_wpt_block(self) -> str:
        return f'<ATCWaypointEnd id="{self.wpt_id}" />'

    @property
    def _image_output_rel_path(self) -> Optional[Path]:
        if self.image_src:
            return Path('images') / f'{self.leg_index + 1}x{self.wpt_index + 1:02d}_{self.wpt_id}{self.image_src.suffix}'

    @property
    def _image_block(self) -> str:
        return f'<ImagePath>{self._image_output_rel_path.as_posix()}</ImagePath>' if self._image_output_rel_path else ''

    @classmethod
    def load(cls, src_dir: Path, *, mission_id: str, leg_index: int) -> Union[UserWaypoint, Waypoint]:
        wpt_index = int(src_dir.name.replace('waypoint.', '')) - 1

        def _parse_metadata_json() -> Tuple[type, str]:
            with (src_dir / '__waypoint__.json').open() as f:
                metadata = json.load(f)
                _wpt_id = metadata['ident']
                if metadata['type'] == 'user':
                    return UserWaypoint, _wpt_id
                elif metadata['type'] == 'ICAO':
                    return Waypoint, _wpt_id
                else:
                    raise ValueError(f"Invalid waypoint type (must be either 'user' or 'ICAO') : {metadata['type']}")

        def _find_image() -> Optional[Path]:
            for ext in {'jpg', 'png'}:
                candidate = (src_dir / f'image.{ext}')
                if candidate.exists():
                    return candidate

        def _description_alternatives() -> Dict[Lang, str]:
            desc_re = re.compile('description\.(?P<lang>\w{2}-\w{2})\.txt', re.IGNORECASE)
            _alternatives = dict()
            for description_file in src_dir.glob('description*.txt'):
                if m := desc_re.match(description_file.name):
                    _alternatives[m.group('lang')] = description_file.read_text()
            return _alternatives

        def _parse_description_files() -> LocStr:
            return LocStr(str_id=f'BUSH_PACK.{mission_id}.WPT{leg_index + 1}x{wpt_index + 1:02d}.DESCRIPTION',
                          alternatives=_description_alternatives())

        wpt_cls, wpt_id = _parse_metadata_json()
        return wpt_cls(leg_index=leg_index,
                       wpt_index=wpt_index,
                       wpt_id=wpt_id,
                       description=_parse_description_files(),
                       image_src=_find_image())

    def build(self, out_dir: Path) -> List[Path]:
        artifacts = list()

        if self._image_output_rel_path:
            image_path = out_dir / self._image_output_rel_path
            image_path.parent.mkdir(exist_ok=True)
            shutil.copy(self.image_src, image_path)
            artifacts.append(image_path)

        return sorted(artifacts)

    def dump_xml(self, prev_waypoint: Waypoint) -> str:
        return f"""<SubLeg>
                       <Descr>{self.description or ''}</Descr>
                       {self._image_block}
                       {prev_waypoint.as_start_wpt_block}
                       {self.as_end_wpt_block}
                   </SubLeg>"""


@dataclass(frozen=True)
class UserWaypoint(Waypoint):
    @property
    def _wpt_region_str(self) -> str:
        return f"!{chr(ord('A') + self.leg_index)}"

    @property
    def as_start_wpt_block(self) -> str:
        return f"""<ATCWaypointStart id="{self.wpt_id}">
                       <idRegion>{self._wpt_region_str}</idRegion>
                   </ATCWaypointStart>"""

    @property
    def as_end_wpt_block(self) -> str:
        return f"""<ATCWaypointEnd id="{self.wpt_id}">
                       <idRegion>{self._wpt_region_str}</idRegion>
                   </ATCWaypointEnd>"""
