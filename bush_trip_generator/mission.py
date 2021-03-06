from __future__ import annotations  # Allow forward reference type annotation in py3.8

import bush_trip_generator.leg
import uuid
import json
import typing

from bush_trip_generator.leg import Leg
from bush_trip_generator.subleg import ICAOSubLeg
from trio import Path

if typing.TYPE_CHECKING:
    from typing import List


class Mission:
    def __init__(self, mission_id: str, title: str, description: str, initial_fix: str, legs: List[Leg]):
        self.mission_id = mission_id
        self.uuid = f"{{{str(uuid.uuid1()).upper()}}}"
        self.title = title
        self.description = description
        self.initial_leg = Leg(sublegs=[ICAOSubLeg(wpt_id=initial_fix)])
        self.legs = legs

    def dump(self) -> str:
        return f"""<?xml version="1.0" encoding="Windows-1252"?>
<SimBase.Document Type="MissionFile" version="1,0" id="{self.mission_id}">
  <Title>{self.title}</Title>
  <Filename>{self.mission_id}.spb</Filename>
  <WorldBase.Flight InstanceId="{{9104F8D7-DC5B-453D-A7A4-6FE64834CF9A}}">
    <SimMission.MissionBushTrip InstanceId="{self.uuid}" id="{self.mission_id}">
      <Descr>{self.description}</Descr>
      <Legs>
        {self._dump_legs()}
      </Legs>
      <Objectives>
        <Objective UniqueRefId="{{37569C05-B09F-493B-A2C3-2BF1A8215E2E}}">
          <Descr>End mission</Descr>
          <FailureText>TT:MISSIONMESSAGE.FLIGHT.OUTOFFUEL</FailureText>
        </Objective>
      </Objectives>
      <OnFinishedActions>
        <WorldBase.ObjectReference id="End Of Mission" InstanceId="{{1AA91671-30AD-4A5C-8DEF-7D80C558EBDC}}" />
      </OnFinishedActions>
    </SimMission.MissionBushTrip>
    {self._dump_leg_completion_triggers()}
    <SimMission.Goal InstanceId="{{37569C05-B09F-493B-A2C3-2BF1A8215E2E}}">
      <Descr>End of mission</Descr>
      <Activated>false</Activated>
    </SimMission.Goal>
    <SimMission.GoalResolutionAction InstanceId="{{1AA91671-30AD-4A5C-8DEF-7D80C558EBDC}}">
      <Descr>Resolve Goal End of mission</Descr>
      <Goals>
        <WorldBase.ObjectReference id="Mission END" InstanceId="{{37569C05-B09F-493B-A2C3-2BF1A8215E2E}}" />
      </Goals>
    </SimMission.GoalResolutionAction>
    <SimMission.GoalResolutionAction InstanceId="{{ADBE1E35-9E4E-414E-82DA-1228398126CC}}">
      <Descr>Failure</Descr>
      <GoalResolution>failed</GoalResolution>
      <Goals>
        <WorldBase.ObjectReference id="Mission END" InstanceId="{{37569C05-B09F-493B-A2C3-2BF1A8215E2E}}" />
      </Goals>
    </SimMission.GoalResolutionAction>
    <SimMission.TimerTriggerFlowStateAction InstanceId="{{50B730D9-18C0-41F6-8B7D-8FD0A17BDD57}}">
      <Descr>TimerStart</Descr>
      <DefaultActivated>true</DefaultActivated>
      <OnScreenTimer>true</OnScreenTimer>
      <UseFirstFlightState>true</UseFirstFlightState>
      <Actions>
        <WorldBase.ObjectReference id="WiseAFSSet" InstanceId="{{43071EAB-D106-41CC-88D6-B113CDAE289B}}" />
      </Actions>
    </SimMission.TimerTriggerFlowStateAction>
    <SimMission.FlowStateAction InstanceId="{{7C4FE0D9-0507-471A-86E0-14014AC56E40}}">
      <FlowStateName>INTRO</FlowStateName>
      <StayInStateAfterEndTeleportActions>false</StayInStateAfterEndTeleportActions>
      <IsFirstStateInTimeline>true</IsFirstStateInTimeline>
      <FromSpawn>true</FromSpawn>
      <TeleportFlowEvents>
        <FlowEvent id="SHOW_MISSION_STARTUP" />
        <FlowEvent id="PAUSE_SIM" />
      </TeleportFlowEvents>
      <StartFlowEvents>
        <FlowEvent id="UNACTIVATE_PUSHBACK" />
        <FlowEvent id="UNPAUSE_SIM" />
        <FlowEvent id="PANEL_COPILOT_FORCE_DISABLED" />
        <FlowEvent id="PANEL_CHECKLIST_FORCE_DISABLED" />
        <FlowEvent id="PANEL_FUEL_PAYLOAD_FORCE_DISABLED" />
        <FlowEvent id="PANEL_TELEPORT_FORCE_DISABLED" />
        <FlowEvent id="PANEL_OBJECTIVES_FORCE_DISABLED" />
        <FlowEvent id="PANEL_ATC_FORCE_DISABLED" />
        <FlowEvent id="PANEL_CONTROLS_FORCE_DISABLED"/>
      </StartFlowEvents>
      <TeleportActions>
        <WorldBase.ObjectReference id="WWiseRTCState_RTC_CONDITIONAL" InstanceId="{{D6980D36-9C6D-4DD1-AFC6-3CB0C3D775B3}}" />
        <WorldBase.ObjectReference id="RTC_Ground_Airport_Aircraft_Intro" InstanceId="{{306B2AE4-06BA-48C3-93A0-BD5569E6EF5B}}" />
      </TeleportActions>
      <EndActions>
        <WorldBase.ObjectReference id="WWiseRTCState_NON_RTC" InstanceId="{{C3271B26-2A26-4830-A0DA-BB6AF9020A87}}" />
      </EndActions>
      <NextState id="BUSHTRIP" InstanceId="{{23552DE7-1761-4299-93D1-012CFA6CF761}}" />
    </SimMission.FlowStateAction>
    <SimMission.FlowStateAction InstanceId="{{23552DE7-1761-4299-93D1-012CFA6CF761}}">
      <FlowStateName>BUSHTRIP</FlowStateName>
      <AutoStateSwitchEnabled>false</AutoStateSwitchEnabled>
      <StartFlowEvents>
        <FlowEvent id="PANEL_GAME_NAVLOG_SHOW" />
        <FlowEvent id="PANEL_VFR_MAP_SHOW" />
      </StartFlowEvents>
      <NextState id="LANDING_REST" InstanceId="{{81E4FFFD-1D53-40C5-A13E-932466A4B998}}" />
    </SimMission.FlowStateAction>
    <SimMission.FlowStateAction InstanceId="{{81E4FFFD-1D53-40C5-A13E-932466A4B998}}">
      <FlowStateName>LANDING_REST</FlowStateName>
      <AutoStateSwitchEnabled>false</AutoStateSwitchEnabled>
      <StartActions>
        <WorldBase.ObjectReference id="RTC_Ground_Aircraft_Outro" InstanceId="{{5DAADB19-3BA3-4235-BCC0-39CD6F4CD4D9}}" />
      </StartActions>
      <NextState id="BUSHTRIP" InstanceId="{{23552DE7-1761-4299-93D1-012CFA6CF761}}" />
    </SimMission.FlowStateAction>
    <SimMission.Calculator id="CLTR_OutOfFuel" InstanceId="{{1A6F0319-B3D4-4237-B697-8E5459964E3B}}">
      <Descr>TT:MISSIONMESSAGE.FLIGHT.OUTOFFUEL</Descr>
      <Activated>true</Activated>
      <CalculatorFormula>
        [FuelQuantity]
      </CalculatorFormula>
      <CalculatorParameterList>
        <FormulaParameter NameInFormula="FuelQuantity">
          <CalculatorFormula>
            (A:FUEL TOTAL QUANTITY, gallons)
            (A:UNUSABLE FUEL TOTAL QUANTITY, gallons)
            -
          </CalculatorFormula>
        </FormulaParameter>
        <FormulaParameter NameInFormula="InAir">
          <CalculatorFormula>
            (A:PLANE ALT ABOVE GROUND, meter) (A:STATIC CG TO GROUND, meter) + 10 &gt;
          </CalculatorFormula>
        </FormulaParameter>
        <FormulaParameter NameInFormula="OnGround">
          <CalculatorFormula>
            (A:SIM ON GROUND, Boolean) 0 &gt;
          </CalculatorFormula>
        </FormulaParameter>
        <FormulaParameter NameInFormula="FlyingOutOfFuel">
          <CalculatorFormula>
            [FuelQuantity] 0.001 &lt;
            [OnGround] not
            and
            [FlyingOutOfFuel]
            or
          </CalculatorFormula>
        </FormulaParameter>
        <FormulaParameter NameInFormula="TimerOutOfFuel">
          <CalculatorFormula>
            [FlyingOutOfFuel]
            [OnGround]
            and
            if{{
            [TimerOutOfFuel]
            [dtime]
            +
            }}
            els{{
            0
            }}
          </CalculatorFormula>
        </FormulaParameter>
      </CalculatorParameterList>
      <CalculatorActions>
        <CalculatorAction>
          <CalculatorFormula>
            [TimerOutOfFuel]  15 &gt;
            [FlyingOutOfFuel]
            [OnGround]
            (A:GROUND VELOCITY, Knots) 5 &lt;
            and
            and
            or
          </CalculatorFormula>
          <Actions>
            <WorldBase.ObjectReference id="ACT_FailGoal" InstanceId="{{ADBE1E35-9E4E-414E-82DA-1228398126CC}}" />
          </Actions>
        </CalculatorAction>
        <CalculatorAction>
          <CalculatorFormula>
            [InAir]
          </CalculatorFormula>
          <Actions>
            <WorldBase.ObjectReference id="FlowEvent_DisableFuel" InstanceId="{{D1646D1F-CFB2-4D83-A490-AC05FD7C6188}}" />
          </Actions>
        </CalculatorAction>
      </CalculatorActions>
    </SimMission.Calculator>
    <SimMission.FlowEventAction InstanceId="{{F4FEBADA-8867-43E7-832D-947FAFCD8187}}">
      <Descr>FlowEvent_Landing_Rest</Descr>
      <FlowEvents>
        <FlowEvent id="BUSHTRIP_LEG_COMPLETED" />
      </FlowEvents>
    </SimMission.FlowEventAction>
    <SimMission.FlowEventAction InstanceId="{{D1646D1F-CFB2-4D83-A490-AC05FD7C6188}}">
      <Descr>FlowEvent_DisableFuel</Descr>
      <FlowEvents>
        <FlowEvent id="PANEL_FUEL_PAYLOAD_FORCE_DISABLED" />
      </FlowEvents>
    </SimMission.FlowEventAction>
    <SimMission.EventTriggerAction id="ACT_NotifOutOfRunway" InstanceId="{{952743E5-F838-4F51-A1A0-07E8DCD44019}}">
      <Descr>Landed outside of runway</Descr>
      <Name>EVENT_TRIGGER_NOT_ON_RUNWAY</Name>
    </SimMission.EventTriggerAction>
    <SimMission.FlowStateWise InstanceId="{{43071EAB-D106-41CC-88D6-B113CDAE289B}}">
      <Descr>WiseAFSSet</Descr>
      <GroupName>ACTIVITIES_FLOW_STATE</GroupName>
      <ElementName>BUSHTRIP</ElementName>
    </SimMission.FlowStateWise>
    <SimMission.FlowStateWise InstanceId="{{C3271B26-2A26-4830-A0DA-BB6AF9020A87}}">
      <Descr>WWiseRTCState_NON_RTC</Descr>
      <GroupName>GAME_RTC_STATE</GroupName>
      <ElementName>NON_RTC</ElementName>
    </SimMission.FlowStateWise>
    <SimMission.FlowStateWise InstanceId="{{D6980D36-9C6D-4DD1-AFC6-3CB0C3D775B3}}">
      <Descr>WWiseRTCState_RTC</Descr>
      <GroupName>GAME_RTC_STATE</GroupName>
      <ConditionalElementName>
        <ReversePolishCondition>(A:PLANE ALT ABOVE GROUND, meter) (A:STATIC CG TO GROUND, meter) - 0 &lt; </ReversePolishCondition>
        <ElementName>RTC</ElementName>
      </ConditionalElementName>
      <ConditionalElementName>
        <ReversePolishCondition>(A:PLANE ALT ABOVE GROUND, meter) (A:STATIC CG TO GROUND, meter) - 0 &gt; </ReversePolishCondition>
        <ElementName>RTC_IN_FLIGHT</ElementName>
      </ConditionalElementName>
    </SimMission.FlowStateWise>
  </WorldBase.Flight>
</SimBase.Document>
"""

    def _dump_legs(self) -> str:
        return '\n'.join([leg.dump(prev=prev)
                          for (prev, leg) in zip([self.initial_leg] + self.legs[:-1],
                                                 self.legs)])

    def _dump_leg_completion_triggers(self) -> str:
        return '\n'.join([leg.dump_leg_completion_trigger()
                          for leg in self.legs])


async def load_mission(source_dir: Path) -> Mission:
    metadata = json.loads(await (source_dir / f'{source_dir.name}.json').read_text())
    return Mission(mission_id=source_dir.name,
                   legs=[await bush_trip_generator.leg.load_leg(leg_source_dir)
                         for leg_source_dir in await source_dir.glob('leg_*')],
                   **metadata)
