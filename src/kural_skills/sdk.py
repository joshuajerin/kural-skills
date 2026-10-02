"""One dispatcher behind Python methods, agent tools, and the CLI."""
from copy import deepcopy
import threading
import time
from uuid import uuid4
from .backends import Backend, DryRunBackend
from .catalog import CATALOG, GESTURES
from .models import SkillRequest, SkillResult, finite_number

class Action:
    def __init__(self, backend: Backend, initial: SkillResult, request_snapshot: dict | None = None):
        self.backend,self._result = backend,initial
        # Keep our failure/deadline data separate from mutable backend objects.
        self._request_snapshot = deepcopy(request_snapshot if request_snapshot is not None else initial.request)
        self._lock = threading.RLock()

    @property
    def operation_id(self) -> str: return self._result.operation_id

    def status(self) -> SkillResult:
        with self._lock:
            if not self._result.terminal or self._result.state == "outcome_unknown":
                try:
                    result = self.backend.status(self.operation_id)
                    self._check(result)
                except Exception as exc:
                    result = SkillResult(self.operation_id,self._result.skill,"outcome_unknown",
                        f"Status outcome unknown: {type(exc).__name__}: {exc}",self._request_snapshot)
                self._result = result
            return self._result

    def _check(self, result: SkillResult):
        if not isinstance(result,SkillResult) or result.operation_id != self.operation_id or result.skill != self._result.skill:
            raise ValueError("Backend returned a mismatched action")
        result.as_dict()  # Revalidate injected results after possible mutation.

    def cancel(self) -> SkillResult:
        with self._lock:
            if self._result.terminal and self._result.state != "outcome_unknown": return self._result
            try:
                result = self.backend.cancel(self.operation_id)
                self._check(result)
            except Exception as exc:
                result = SkillResult(self.operation_id,self._result.skill,"outcome_unknown",
                    f"Cancellation outcome unknown: {type(exc).__name__}: {exc}",self._request_snapshot)
            self._result = result
            return result

    def wait(self, timeout_s: float | None = None) -> SkillResult:
        if timeout_s is None: timeout_s = self._request_snapshot.get("timeout_s",20.) + 2.
        timeout_s = finite_number(timeout_s,"wait timeout_s",0,60,positive=True)
        deadline = time.monotonic()+timeout_s
        while True:
            result = self.status()
            if result.terminal: return result
            remaining = deadline-time.monotonic()
            if remaining <= 0:
                cancelled = self.cancel()
                if cancelled.terminal: return cancelled
                with self._lock:
                    self._result = SkillResult(self.operation_id,result.skill,"outcome_unknown",
                        "Wait timed out; cancellation requested but not confirmed. Use operator STOP if needed.",self._request_snapshot)
                return self._result
            time.sleep(min(.05,remaining))

class BaseSkills:
    def __init__(self, robot: "KuralSkills"): self.robot = robot
    def forward(self, *, duration_s=1., speed_m_s=.1): return self.robot.call("move_forward",duration_s=duration_s,speed_m_s=speed_m_s)
    def backward(self, *, duration_s=1., speed_m_s=.1): return self.robot.call("move_backward",duration_s=duration_s,speed_m_s=speed_m_s)
    def left(self, *, duration_s=1., speed_m_s=.1): return self.robot.call("move_left",duration_s=duration_s,speed_m_s=speed_m_s)
    def right(self, *, duration_s=1., speed_m_s=.1): return self.robot.call("move_right",duration_s=duration_s,speed_m_s=speed_m_s)
    def steer_left(self, *, duration_s=1., speed_m_s=.1, yaw_rate_rad_s=.3): return self.robot.call("steer_left",duration_s=duration_s,speed_m_s=speed_m_s,yaw_rate_rad_s=yaw_rate_rad_s)
    def steer_right(self, *, duration_s=1., speed_m_s=.1, yaw_rate_rad_s=.3): return self.robot.call("steer_right",duration_s=duration_s,speed_m_s=speed_m_s,yaw_rate_rad_s=yaw_rate_rad_s)
    def steer_back_left(self, *, duration_s=1., speed_m_s=.1, yaw_rate_rad_s=.3): return self.robot.call("steer_back_left",duration_s=duration_s,speed_m_s=speed_m_s,yaw_rate_rad_s=yaw_rate_rad_s)
    def steer_back_right(self, *, duration_s=1., speed_m_s=.1, yaw_rate_rad_s=.3): return self.robot.call("steer_back_right",duration_s=duration_s,speed_m_s=speed_m_s,yaw_rate_rad_s=yaw_rate_rad_s)
    def turn_left(self, *, duration_s=1., yaw_rate_rad_s=.3): return self.robot.call("turn_left",duration_s=duration_s,yaw_rate_rad_s=yaw_rate_rad_s)
    def turn_right(self, *, duration_s=1., yaw_rate_rad_s=.3): return self.robot.call("turn_right",duration_s=duration_s,yaw_rate_rad_s=yaw_rate_rad_s)
    def velocity(self, *, vx_m_s=0., vy_m_s=0., yaw_rate_rad_s=0., duration_s=1.): return self.robot.call("base_velocity",vx_m_s=vx_m_s,vy_m_s=vy_m_s,yaw_rate_rad_s=yaw_rate_rad_s,duration_s=duration_s)

