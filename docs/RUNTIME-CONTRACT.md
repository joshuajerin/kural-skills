# Runtime contract and integration limits

## Phase 1 status

Phase 1 is an executable SDK, CLI and JSON-lines interface. It is not a robot
runtime or a DIMOS motion bridge. `DryRunBackend` is the default. It builds and
records bounded requests without publishing commands or moving a robot.

`GatewayBackend` accepts an externally supplied gateway. It does not discover,
start or approve a robot-control service. A future gateway must meet the contract
below before it can execute requests. Injecting a callable alone is not proof of
safe runtime integration.

- Base and lift skills are **not live-bound** in this phase.
- `home`, `wave`, `point`, `inspect` and `stow` reuse existing gesture names.
  Their robot source exists, but SDK execution is **not live-verified**.
- Unit tests or recorded requests do not prove simulation or hardware motion.
- No perception, depth, clearance producer, planner, model export or physics
  owner is added here.

The sole robot model authority remains
`/home/josh/Desktop/Kural/kural_description`. This repository must not copy robot
models, actuator mappings or gesture trajectories into a second authority.

## Requests and results

Requests describe bounded intent, not guaranteed displacement or joint motion.
Robot-local coordinates are +X forward, +Y left and positive yaw left.

| Skill | Intent |
| --- | --- |
| `move_forward` / `move_backward` | Positive / negative X translation |
| `move_left` / `move_right` | Positive / negative Y strafe, not rotation |
| `steer_left` / `steer_right` | Forward translation with positive / negative yaw |
| `steer_back_left` / `steer_back_right` | Reverse translation with positive / negative yaw |
| `turn_left` / `turn_right` | Positive / negative in-place yaw |
| `lift_up` / `lift_down` | Timed existing `liftUp` / `liftDown` action |
| `home`, `wave`, `point`, `inspect`, `stow` | One existing discrete gesture request |

Reverse steering names specify **yaw sign**, not car steering-wheel angle. Do
not infer reversed yaw signs from car steering behavior.

Phase 1 bounds are at most 10 seconds for continuous requests, 0.2 m/s combined
linear speed and 0.5 rad/s yaw. Gesture timeout is at most 30 seconds, with a
20-second default. These are SDK validation bounds, not runtime guarantees.
The runtime must enforce equal or stricter bounds independently.

The backend boundary is `submit(request)`, `status(operation_id)`,
`cancel(operation_id)` and `stop()`. Operation IDs identify local requests. They
do not imply that the robot arbiter acknowledged ownership.

A successful submission means only what the backend can demonstrate. Dry run
means no motion. Acceptance, elapsed duration or a finished command does not
prove physical arrival. Gesture status clearing does not prove measured joints
settled. Phase 1 does not assert `motion_verified` or `stop_confirmed`.
Transport loss after submission must not be reported as successful completion.

## Existing DIMOS routes: source findings

The read-only review covered the `local-stack` source in
`/home/josh/Desktop/Kural-combined-motion`, including `control.py` (there is no
`arbiter.py` there), `robot.py`, `scene.py`, `blueprints.py` and `native_view.py`.
It also reviewed controller/gesture source and compared it with the sole model
authority. These are source findings, not live integration results.

### Base and arm

The supported base route is:

`manual_cmd_vel` or `nav_cmd_vel` -> `CommandArbiter` -> `cmd_vel` ->
`SceneRuntime` -> `RobotBinding` -> owning physics thread -> authoritative
`Controller.tick(base_velocity=(vx, vy, yawRate))`.

An agent-capable future gateway must use the guarded autonomous route. It must
never disguise agent commands as human `manual_cmd_vel` to bypass clearance.
A supervised human primitive mode would need separate approved ownership.

The arm route is:

`arm_request` JSON -> arbiter authorization -> `authorized_arm_request` ->
`RobotBinding` -> owning physics thread.

Existing arm request forms include:

```json
{"kind": "actions", "actions": ["liftUp"]}
{"kind": "actions", "actions": ["liftDown"]}
{"kind": "actions", "actions": []}
{"kind": "gesture", "name": "wave"}
```

