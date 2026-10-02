# Phase 1: callable basic skills

## Scope and status

Phase 1 is a small Python callable layer with a JSON CLI for humans and agents.
It covers robot-local base velocity, timed lift commands, and named authored
arm gestures. It is not navigation, manipulation planning, or a robot simulator.

`KuralSkills()` uses `DryRunBackend` by default. A dry run validates and describes
a request without moving a robot. It does not wait out the requested duration.
No live DIMOS adapter, simulation execution, or hardware verification is claimed.
The sole robot model authority remains
`/home/josh/Desktop/Kural/kural_description`. No robot model is copied here.

`GatewayBackend` is an interface for an externally supplied, future approved
gateway with `submit`, `status`, `cancel`, and `stop`. It is not a connection to
the current DIMOS stack. Command payloads are intents, not permission to publish
directly to control streams. Do not bypass motion arbitration, clearance checks,
operator takeover, stop/estop, or command freshness limits.

## Python interface

```python
from kural_skills import KuralSkills

robot = KuralSkills()  # Dry run; no robot connection.
result = robot.base.forward(duration_s=1.0, speed_m_s=0.1)
print(result.as_dict())

robot.base.velocity(vx_m_s=0.1, vy_m_s=0.0,
                    yaw_rate_rad_s=0.2, duration_s=1.0)
robot.lift.up(duration_s=0.5)
robot.gestures.wave(timeout_s=20.0)

# Canonical names are shared by Python, CLI, and tool schemas.
result = robot.call("move_forward", duration_s=1.0, speed_m_s=0.1)
print(robot.describe("move_forward"))
print(robot.list_skills())
print(robot.tools())
```

The family methods and `call(skill, **params)` wait and return `SkillResult`.
`start(skill, **params)` returns an `Action` without waiting:

```python
action = robot.start("steer_back_left", duration_s=0.5,
                     speed_m_s=0.1, yaw_rate_rad_s=0.2)
print(action.operation_id)
print(action.status().as_dict())
print(action.wait(timeout_s=2.0).as_dict())
print(action.cancel().as_dict())  # A terminal dry run stays terminal.
```

A dry-run action is already terminal. `wait(timeout_s)` accepts a positive
finite timeout of at most 60 seconds. Its default is the request deadline plus
2 seconds. If the wait expires, it requests cancellation. If cancellation is
not reported terminal, it returns `outcome_unknown`; it cannot confirm a stop.
`cancel()` does not change an already-terminal operation except an unknown one.
An active action or unknown previous outcome blocks a new action on that client.
Use the result's state and reason; an operation ID is not execution evidence.

`stop()` requests a backend stop. It is not a physical-stop certificate.
`close()` and context-manager exit request stop. A closed client rejects new
requests. There is no automatic resume API or replay of stopped commands.

## Names, directions, and units

The canonical catalog is `src/kural_skills/catalog.py`.
All base velocities use the robot-local frame:

- +X: forward; -X: backward.
- +Y: left strafe; -Y: right strafe.
- +yaw: turn the robot heading left; -yaw: turn it right.
- Linear speed is in m/s. Yaw rate is in rad/s, not degrees/s.

| Python method after `robot.` | Canonical skill | Velocity signs (vx, vy, yaw) |
| --- | --- | --- |
| `base.forward` | `move_forward` | +, 0, 0 |
| `base.backward` | `move_backward` | -, 0, 0 |
| `base.left` | `move_left` | 0, +, 0 |
| `base.right` | `move_right` | 0, -, 0 |
| `base.steer_left` | `steer_left` | +, 0, + |
| `base.steer_right` | `steer_right` | +, 0, - |
| `base.steer_back_left` | `steer_back_left` | -, 0, + |
| `base.steer_back_right` | `steer_back_right` | -, 0, - |
| `base.turn_left` | `turn_left` | 0, 0, + |
| `base.turn_right` | `turn_right` | 0, 0, - |
| `base.velocity` | `base_velocity` | Signed explicit values |
| `lift.up` / `lift.down` | `lift_up` / `lift_down` | Authored lift actions |
| `gestures.home/wave/point/inspect/stow` | `home/wave/point/inspect/stow` | Authored named gestures |

**Reverse steering means heading direction, not a car steering-wheel angle.**
`steer_back_left` requests negative forward velocity and positive yaw: the robot
backs up while its heading rotates left. It does not promise that its rear moves
left. `steer_back_right` backs up while its heading rotates right. Strafe commands
do not request yaw. `turn_left/right` do not request translation.

### Parameter limits

These are callable-layer bounds, not calibrated safe hardware limits.

| Parameter | Default | Allowed values |
| --- | --- | --- |
| `duration_s` for base/lift | 1.0 | Greater than 0; at most 10 |
| `speed_m_s` for directional translation | 0.1 | Greater than 0; at most 0.2 |
| `yaw_rate_rad_s` for named steering/turning | 0.3 | Positive magnitude; at most 0.5 |
| `vx_m_s`, `vy_m_s` for `base_velocity` | 0.0 | Each in [-0.2, 0.2] |
| `yaw_rate_rad_s` for `base_velocity` | 0.0 | Signed value in [-0.5, 0.5] |
| `timeout_s` for gestures | 20.0 | Greater than 0; at most 30 |

Combined linear speed `sqrt(vx_m_s**2 + vy_m_s**2)` must not exceed 0.2 m/s.
Numbers must be finite; booleans are not numbers. Unknown skills and extra
parameters are rejected. Only applicable parameters appear in each schema.
A lift command takes a duration, not a target height or calibrated lift speed.
A gesture takes a deadline, not a joint target or perception/object argument.

