# Official SDK inspiration

These public Python SDKs informed the small callable interface. Their source was
read over HTTPS. No SDK was installed or integrated for this research.
These are design references, **not SDK compatibility claims**. No one example
covers all of Kural's mechanics or supplies its required safety gateway.

## DJI RoboMaster SDK: holonomic velocity and action records

Official sources:

- [Chassis](https://github.com/dji-sdk/RoboMaster-SDK/blob/master/src/robomaster/chassis.py)
- [Action](https://github.com/dji-sdk/RoboMaster-SDK/blob/master/src/robomaster/action.py)

`chassis.drive_speed(x, y, z, timeout)` takes forward and strafe speeds in m/s
and yaw in **degrees/s**. The timeout starts a local auto-stop timer.
`chassis.move(...)` returns an `Action` with state, running/completion flags,
success/failure flags, a failure reason, and `wait_for_completed(timeout)`.
Chassis status and velocity can be subscribed to separately.

Useful patterns: explicit velocity axes; bounded command lifetime; a small
action record separate from the robot object; structured failure detail.

Limits: there is no vertical lift in this reference. A wait timeout is not a
motion-duration contract or confirmed cancellation. The inspected private
`Action._abort()` changes local action state; it does not establish a public
physical cancellation guarantee. `chassis.stop()` performs lifecycle cleanup;
explicit zero velocity is the motion-stop pattern in the speed interface.
Kural uses rad/s, so units must not be copied blindly.

## Hello Robot Stretch Body: lift, shared callable controls, status

Official sources:

- [Robot lifecycle, status, stow, and command dispatch](https://github.com/hello-robot/stretch_body/blob/master/body/stretch_body/robot.py)
- [Base velocity](https://github.com/hello-robot/stretch_body/blob/master/body/stretch_body/base.py)
- [Prismatic joint methods inherited by lift](https://github.com/hello-robot/stretch_body/blob/master/body/stretch_body/prismatic_joint.py)
- [Lift class](https://github.com/hello-robot/stretch_body/blob/master/body/stretch_body/lift.py)
- [Keyboard CLI](https://github.com/hello-robot/stretch_body/blob/master/tools/bin/stretch_robot_keyboard_teleop.py)

`robot.base.set_velocity(v_m, w_r)` uses m/s and rad/s on a differential base.
It does **not** support strafe. The lift inherits `move_to`, `move_by`, and
`set_velocity`, with explicit units, calibration checks, and soft limits.
Commands are queued and sent with `robot.push_command()`.
`robot.wait_command(timeout)` returns a completion boolean.
`robot.get_status()` returns a thread-safe dict. `robot.stow()` is a named,
blocking coordinated action.

Useful patterns: a small `robot.base` / `robot.lift` interface; normalized units;
explicit startup and dispatch; human keyboard controls calling the same methods;
structured status separate from pretty printing.

Limits: this is different hardware and control infrastructure. Kural's timed
lift API does not imply Stretch's calibrated height control. Stretch's
`stop_trajectory()` concerns waypoint trajectories; it is not evidence of a
blanket cancellation API. The keyboard example is not an agent JSON CLI.

## Unitree SDK2 Python: named actions and a small velocity call

Official sources:

- [Go2 SportClient](https://github.com/unitreerobotics/unitree_sdk2_python/blob/master/unitree_sdk2py/go2/sport/sport_client.py)
- [Human CLI example](https://github.com/unitreerobotics/unitree_sdk2_python/blob/master/example/go2/high_level/go2_sport_client.py)

`SportClient.Move(vx, vy, vyaw)` accepts three velocity components.
`StopMove()` is a separate locomotion command. Named methods include `Hello()`,
`Stretch()`, `Dance1()`, `Dance2()`, `Sit()`, and `StandUp()`. These map to API IDs
and JSON request parameters. The official CLI dispatches a name or numeric ID
to the same methods.

Useful patterns: named-action allowlist; simple velocity method; one callable
API reused by a thin human interface; transport return codes kept explicit.

Limits: `Move` uses `_CallNoReply`; its return code is not completion evidence.
`SetTimeout(10.0)` is an RPC timeout, not a command duration. `StopMove()` does
not prove that every named gesture can be cancelled. There is no manipulator
lift here. The interactive example is not a robust agent operation protocol.

## What Phase 1 takes, and what it does not

Phase 1 uses simple family methods, canonical skill names, explicit units,
parameter schemas, and structured operation records. Humans and agents use the
same validation rather than separate motion implementations.

It does not reuse these robots' poses, limits, models, transport, or safety
assumptions. Duration, wait timeout, transport timeout, and freshness are distinct.
A cancellation request must not be described as a measured stop. A backend
completion report must not be described as physical task success.
The default dry run makes these limits explicit while live integration remains
blocked on an approved gateway and integration evidence.
