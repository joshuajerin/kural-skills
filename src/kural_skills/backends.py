"""Backends: dry-run by default; no direct robot-controller or stream writes."""
from copy import deepcopy
import threading
from typing import Protocol, Any
from uuid import uuid4
from .models import SkillRequest, SkillResult

class Backend(Protocol):
    def submit(self, request: SkillRequest) -> SkillResult: ...
    def status(self, operation_id: str) -> SkillResult: ...
    def cancel(self, operation_id: str) -> SkillResult: ...
    def stop(self) -> SkillResult: ...

class DryRunBackend:
    """Serialize and record requests. Never move a robot or wait out a duration."""
    def __init__(self, max_records: int = 128):
        if type(max_records) is not int or not 1 <= max_records <= 4096:
            raise ValueError("max_records must be an integer in [1,4096]")
        self.max_records = max_records
        self._results: dict[str, SkillResult] = {}
        self._lock = threading.RLock()

    def submit(self, request: SkillRequest) -> SkillResult:
        request = SkillRequest.create(request.skill, **request.parameters)
        result = SkillResult(str(uuid4()),request.skill,"dry_run",
            "Validated and recorded only. No runtime connected; no robot motion.",deepcopy(request.as_dict()))
        with self._lock:
            self._results[result.operation_id] = result
            while len(self._results) > self.max_records:
                del self._results[next(iter(self._results))]
        return result

    def status(self, operation_id: str) -> SkillResult:
        with self._lock:
            if operation_id not in self._results: raise ValueError("Unknown operation ID")
            return self._results[operation_id]

    def cancel(self, operation_id: str) -> SkillResult:
        with self._lock:
            old = self.status(operation_id)
            result = SkillResult(old.operation_id,old.skill,"cancelled",
                "Dry-run cancelled; no live command was sent.",old.request)
            self._results[operation_id] = result
            return result

    def stop(self) -> SkillResult:
        return SkillResult(str(uuid4()),"stop","dry_run","No runtime connected. No robot stop was sent.")

class GatewayBackend:
    """Adapter to a FUTURE externally supplied, approved single-owner gateway.

    This is NOT a DIMOS client and creates no network service. The gateway must
    implement capabilities/submit/status/cancel/stop with bounded transport calls
    and independently enforce authorization, ownership, command deadlines,
    client-liveness cancellation, and the real robot's safety gates.
    """
    def __init__(self, gateway: Any, max_records: int = 128):
        if type(max_records) is not int or not 1 <= max_records <= 4096:
            raise ValueError("max_records must be an integer in [1,4096]")
        self.max_records = max_records
        self._states: dict[str,str] = {}
        self.gateway = gateway
        self.client_id = str(uuid4())
        self._requests: dict[str, SkillRequest] = {}
        self._lock = threading.RLock()
        caps = gateway.capabilities()
        if not isinstance(caps,dict) or caps.get("protocol") != "kural.skills.gateway.v1":
            raise ValueError("Not a kural.skills.gateway.v1 gateway")
        if caps.get("runtime_integrated") is not True or not isinstance(caps.get("namespace"),str) or not caps["namespace"]:
            raise ValueError("Gateway has no declared runtime integration/namespace")
        names = caps.get("skills")
        if not isinstance(names,list) or any(not isinstance(name,str) for name in names):
            raise ValueError("Gateway must declare supported skills")
        self.skills = frozenset(names)

    def _response(self, value: Any, operation_id: str, request: SkillRequest | None) -> SkillResult:
        if not isinstance(value,dict) or value.get("operation_id") != operation_id:
            raise ValueError("Gateway returned a missing/mismatched operation ID")
        skill = request.skill if request is not None else "stop"
        if value.get("skill") != skill: raise ValueError("Gateway skill mismatch")
        return SkillResult(operation_id,skill,value["state"],str(value.get("reason","")),
            deepcopy(request.as_dict()) if request else {}, evidence=deepcopy(value.get("evidence",{})))

    def _invoke(self, method: str, operation_id: str, request: SkillRequest | None, payload: dict) -> SkillResult:
        try:
            value = getattr(self.gateway,method)(payload)
            result = self._response(value,operation_id,request)
        except Exception as exc:
            # An RPC timeout/failure is not cancellation. Never retry a command.
            result = SkillResult(operation_id,request.skill if request else "stop","outcome_unknown",
                f"{method} outcome unknown: {type(exc).__name__}: {exc}",
                deepcopy(request.as_dict()) if request else {})
        if request is not None:
            with self._lock: self._states[operation_id] = result.state
        return result

    def submit(self, request: SkillRequest) -> SkillResult:
        request = SkillRequest.create(request.skill, **request.parameters)
        operation_id = str(uuid4())
        if request.skill not in self.skills:
            return SkillResult(operation_id,request.skill,"blocked","Gateway does not support this skill.",request.as_dict())
        with self._lock:
            # Evict only known-finished records, NEVER running/unknown outcomes.
            safe_states = {"dry_run","command_finished","gesture_finished","blocked","cancelled","failed"}
            for old_id in list(self._requests):
                if len(self._requests) < self.max_records: break
                if self._states.get(old_id) in safe_states:
                    del self._requests[old_id]; self._states.pop(old_id,None)
            if len(self._requests) >= self.max_records:
                return SkillResult(operation_id,request.skill,"blocked",
                    "Gateway record capacity reached; unresolved operations must be resolved first.",request.as_dict())
            self._requests[operation_id] = request
            self._states[operation_id] = "accepted"
        return self._invoke("submit",operation_id,request,
            {"client_id": self.client_id,"operation_id": operation_id,"request": request.as_dict()})

    def _operation(self, method: str, operation_id: str) -> SkillResult:
        with self._lock:
            if operation_id not in self._requests: raise ValueError("Unknown operation ID")
            request = self._requests[operation_id]
        return self._invoke(method,operation_id,request,{"client_id": self.client_id,"operation_id": operation_id})

    def status(self, operation_id: str) -> SkillResult: return self._operation("status",operation_id)
    def cancel(self, operation_id: str) -> SkillResult: return self._operation("cancel",operation_id)

    def stop(self) -> SkillResult:
        operation_id = str(uuid4())
        return self._invoke("stop",operation_id,None,{"client_id": self.client_id,"operation_id": operation_id})