class LiftSkills:
    def __init__(self, robot: "KuralSkills"): self.robot = robot
    def up(self, *, duration_s=1.): return self.robot.call("lift_up",duration_s=duration_s)
    def down(self, *, duration_s=1.): return self.robot.call("lift_down",duration_s=duration_s)

class GestureSkills:
    def __init__(self, robot: "KuralSkills"): self.robot = robot
    def run(self, name: str, *, timeout_s=20.):
        if name not in GESTURES: raise ValueError("Unknown authored gesture")
        return self.robot.call(name,timeout_s=timeout_s)
    def home(self, *, timeout_s=20.): return self.run("home",timeout_s=timeout_s)
    def wave(self, *, timeout_s=20.): return self.run("wave",timeout_s=timeout_s)
    def point(self, *, timeout_s=20.): return self.run("point",timeout_s=timeout_s)
    def inspect(self, *, timeout_s=20.): return self.run("inspect",timeout_s=timeout_s)
    def stow(self, *, timeout_s=20.): return self.run("stow",timeout_s=timeout_s)

class KuralSkills:
    def __init__(self, backend: Backend | None = None):
        self.backend = backend if backend is not None else DryRunBackend()
        self.base,self.lift,self.gestures = BaseSkills(self),LiftSkills(self),GestureSkills(self)
        self._lock = threading.RLock()
        self._active: Action | None = None
        self._closed = False

    @staticmethod
    def list_skills(): return deepcopy([d.as_dict() for d in CATALOG.values()])
    @staticmethod
    def describe(name: str):
        if name not in CATALOG: raise ValueError("Unknown skill")
        return deepcopy(CATALOG[name].as_dict())
    @staticmethod
    def tools(): return deepcopy([d.tool() for d in CATALOG.values()])

    def start(self, skill: str, **parameters) -> Action:
        request = SkillRequest.create(skill,**parameters)
        request_snapshot = deepcopy(request.as_dict())
        with self._lock:
            if self._closed: raise RuntimeError("Skills client is closed")
            if self._active:
                previous = self._active.status()
                if not previous.terminal or previous.state == "outcome_unknown":
                    result = SkillResult(str(uuid4()),skill,"blocked",
                        "Another action is active or its outcome is unknown. Resolve/cancel it first.",request_snapshot)
                    return Action(self.backend,result,request_snapshot)
            try:
                result = self.backend.submit(request)
                if not isinstance(result,SkillResult) or result.skill != skill:
                    raise ValueError("Backend returned an invalid submission")
                result.as_dict()
            except Exception as exc:
                result = SkillResult(str(uuid4()),skill,"outcome_unknown",
                    f"Submission outcome unknown: {type(exc).__name__}: {exc}. Do not retry; use operator STOP if needed.",request_snapshot)
            action = Action(self.backend,result,request_snapshot)
            self._active = action
            return action

    def call(self, skill: str, **parameters) -> SkillResult: return self.start(skill,**parameters).wait()

    def stop(self) -> SkillResult:
        # Backend STOP is global/latched when live; never auto-resume afterward.
        with self._lock:
            try:
                result = self.backend.stop()
                if not isinstance(result,SkillResult) or result.skill != "stop":
                    raise ValueError("Invalid backend stop result")
                result.as_dict()
            except Exception as exc:
                result = SkillResult(str(uuid4()),"stop","outcome_unknown",
                    f"STOP outcome unknown: {type(exc).__name__}: {exc}. Use operator STOP.")
            return result

    def close(self):
        with self._lock:
            if not self._closed:
                self._closed = True
                return self.stop()
        return None

    def __enter__(self): return self
    def __exit__(self, *_): self.close()