The source also supports selected-joint jogging/selection and gripper toggling.
That does not expand the requested Phase 1 skill scope. There is no arbitrary
lift target or lift velocity request in this route.

The reviewed scene and arbiter expose lifecycle RPCs, not per-primitive motion
RPCs. Scene `health()` is explicitly a diagnostic snapshot, not a control input.
Do not call private scene/controller methods, write `qpos` or actuator controls,
publish directly to `cmd_vel` or `authorized_arm_request`, or use native test
keyboard injection as a production adapter.

### Readiness and clearance

The existing arbiter requires robot readiness, no latched estop and a fresh
operator heartbeat. The reviewed blueprint uses 250 ms command and heartbeat
timeouts, a 2-second scene-status timeout, enabled strafe, 0.2 m/s linear norm
and 0.5 rad/s yaw limits. `RobotBinding` separately checks fresh commands and
control status. Authored acceleration, heading control, wheel limits and lift
limits remain in the authoritative controller. Commanded velocity is not
measured velocity.

Autonomous base motion additionally requires a fresh observed swept-volume
certificate matched to the robot envelope identity and episode epoch. The
binding checks scope `observed_swept_volume_v1`, timestamp, radius, identity and
epoch. A 2D map or valid model envelope is not that certificate.

In the reviewed source, `RobotBinding.set_navigation_clearance()` has no runtime
caller. Only a test supplies evidence. The current binding reports unavailable
clearance. Neither camera mode nor the static comparison baseline is an
approved escape from this gate. Guarded base execution therefore remains
blocked. Phase 1 must not create evidence, alter evidence timestamps, turn off
the requirement or add an evidence ingress to make a request succeed.

Even a future certificate does not by itself approve an arbitrary primitive.
Direct `nav_cmd_vel` publication bypasses `LocalNavigation._on_velocity()` checks
for the command horizon, whole-reach disk and curved-translation clearance.
`navigation_status.available` is general readiness, not approval of the requested
primitive corridor. A future integration must reuse an approved command-path
safety guard. Phase 1 does not implement one.

### Ownership conflicts

The existing arbiter distinguishes manual from navigation intent, not individual
clients. It has no client ID, lease or atomic planner-versus-skill grant.

The native window publishes heartbeat and held base/arm actions at 30 Hz. Even
when idle, it publishes zero base intent and an empty arm action list. An
independent publisher races those updates: native zeros clear external manual
base/lift intent. Native lift/jog/gripper requests can override a gesture.

The planner can also publish zero `nav_cmd_vel` while idle or unavailable. Its
watchdog emits blocked zeros at 10 Hz. A second navigation publisher therefore
has conflicts even when the planner has no active goal.

A global heartbeat has no client identity. Adding a skill heartbeat can mask
native event-loop failure. Conversely, if the skill client disappears while the
native heartbeat continues, a discrete gesture can continue. Native heartbeat
is not proof of skill-client liveness.

### Gesture and stop semantics

- Empty arm actions release held lift/jog input. They do **not** cancel a gesture.
- Nonzero lift/jog intent cancels a gesture. Gripper toggling also cancels it.
  Do not use either as an invented gesture-cancel operation.
- A gesture can start and then cancel immediately if an incompatible lift/jog
  hold is still active. The current status stream does not expose an arm owner
  or all held actions.
- Another gesture while one is active is rejected by the controller. That
  return value is not carried back as a per-request acknowledgment.
- Gesture segment timing expands to meet velocity and acceleration limits.
  Authored keyframe duration is not a reliable completion deadline.
- Zero base intent is ordinary deceleration, not emergency stop or gesture cancel.
- Global `stop_movement=true` latches the arbiter stop, cancels navigation and
  clears commands. The binding stops the controller, cancels gestures and holds
  commanded arm/lift targets. This is not mechanical braking or a measured-pose
  freeze.
- Resume clears old intent. It must not restore old holds or pending requests.
  STOP and RESUME are separate streams; sending both is not an ordering guarantee.
- There is no existing request for reliable gesture-only cancellation or
  base-only immediate stopping through these arbiter inputs.

