from __future__ import annotations  # Allow forward reference type annotation in py3.8

import re

from trio import Path
from typing import NewType, Union, TYPE_CHECKING

if TYPE_CHECKING:
    pass


class ICAOSubLeg:
    def __init__(self, wpt_id: str, *, description: str = None, image: Path = None):
        self.wpt_id = wpt_id
        self.description = description
        self.image = image

    def as_start_wpt_block(self) -> str:
        return f'<ATCWaypointStart id="{self.wpt_id}" />'

    def as_end_wpt_block(self) -> str:
        return f'<ATCWaypointEnd id="{self.wpt_id}" />'

    def _image_block(self) -> str:
        if not self.image:
            return ''
        return f'<ImagePath>{self.image}</ImagePath>'

    def dump(self, prev: SubLeg) -> str:
        return f"""<SubLeg>
                       <Descr>{self.description}</Descr>
                       {self._image_block()}
                       {prev.as_start_wpt_block()}
                       {self.as_end_wpt_block()}
                   </SubLeg>"""


class UserWptSubLeg(ICAOSubLeg):
    def __init__(self, leg_index: int, wpt_id: str, *, description: str = None, image: Path = None):
        super().__init__(wpt_id=wpt_id,
                         description=description,
                         image=image)
        self.leg_index = leg_index

    @property
    def _wpt_region_str(self) -> str:
        return f"!{chr(ord('A') + self.leg_index)}"

    def as_start_wpt_block(self) -> str:
        return f"""<ATCWaypointStart id="{self.wpt_id}">
                       <idRegion>{self._wpt_region_str}</idRegion>
                   </ATCWaypointStart>"""

    def as_end_wpt_block(self) -> str:
        return f"""<ATCWaypointEnd id="{self.wpt_id}">
                       <idRegion>{self._wpt_region_str}</idRegion>
                   </ATCWaypointEnd>"""


SubLeg = NewType('SubLeg', Union[ICAOSubLeg, UserWptSubLeg])


async def load_subleg(parent_leg_index: int, source_file: Path) -> SubLeg:
    re_header = re.compile(r'^(?P<key>waypoint|user_waypoint|image):\s*(?P<value>.*)', re.IGNORECASE)
    is_in_header = True
    header = dict()
    description_lines = list()

    async with await source_file.open() as f:
        async for line in f:
            stripped_line = line.strip()
            if not stripped_line:
                is_in_header = False
            elif is_in_header:
                if m := re_header.match(stripped_line):
                    key = m.group('key')
                    value = m.group('value')
                    if key in header:
                        raise ValueError(f'Duplicate key in {source_file}: {key}')
                    header[key] = value
                else:
                    raise ValueError(f'Malformed line in {source_file}: {line}')
            else:
                description_lines.append(stripped_line)

    if 'waypoint' in header:
        return ICAOSubLeg(wpt_id=header['waypoint'],
                          description='\n'.join(description_lines),
                          image=header.get('image'))

    elif 'user_waypoint' in header:
        return UserWptSubLeg(leg_index=parent_leg_index,
                             wpt_id=header['user_waypoint'],
                             description='\n'.join(description_lines),
                             image=header.get('image'))

    else:
        raise ValueError(f'Missing header in {source_file}: requires either waypoint or user_waypoint')
