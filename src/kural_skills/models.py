"""Validated requests and honest action results; no robot/simulator imports."""
from dataclasses import dataclass, field
import math
import json
from copy import deepcopy
from typing import Any
from .catalog import BASE_DIRECTIONS, CATALOG

TERMINAL_STATES = frozenset({"dry_run", "command_finished", "gesture_finished", "blocked",
    "cancelled", "failed", "outcome_unknown"})
ALL_STATES = TERMINAL_STATES | {"accepted", "running", "cancel_requested"}

def finite_number(value: Any, name: str, minimum: float, maximum: float, *, positive=False) -> float:
    if type(value) not in (int, float):
        raise ValueError(f"{name} must be a finite number (not a boolean)")
    # Check bounds before float conversion: giant JSON integers must be rejected,
    # not overflow math.isfinite() and kill an agent session.
    if value < minimum or value > maximum or (positive and value <= 0):
        raise ValueError(f"{name} is outside its allowed bounds")
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return float(value)

@dataclass(frozen=True)
class SkillRequest:
    skill: str
    parameters: dict[str, float]
    family: str
    duration_s: float | None
    timeout_s: float
    command: dict[str, Any]

    @classmethod
    def create(cls, skill: str, **parameters: Any) -> "SkillRequest":
        if not isinstance(skill,str) or skill not in CATALOG:
            raise ValueError(f"Unknown skill: {skill!r}")
        definition = CATALOG[skill]
        props = definition.parameters["properties"]
        unknown = parameters.keys() - props.keys()
        if unknown: raise ValueError(f"Unsupported parameters: {', '.join(sorted(unknown))}")
        values = {}
        for name,schema in props.items():
            values[name] = finite_number(parameters.get(name,schema["default"]),name,
                schema.get("minimum",0),schema["maximum"],positive="exclusiveMinimum" in schema)
        duration = values.get("duration_s")
        timeout = values.get("timeout_s", duration if duration is not None else 20.)
        if definition.family == "base":
            if skill == "base_velocity": vx,vy,yaw = values["vx_m_s"],values["vy_m_s"],values["yaw_rate_rad_s"]
            else:
                x,y,z = BASE_DIRECTIONS[skill]
                vx,vy,yaw = x*values.get("speed_m_s",0), y*values.get("speed_m_s",0), z*values.get("yaw_rate_rad_s",0)
            if math.hypot(vx,vy) > .2 + 1e-12:
                raise ValueError("Combined linear speed exceeds 0.2 m/s")
            command = {"stream": "nav_cmd_vel", "linear": [vx,vy,0.], "angular": [0.,0.,yaw]}
        elif definition.family == "lift":
            command = {"stream": "arm_request", "body": {"kind": "actions",
                       "actions": ["liftUp" if skill == "lift_up" else "liftDown"]}}
        else:
            command = {"stream": "arm_request", "body": {"kind": "gesture", "name": skill}}
        return cls(skill,values,definition.family,duration,timeout,command)

    def as_dict(self) -> dict[str, Any]:
        return {"skill": self.skill, "parameters": dict(self.parameters), "family": self.family,
                "duration_s": self.duration_s, "timeout_s": self.timeout_s, "command": deepcopy(self.command)}

@dataclass(frozen=True)
class SkillResult:
    operation_id: str
    skill: str
    state: str
    reason: str
    request: dict[str, Any] = field(default_factory=dict)
    motion_verified: bool = False
    stop_confirmed: bool = False
    evidence: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.state not in ALL_STATES: raise ValueError("Unknown action state")
        if not isinstance(self.operation_id,str) or not self.operation_id:
            raise ValueError("Missing operation ID")
        if self.motion_verified or self.stop_confirmed:
            # This facade makes no hardware/simulation motion-verification claims.
            raise ValueError("Motion/stop verification is not supported by this Phase 1 facade")
        if not isinstance(self.skill,str) or not isinstance(self.reason,str):
            raise ValueError("Result skill and reason must be strings")
        if not isinstance(self.request,dict) or not isinstance(self.evidence,dict):
            raise ValueError("Result request and evidence must be JSON objects")
        try:
            json.dumps({"request":self.request,"evidence":self.evidence},allow_nan=False)
        except (ValueError,TypeError,OverflowError) as exc:
            raise ValueError("Result contains non-JSON or nonfinite data") from exc
        object.__setattr__(self,"request",deepcopy(self.request))
        object.__setattr__(self,"evidence",deepcopy(self.evidence))

    @property
    def terminal(self) -> bool: return self.state in TERMINAL_STATES

    def as_dict(self) -> dict[str, Any]:
        result = {"operation_id": self.operation_id, "skill": self.skill, "state": self.state,
                  "reason": self.reason, "request": deepcopy(self.request), "motion_verified": False,
                  "stop_confirmed": False, "evidence": deepcopy(self.evidence)}
        try:
            json.dumps(result,allow_nan=False)
        except (ValueError,TypeError,OverflowError) as exc:
            raise ValueError("Result contains non-JSON or nonfinite data") from exc
        return result
