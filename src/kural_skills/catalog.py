"""Phase 1 skill definitions. Robot-local +X forward, +Y left, +yaw left."""
from dataclasses import dataclass
from typing import Any

GESTURES = ("home", "wave", "point", "inspect", "stow")
# Reverse steering is explicitly yaw direction, NOT a car wheel angle.
BASE_DIRECTIONS = {
    "move_forward": (1, 0, 0), "move_backward": (-1, 0, 0),
    "move_left": (0, 1, 0), "move_right": (0, -1, 0),
    "steer_left": (1, 0, 1), "steer_right": (1, 0, -1),
    "steer_back_left": (-1, 0, 1), "steer_back_right": (-1, 0, -1),
    "turn_left": (0, 0, 1), "turn_right": (0, 0, -1),
}
DESCRIPTIONS = {
    "move_forward": "Move forward in the robot frame.",
    "move_backward": "Move backward in the robot frame.",
    "move_left": "Strafe left without requesting a turn.",
    "move_right": "Strafe right without requesting a turn.",
    "steer_left": "Move forward while turning the robot heading left.",
    "steer_right": "Move forward while turning the robot heading right.",
    "steer_back_left": "Move backward while turning the robot heading left (+yaw).",
    "steer_back_right": "Move backward while turning the robot heading right (-yaw).",
    "turn_left": "Turn left in place.", "turn_right": "Turn right in place.",
    "base_velocity": "Request bounded robot-local vx/vy/yaw velocities.",
    "lift_up": "Raise the lift using the existing authored liftUp action.",
    "lift_down": "Lower the lift using the existing authored liftDown action.",
    **{name: f"Run the existing authored {name} gesture." for name in GESTURES},
}

def number(description: str, default: float, maximum: float) -> dict[str, Any]:
    return {"type": "number", "description": description, "exclusiveMinimum": 0,
            "maximum": maximum, "default": default}

@dataclass(frozen=True)
class SkillDefinition:
    name: str
    family: str
    description: str
    parameters: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {"name": self.name, "family": self.family,
                "description": self.description, "parameters": self.parameters,
                "status": "implemented_callable_layer_not_live_robot_verified"}

    def tool(self) -> dict[str, Any]:
        return {"type": "function", "function": {"name": self.name,
                "description": self.description, "parameters": self.parameters}}

def definitions() -> tuple[SkillDefinition, ...]:
    result = []
    for name in DESCRIPTIONS:
        family = "gesture" if name in GESTURES else "lift" if name.startswith("lift_") else "base"
        if family == "gesture":
            props = {"timeout_s": number("Execution deadline in seconds, not proof of completion.", 20., 30.)}
        else:
            props = {"duration_s": number("Command interval in seconds, not a distance or arrival goal.", 1., 10.)}
            if family == "base":
                if name == "base_velocity":
                    props.update({key: {"type": "number", "minimum": -limit, "maximum": limit,
                                  "default": 0., "description": units}
                                  for key,limit,units in (("vx_m_s",.2,"Forward m/s."),("vy_m_s",.2,"Left m/s."),
                                                          ("yaw_rate_rad_s",.5,"Left-turn rad/s."))})
                else:
                    x,y,yaw = BASE_DIRECTIONS[name]
                    if x or y: props["speed_m_s"] = number("Positive requested linear speed in m/s.", .1, .2)
                    if yaw: props["yaw_rate_rad_s"] = number("Positive requested yaw magnitude in rad/s.", .3, .5)
        result.append(SkillDefinition(name, family, DESCRIPTIONS[name],
                      {"type": "object", "properties": props, "additionalProperties": False}))
    return tuple(result)

CATALOG = {definition.name: definition for definition in definitions()}
