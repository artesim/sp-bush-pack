from __future__ import annotations  # Allow forward reference type annotation in py3.8

import json
import re
import shutil
import typing

from bush_packer.leg import Leg, InitialLeg
from bush_packer.utils import LocStr, new_uuid_str
from dataclasses import dataclass, field, InitVar
from pathlib import Path

if typing.TYPE_CHECKING:
    from bush_packer.utils import Lang
    from typing import Dict, List


@dataclass(frozen=True)
class Mission:
    mission_id: str
    uuid: str = field(default=new_uuid_str(), init=False)
    version: str
    title: LocStr
    description: LocStr
    location: LocStr
    main_briefing: LocStr
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
                        'location': LocStr(str_id=f'BUSH_PACK.{mission_id}.LOCATION',
                                           alternatives=metadata['location']),
                        'initial_fix': metadata['initial_fix']}

        def _briefing_alternatives() -> Dict[Lang, str]:
            desc_re = re.compile('briefing\.(?P<lang>\w{2}-\w{2})\.txt', re.IGNORECASE)
            _alternatives = dict()
            for briefing_file in src_dir.glob('briefing*.txt'):
                if m := desc_re.match(briefing_file.name):
                    _alternatives[m.group('lang')] = briefing_file.read_text()
            return _alternatives

        def _parse_briefing_files() -> LocStr:
            return LocStr(str_id=f'BUSH_PACK.{mission_id}.BRIEFING',
                          alternatives=_briefing_alternatives())

        return cls(mission_id=mission_id,
                   legs=[Leg.load(leg_dir, mission_id=mission_id)
                         for leg_dir in src_dir.glob('leg.*')],
                   src_dir=src_dir,
                   main_briefing=_parse_briefing_files(),
                   **_parse_metadata_json())

    def build(self, out_dir: Path) -> List[Path]:
        root = out_dir / self.mission_id
        mission_flt = root / f"{self.mission_id}.flt"
        mission_xml = root / f"{self.mission_id}.xml"
        root.mkdir(parents=True, exist_ok=True)
        (root / 'images').mkdir(parents=True, exist_ok=True)

        # Build the children and collect their artifacts
        artifacts = sorted([artifact
                            for leg in self.legs
                            for artifact in leg.build(out_dir=root)])

        # Copy the mission pln, wpr and images
        shutil.copy(self.src_dir / 'flight_plan.pln', root / f'{self.mission_id}.pln')
        shutil.copy(self.src_dir / 'weather.wpr', root)
        shutil.copytree(self.src_dir / 'images', root / 'images', dirs_exist_ok=True)

        # Generate the mission FLT file
        mission_flt.write_text(self.dump_flt())

        # Generate the MissionFile xml
        mission_xml.write_text(self.dump_xml())

        # Return the full list of artifacts
        # (not used for now, just being consistent with the children, here)
        return sorted([mission_flt,
                       mission_xml,
                       root / f'{self.mission_id}.pln',
                       root / f'weather.wpr',
                       root / 'images' / 'Activity_Widget.jpg',
                       root / 'images' / 'Loading_Screen.jpg'] +
                      artifacts)

    def dump_xml(self) -> str:
        event_trigger_out_of_rwy_uuid = new_uuid_str()
        flow_event_landing_rest_uuid = new_uuid_str()

        return Path(__file__).with_suffix('.xml_template').read_text().format(
            title=self.title,
            mission_id=self.mission_id,
            description=self.description,
            legs=self._dump_xml_legs(),

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
            leg_completion_triggers=self._dump_xml_leg_completion_triggers(
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

    def _dump_xml_legs(self) -> str:
        return '\n'.join([leg.dump_xml(prev_leg=prev)
                          for (prev, leg) in zip([self.initial_leg] + self.legs[:-1],
                                                 self.legs)])

    def _dump_xml_leg_completion_triggers(self,
                                          event_trigger_out_of_rwy_uuid: str,
                                          flow_event_landing_rest_uuid: str) -> str:
        return '\n'.join([leg.dump_xml_leg_completion_trigger(
            event_trigger_out_of_rwy_uuid=event_trigger_out_of_rwy_uuid,
            flow_event_landing_rest_uuid=flow_event_landing_rest_uuid
        ) for leg in self.legs])

    def dump_flt(self) -> str:
        return (self.src_dir / 'mission.flt_template').read_text().format(
            location=self.location,
            title=self.title,
            description=self.description,
            main_briefing=self.main_briefing,
            leg_briefing_images='\n'.join([leg.dump_flt_briefing_images() for leg in self.legs]),
            mission_id=self.mission_id
        )
