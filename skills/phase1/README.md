# Phase 1 skill family definition

## Purpose

Expose basic Kural commands through one small callable Python interface and a
structured CLI. Support bounded robot-local base motion, timed lift up/down,
and existing named gestures. Humans and agents share the same canonical catalog
and validation. This is not task planning or autonomous navigation.

## Status

Implemented callable-layer contract; dry run is the default execution mode.
No live DIMOS adapter, simulation-execution verification, or hardware verification
is claimed here. Tests of validation or fake gateways are not robot tests.
The external approved gateway remains a prerequisite for any live integration.
See [Phase 1 API documentation](../../docs/PHASE1.md) for usage and limits.

## Skills and inputs

Canonical names come from `src/kural_skills/catalog.py`:

- Base: `move_forward`, `move_backward`, `move_left`, `move_right`, `steer_left`,
  `steer_right`, `steer_back_left`, `steer_back_right`, `turn_left`, `turn_right`,
  `base_velocity`.
- Lift: `lift_up`, `lift_down`.
- Gestures: `home`, `wave`, `point`, `inspect`, `stow`.

Base/lift commands take positive `duration_s` (default 1, maximum 10 seconds).
Directional base translation uses positive `speed_m_s` (default 0.1, maximum 0.2).
Named steering/turning uses positive yaw magnitude `yaw_rate_rad_s`
(default 0.3, maximum 0.5). `base_velocity` instead takes signed `vx_m_s`,
`vy_m_s`, and `yaw_rate_rad_s`, with maxima 0.2 m/s per linear component,
combined linear magnitude at most 0.2 m/s, and yaw magnitude at most 0.5 rad/s.
Gestures take positive `timeout_s` (default 20, maximum 30 seconds).

Values must be finite numbers, not booleans. Unknown names and extra parameters
are rejected. Discovery methods expose each skill's applicable parameters.
No lift height, object target, gesture pose, or perception input is accepted.

## Output

`call()` and family methods return `SkillResult`. `start()` returns an `Action`
for status, wait, and cancel. Structured results include `operation_id`, `skill`,
`state`, `reason`, `request`, `evidence`, `motion_verified`, and `stop_confirmed`.
The last two flags remain false throughout Phase 1.

A dry run ends in `dry_run`, not physical success. Other terminal states are
`command_finished`, `gesture_finished`, `blocked`, `cancelled`, `failed`, and
`outcome_unknown`. Nonterminal states are `accepted`, `running`, and
`cancel_requested`. Reported completion is not proof of movement, arrival,
pose, or stop. Consult the reason and backend evidence without overstating it.

## Requirements

For dry run:

- Python 3.11 or newer and this package.
- No simulator, model credentials, robot connection, or additional SDK is needed.

For a future live integration:

- An explicitly supplied and approved gateway with `submit/status/cancel/stop`.
- The authoritative robot controls and named gestures, not duplicate model code.
- Existing motion arbitration, operator takeover, stop/estop, command freshness,
  and applicable clearance checks, retained end to end.
- Measured completion and stop evidence, with real integration tests.

`GatewayBackend` is not a deployed gateway or current DIMOS connection.
This package must not write control state directly or publish around safety
checks. The sole robot model authority remains
`/home/josh/Desktop/Kural/kural_description`.

## Behavior and completion

1. Resolve the canonical skill and validate parameters.
2. Build a normalized request from the fixed direction or named-action mapping.
3. Submit it to the selected backend. The default backend only describes it.
4. Report state and reason through the same result format.
5. Preserve unknown or blocked outcomes instead of inventing successful motion.

The robot frame is +X forward, +Y left, +yaw heading-left. Reverse steering uses
heading yaw, not car wheel angle: `steer_back_left` combines -X and +yaw;
`steer_back_right` combines -X and -yaw. It does not name rearward path direction.
Lift requests reuse `liftUp`/`liftDown`. Gestures reuse existing authored names;
this repository does not author new joint poses.

Timed motion is not a distance goal. A gesture deadline is not a completion
signal. Dry-run completion is only request validation and representation.

## Safety, cancellation, and failure

- Default to dry run. Do not silently connect to a running robot or simulator.
- Keep command interval, wait timeout, transport timeout, and freshness separate.
- Request cancellation through the operation; request global stop through `stop()`.
- Do not interpret `cancelled` as physically confirmed stopped.
- Do not interpret a caller wait timeout as confirmed robot cancellation.
- On a blocked, failed, or unknown outcome, read the reason. Do not automatically
  retry, resume, or restore an earlier command.
- Preserve operator and safety decisions; never resume around a latched stop.
- Validation limits are not calibrated hardware safety limits or a clearance
  certificate. Dry run cannot check obstacles or confirm mechanical travel.

No depth, perception, mapping, or live-navigation change is part of this family.

## Verification requirements

Callable-layer tests should cover:

- Every canonical skill and its discovery/schema entry.
- Robot-frame direction signs, especially both reverse-steering cases.
- Unit and parameter bounds, combined linear-speed bound, nonfinite numbers,
  booleans, unknown names, and unsupported parameters.
- Default dry-run isolation: no simulator imports, robot connection, or motion.
- Python and CLI requests using the same catalog and normalized results.
- Action lifecycle, timeout, cancellation, stop, and gateway error reporting
  with a fake gateway, explicitly labeled as nonphysical tests.
- Every result retaining false physical-verification flags.

Live verification is blocked until the gateway is approved. Before claiming
integration, measure arbitration, operator takeover, command freshness,
applicable clearance checks, cancellation, stop, reset/epoch handling, and
actual completion. Record environment, gateway version, test commands, measured
evidence, failures, and remaining limits. Hardware verification is separate
from simulation verification and needs its own calibration and tests.

This document defines expected checks; it does not assert they already passed.
See [official SDK references](../../docs/SDK-INSPIRATION.md) for design patterns,
not compatibility or live-execution evidence.