The reviewed combined-motion controller preserves wheels at gesture start. The
sole authoritative controller instead calls `self.stop()` at gesture start.
Gesture JSON was identical at review. `paths.py` defaults to the sole authority
unless `KURAL_WORKSPACE` overrides it. Do not claim the copied controller's
combined-motion behavior is the active authoritative behavior. Reconciliation
requires approval and later verification; this phase does neither.

## Requirements for a future approved gateway

These requirements describe missing integration work. They do not state that a
gateway is deployed or that Phase 1 implements it.

### One owner and atomic approval

Keep the existing native UI, motion arbiter and single physics owner. An approved
integration needs one owner-aware mux or lease boundary for native manual,
planner and skill intent. A client-side lock cannot arbitrate other processes.

The ownership grant must be atomic with safety approval and tied to a request ID,
client identity, scene namespace and episode epoch. Admission must check both
base and arm ownership. A read of `mode=idle` or `goal=null` followed by publish
is not an atomic grant. Unknown ownership means blocked, not presumed free.

An approved ingress must bind autonomous primitive intent to current real
clearance and command-path approval. Do not fabricate a certificate or reroute
through manual control. No commands, poses, maps, heartbeat or safety state may
cross independent scene namespaces.

### Native safety and client liveness

Preserve native heartbeat, estop, explicit resume, key-release, focus-loss,
window-close, operator-timeout and physics guards. Native STOP and takeover must
win over all skills. A gateway must not create a competing heartbeat, disable
native idle/stop behavior, silently resume, or restore a cancelled request.

Each accepted operation needs an in-process monotonic deadline at the approved
runtime boundary. Client disconnect, missing client-liveness proof, gateway
failure, ownership loss, epoch change or safety-gate loss must terminate its
intent without waiting for the caller to cancel. Continuing native heartbeat
must not keep a lost skill client's gesture or continuous request alive.

No process may own a second physics loop or mutate the model from a gateway
callback. Ownership, cancellation and publication must be serialized so a late
nonzero command cannot follow STOP or an expired deadline.

### Continuous gates and acknowledgments

A future gateway may subscribe to `scene_status`, `control_status` and
`navigation_status`, recording local monotonic arrival times. Those streams can
support fail-closed checks; they do not grant ownership. `health()` polling must
not replace them.

Required checks include fresh permitted control state, robot readiness, no
estop/error, current episode and geometry identity, current real certificate,
command-path safety and no conflicting owner. For camera operation, loss of
tracking, pose or map evidence must block motion. No silent static/ground-truth
fallback is allowed. Recheck gates on every output cycle and on invalidation.
Do not reset remote evidence age when receiving it.

The runtime must acknowledge acceptance, ownership, deadline, cancellation and
stop separately from transport delivery. An SDK operation ID must be correlated
with the runtime grant. Without evidence, report an unconfirmed or unknown
outcome rather than physical success.

### Release, cancel and stop

Normal continuous completion releases only that request's owned channel. Base
release sends zero intent; lift release sends empty held actions. Neither implies
immediate physical stopping. Completing a base request must not erase another
owner's lift. Cancelling a gesture must not be faked by lift/jog/gripper input.

`cancel(id)` needs an atomic runtime revocation that prevents further outputs.
The current source has no gesture-only revocation route. Until approved support
exists, a gateway must reject unsupported cancellation semantics or document and
require an agreed global-stop policy. Do not report gesture cancellation merely
because local waiting ended.

`stop()` must stop local work and queued intent, invoke the approved global stop
route and await fresh acknowledgment where available. A disconnected backend
cannot confirm stop. Only explicit operator resume may unlatch stop; require
fresh resume acknowledgment before a new ownership grant. Do not auto-resume
on submit, retry, timeout or reconnect.

## Verification boundary

This document records a read-only source review. No live RPC, rendering, robot
motion or hardware verification was performed for it. Future deployment needs
integration tests for native takeover, focus loss, heartbeat loss, client loss,
planner conflicts, deadlines, stale evidence, reset epochs, cross-stream stop
ordering and late-output races. Measure live simulation pacing with rendering
active before making performance claims. Source availability and SDK unit tests
are not deployment evidence.
