from __future__ import annotations  # Allow forward reference type annotation in py3.8

import bush_trip_generator.subleg
import uuid

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bush_trip_generator.subleg import SubLeg
    from trio import Path
    from typing import List, Optional


class Leg:
    def __init__(self, leg_index: int = None, description: str = None, sublegs: List[SubLeg] = None):
        self.leg_index = leg_index
        self.description = description
        self.sublegs = sublegs
        self.end_trigger_uuid = f"{{{str(uuid.uuid1()).upper()}}}"

    @property
    def index(self) -> int:
        return 0

    @property
    def last_subleg(self) -> Optional[SubLeg]:
        if self.sublegs:
            return self.sublegs[-1]

    def dump(self, prev: Leg) -> str:
        return f"""<Leg>
                      <Descr>{self.description}</Descr>
                      {self.dump_leg_completion_trigger_ref()}
                      <SubLegs>
                      {self._dump_sublegs(initial_subleg=prev.last_subleg)}
                      </SubLegs>
                   </Leg>"""

    def _dump_sublegs(self, initial_subleg: SubLeg) -> str:
        if not self.sublegs:
            return ''

        return '\n'.join([subleg.dump(prev=prev)
                          for (prev, subleg) in zip([initial_subleg] + self.sublegs[:-1],
                                                    self.sublegs)])

    def dump_leg_completion_trigger_ref(self) -> str:
        return f'<AirportLandingTriggerEnd UniqueRefId="{self.end_trigger_uuid}" />'

    def dump_leg_completion_trigger(self) -> str:
        return f"""<SimMission.AirportCalculator InstanceId="{self.end_trigger_uuid}">
      <AirportIdent>{self.last_subleg.wpt_id}</AirportIdent>
      <ComputeAirportPolygon>true</ComputeAirportPolygon>
      <Activated>false</Activated>
      <CalculatorParameterList>
        <FormulaParameter NameInFormula="Threshold">
          <StartValue>20.000</StartValue>
        </FormulaParameter>
        <FormulaParameter NameInFormula="FarThreshold">
          <StartValue>100.000</StartValue>
        </FormulaParameter>
        <FormulaParameter NameInFormula="OnGround">
          <CalculatorFormula>
            (A:SIM ON GROUND, Boolean) 0 &gt;
          </CalculatorFormula>
        </FormulaParameter>
        <FormulaParameter NameInFormula="OnRunway">
          <CalculatorFormula>
            [SignedDistanceToClosestRunway] [Threshold] &lt;
          </CalculatorFormula>
        </FormulaParameter>
        <FormulaParameter NameInFormula="TimerLanded">
          <CalculatorFormula>
            [OnRunway] [SignedDistanceToAirportArea] [Threshold] &lt; or [OnGround]  and (A:GROUND VELOCITY, Knots) 2 &lt; and
            if{{
            [TimerLanded] [dtime] +
            }}
            els{{ 0 }}
          </CalculatorFormula>
        </FormulaParameter>
        <FormulaParameter NameInFormula="UnknownTouchDown">
          <CalculatorFormula>
            [SignedDistanceToClosestRunway] [FarThreshold] &gt; [OnGround] and [UnknownTouchDown] or
          </CalculatorFormula>
        </FormulaParameter>
        <FormulaParameter NameInFormula="OutsideTouchDown">
          <CalculatorFormula>
            [SignedDistanceToClosestRunway] [FarThreshold] &lt; [SignedDistanceToClosestRunway] [Threshold] &gt; [OnGround] and and [OutsideTouchDown] or
          </CalculatorFormula>
        </FormulaParameter>
      </CalculatorParameterList>
      <CalculatorActions>
        <CalculatorAction>
          <CalculatorFormula>
            [OutsideTouchDown] [UnknownTouchDown] not and
          </CalculatorFormula>
          <Actions>
            <WorldBase.ObjectReference id="ACT_NotifOutOfRunway" InstanceId="{{952743E5-F838-4F51-A1A0-07E8DCD44019}}" />
          </Actions>
        </CalculatorAction>
        <CalculatorAction>
          <DeactivateAfterExecution>true</DeactivateAfterExecution>
          <CalculatorFormula>
            [TimerLanded] 2 &gt;
          </CalculatorFormula>
          <Actions>
            <WorldBase.ObjectReference id="FlowEvent_LandingRest" InstanceId="{{F4FEBADA-8867-43E7-832D-947FAFCD8187}}" />
          </Actions>
        </CalculatorAction>
      </CalculatorActions>
    </SimMission.AirportCalculator>
"""


async def load_leg(source_dir: Path) -> Leg:
    leg_index = int(source_dir.name.replace('leg_', '')) - 1

    return Leg(leg_index=leg_index,
               description=await (source_dir / f"{source_dir.name}.txt").read_text(),
               sublegs=[await bush_trip_generator.subleg.load_subleg(leg_index, subleg_source_file)
                        for subleg_source_file in await source_dir.glob('subleg.*')])
