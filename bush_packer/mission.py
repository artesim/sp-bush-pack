from __future__ import annotations  # Allow forward reference type annotation in py3.8

import json
import shutil
import typing

from bush_packer.leg import Leg, InitialLeg
from bush_packer.utils import LocStr, new_uuid_str
from dataclasses import dataclass, field, InitVar
from pathlib import Path

if typing.TYPE_CHECKING:
    from typing import List


@dataclass(frozen=True)
class Mission:
    mission_id: str
    uuid: str = field(default=new_uuid_str(), init=False)
    version: str
    title: LocStr
    description: LocStr
    initial_fix: InitVar[str]
    initial_leg: Leg = field(init=False)  # init in __post_init, using initial_fix
    legs: List[Leg]
    src_dir: Path

    def __post_init__(self, initial_fix: str):
        object.__setattr__(self, 'initial_leg', InitialLeg(initial_fix))

    @classmethod
    def load(cls, src_dir: Path) -> Mission:
        mission_id = src_dir.name

        def _parse_metadata_json():
            with (src_dir / '__mission__.json').open() as f:
                metadata = json.load(f)
                return {'version': metadata['version'],
                        'title': LocStr(str_id=f'BUSH_PACK.{mission_id}.TITLE',
                                        alternatives=metadata['title']),
                        'description': LocStr(str_id=f'BUSH_PACK.{mission_id}.DESCRIPTION',
                                              alternatives=metadata['description']),
                        'initial_fix': metadata['initial_fix']}

        return cls(mission_id=mission_id,
                   legs=[Leg.load(leg_dir, mission_id=mission_id)
                         for leg_dir in src_dir.glob('leg.*')],
                   src_dir=src_dir,
                   **_parse_metadata_json())

    def build(self, out_dir: Path) -> List[Path]:
        root = out_dir / self.mission_id
        mission_file_xml = root / f"{self.mission_id}.xml"
        root.mkdir(parents=True, exist_ok=True)
        (root / 'images').mkdir(parents=True, exist_ok=True)

        # Build the children and collect their artifacts
        artifacts = sorted([artifact
                            for leg in self.legs
                            for artifact in leg.build(out_dir=root)])

        # Copy the mission flt, pln, wpr and images
        shutil.copy(self.src_dir / 'mission.flt', root / f'{self.mission_id}.flt')
        shutil.copy(self.src_dir / 'flight_plan.pln', root / f'{self.mission_id}.pln')
        shutil.copy(self.src_dir / 'weather.wpr', root)
        shutil.copytree(self.src_dir / 'images', root / 'images', dirs_exist_ok=True)

        # Generate the MissionFile xml
        mission_file_xml.write_text(self.dump())

        # Return the full list of artifacts
        # (not used for now, just being consistent with the children, here)
        return sorted([mission_file_xml,
                       root / f'{self.mission_id}.flt',
                       root / f'{self.mission_id}.pln',
                       root / f'weather.wpr',
                       root / 'images' / 'Activity_Widget.jpg',
                       root / 'images' / 'Loading_Screen.jpg'] +
                      artifacts)

    def dump(self) -> str:
        event_trigger_out_of_rwy_uuid = new_uuid_str()
        flow_event_landing_rest_uuid = new_uuid_str()

        return Path(__file__).with_suffix('.xml_template').read_text().format(
            title=self.title,
            mission_id=self.mission_id,
            description=self.description,
            legs=self._dump_legs(),

            calc_out_of_fuel_uuid=new_uuid_str(),
            event_trigger_out_of_rwy_uuid=event_trigger_out_of_rwy_uuid,
            flight_uuid=new_uuid_str(),
            flow_event_disable_fuel_uuid=new_uuid_str(),
            flow_event_landing_rest_uuid=new_uuid_str(),
            flow_state_intro_uuid=new_uuid_str(),
            flow_state_bush_trip_uuid=new_uuid_str(),
            flow_state_landing_rest_uuid=new_uuid_str(),
            goal_uuid=new_uuid_str(),
            goal_resolution_success_uuid=new_uuid_str(),
            goal_resolution_failure_uuid=new_uuid_str(),
            leg_completion_triggers=self._dump_leg_completion_triggers(
                event_trigger_out_of_rwy_uuid=event_trigger_out_of_rwy_uuid,
                flow_event_landing_rest_uuid=flow_event_landing_rest_uuid
            ),
            mission_uuid=self.uuid,
            rtc_ground_ac_outro_uuid=new_uuid_str(),
            teleport_wise_rtc_uuid=new_uuid_str(),
            teleport_wise_rtc_non_rtc_uuid=new_uuid_str(),
            teleport_ground_arpt_ac_intro_uuid=new_uuid_str(),
            timer_start_uuid=new_uuid_str(),
            wise_afs_set_uuid=new_uuid_str()
        )

    def _dump_legs(self) -> str:
        return '\n'.join([leg.dump(prev_leg=prev)
                          for (prev, leg) in zip([self.initial_leg] + self.legs[:-1],
                                                 self.legs)])

    def _dump_leg_completion_triggers(self,
                                      event_trigger_out_of_rwy_uuid: str,
                                      flow_event_landing_rest_uuid: str) -> str:
        return '\n'.join([leg.dump_leg_completion_trigger(
            event_trigger_out_of_rwy_uuid=event_trigger_out_of_rwy_uuid,
            flow_event_landing_rest_uuid=flow_event_landing_rest_uuid
        ) for leg in self.legs])
