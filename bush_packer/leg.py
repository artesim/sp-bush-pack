from __future__ import annotations  # Allow forward reference type annotation in py3.8

import json

from bush_packer.utils import LocStr, new_uuid_str
from bush_packer.waypoint import Waypoint
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Optional


@dataclass(frozen=True)
class Leg:
    leg_index: int
    description: LocStr
    waypoints: List[Waypoint]
    end_trigger_uuid: str = field(default=new_uuid_str(), init=False)

    @property
    def last_waypoint(self) -> Optional[Waypoint]:
        if self.waypoints:
            return self.waypoints[-1]

    @classmethod
    def load(cls, src_dir: Path, *, mission_id: str) -> Leg:
        leg_index = int(src_dir.name.replace('leg.', '')) - 1

        def _parse_metadata_json():
            with (src_dir / '__leg__.json').open() as f:
                metadata = json.load(f)
                return {'description': LocStr(str_id=f'BUSH_PACK.{mission_id}.LEG{leg_index + 1}.DESCRIPTION',
                                              alternatives=metadata['description'])}

        return cls(leg_index=leg_index,
                   waypoints=[Waypoint.load(waypoint_dir,
                                            mission_id=mission_id,
                                            leg_index=leg_index)
                              for waypoint_dir in src_dir.glob('waypoint.*')],
                   **_parse_metadata_json())

    def build(self, out_dir: Path) -> List[Path]:
        # Build the children and return their artifacts
        return sorted([artifact
                       for waypoint in self.waypoints
                       for artifact in waypoint.build(out_dir=out_dir)])

    def dump(self, prev_leg: Leg) -> str:
        return f"""<Leg>
                      <Descr>{self.description}</Descr>
                      {self.dump_leg_completion_trigger_ref()}
                      <SubLegs>
                      {self._dump_waypoints(initial_waypoint=prev_leg.last_waypoint)}
                      </SubLegs>
                   </Leg>"""

    def _dump_waypoints(self, initial_waypoint: Waypoint) -> str:
        if not self.waypoints:
            return ''

        return '\n'.join([waypoint.dump(prev_waypoint=prev_waypoint)
                          for (prev_waypoint, waypoint) in zip([initial_waypoint] + self.waypoints[:-1],
                                                               self.waypoints)])

    def dump_leg_completion_trigger_ref(self) -> str:
        return f'<AirportLandingTriggerEnd UniqueRefId="{self.end_trigger_uuid}" />'

    def dump_leg_completion_trigger(self,
                                    event_trigger_out_of_rwy_uuid: str,
                                    flow_event_landing_rest_uuid: str) -> str:
        return Path(__file__).with_name('leg_end_trigger.xml_template').read_text().format(
            end_trigger_uuid=self.end_trigger_uuid,
            last_wpt_id=self.last_waypoint.wpt_id,
            event_trigger_out_of_rwy_uuid=event_trigger_out_of_rwy_uuid,
            flow_event_landing_rest_uuid=flow_event_landing_rest_uuid
        )


@dataclass(frozen=True)
class InitialLeg(Leg):
    def __init__(self, initial_fix: str):
        super().__init__(leg_index=-1,
                         description=LocStr(str_id='', alternatives={}),
                         waypoints=[Waypoint(leg_index=-1,
                                             wpt_index=-1,
                                             wpt_id=initial_fix)])