Duration is a command interval, not a distance or arrival guarantee.
Gesture timeout is an execution deadline, not proof the gesture finished.
An action wait timeout limits how long the caller waits; it does not by itself
prove robot cancellation. Transport timeouts are a separate concern.

## CLI and agent discovery

After installing this package in the chosen project environment:

```sh
kural-skills list
kural-skills tools
kural-skills describe move_forward
kural-skills call move_forward --params '{"duration_s": 1.0, "speed_m_s": 0.1}'
kural-skills call base_velocity --params '{"vx_m_s": -0.1, "yaw_rate_rad_s": 0.2, "duration_s": 1.0}'
kural-skills call lift_up --params '{"duration_s": 0.5}'
kural-skills call wave --params '{"timeout_s": 20.0}'
kural-skills stop
kural-skills serve
```

The installed CLI is **dry-run only**; it has no live-backend switch or plugin.
`list` and `describe` expose the canonical catalog. `tools` and Python `tools()`
provide function descriptions and JSON parameter schemas; these are discovery
data, not evidence of runtime availability. One-shot commands print a JSON
object with `ok`, `backend: "dry_run"`, and `result` or `error`. Exit code 0 means
the CLI request completed; it does not mean physical success. Input errors use
exit code 2. No model credential is required.

### JSON-lines agent session

`kural-skills serve` reads one JSON request per stdin line and writes one JSON
response per stdout line. It is a local stdio interface, not HTTP, a deployed
robot gateway, or an MCP server. EOF closes the client and requests backend stop.

Example input lines:

```json
{"id": 1, "method": "tools"}
{"id": 2, "method": "describe", "skill": "steer_back_left"}
{"id": 3, "method": "start", "skill": "wave", "params": {"timeout_s": 20.0}}
```

Responses use `{"id": ..., "ok": true, "result": ...}` or
`{"id": ..., "ok": false, "error": "..."}`. An ID may be a string, integer,
or null. Additional methods are `list`, `call`, `status`, `cancel`, and `stop`.
For `status` or `cancel`, send `operation_id` from a prior `call` or `start`
result in **the same serve session**, not `skill` or `params`:

```json
{"id": 4, "method": "status", "operation_id": "COPY_RETURNED_OPERATION_ID"}
{"id": 5, "method": "cancel", "operation_id": "COPY_RETURNED_OPERATION_ID"}
{"id": 6, "method": "stop"}
```

`call` waits; `start` returns the current state. In dry run both are immediately
terminal. Status and cancellation are not standalone installed CLI commands.
Unknown operation IDs and extra fields are errors. Session action history is
bounded to 128 entries. Backends also retain at most 128 records by default
(`max_records` is configurable); only known-finished records may be evicted.
Running or unknown gateway operations are never evicted to admit new movement.
Old terminal IDs may expire. This protocol does not add execution permissions
or turn schemas into an authenticated robot service.

## Structured results

`SkillResult.as_dict()` contains:

- `operation_id`: identifier for this operation.
- `skill`, `request`: canonical name and normalized requested intent.
- `state`, `reason`: lifecycle state and its explanation.
- `motion_verified`, `stop_confirmed`: both false in this Phase 1 facade.
- `evidence`: backend details; not a physical verification claim.

| State | Meaning |
| --- | --- |
| `accepted` | Request accepted; motion not confirmed. |
| `running` | Backend reports active execution. |
| `cancel_requested` | Cancellation requested; outcome not yet terminal. |
| `dry_run` | Terminal validated intent; no robot motion. |
| `command_finished` | Terminal reported end of a command; no arrival proof. |
| `gesture_finished` | Terminal reported end of a gesture; no pose proof. |
| `blocked` | Terminal refusal or safety block; read the reason. |
| `cancelled` | Terminal reported cancellation; physical stop unverified. |
| `failed` | Terminal known failure; read the reason. |
| `outcome_unknown` | Terminal unknown outcome; do not assume stopped or retry automatically. |

There is deliberately no `success` state that asserts physical task success.
A terminal state means the operation record is finished, not that movement was
measured or the robot is safe. Even a reported finish leaves both verification
flags false. On uncertainty, do not issue replacement motion automatically.

## What remains blocked

Live execution requires an explicitly approved gateway and real integration
tests. Constructing `GatewayBackend(gateway)` requires a `capabilities()` dict
with protocol `kural.skills.gateway.v1`, `runtime_integrated: true`, a nonempty
`namespace`, and a `skills` list. These declarations are handshake data, not
proof that the gateway is approved, safe, or tested. Unsupported skills are
blocked. `submit/status/cancel/stop` receive a dict containing `client_id` and
`operation_id`; `submit` also includes `request`. Replies must match the
operation ID and canonical skill (or `stop` for global stop). Gateway call or
response failures report `outcome_unknown` without automatic command retry.
Transport calls must themselves be bounded; a caller wait cannot interrupt an
indefinitely blocked transport call.

A base request's `nav_cmd_vel` payload is a logical source contract, not robot
input authorization. The same applies to `arm_request` lift/gesture payloads.
Neither payload grants permission to publish directly into the current stack.

That gateway must retain one physics/control owner, arbitration, operator
priority, stop/estop, freshness watchdogs, applicable clearance checks, and
observed completion/stop reporting. No implicit resume or direct stream shortcut
is allowed. Named gestures must use the authoritative robot's existing controls;
this package does not define new poses or recreate robot mechanisms.

See [the skill definition](../skills/phase1/README.md) for prerequisites and
verification requirements. [SDK inspiration](SDK-INSPIRATION.md) records the
external references and their limits. No depth or perception work is included.
