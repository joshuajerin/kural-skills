# kural-skills

A small callable skill library for Kural. Developers, humans, and AI agents use
one set of commands and build more useful behaviors on top.

## Phase 1

- **Base:** forward, backward, left/right strafe, forward/reverse steering.
- **Extras:** left/right turns in place and bounded base velocity.
- **Lift:** up and down using the existing authored actions.
- **Gestures:** home, wave, point, inspect, and stow.
- **Interfaces:** Python SDK, JSON CLI, agent tool schemas, and a JSON-lines session.
- **Actions:** operation IDs, status, cancellation, deadlines, and stop requests.

**Status:** the callable layer is implemented and unit-tested. It defaults to
**dry run** and does not move the robot. Live runtime integration is not yet
implemented or verified. The current native UI and independent skill publishers
would race; a reviewed single-owner gateway is required, not direct stream writes.

## Start

```sh
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python -e .
.venv/bin/kural-skills list
.venv/bin/kural-skills call move_forward --params '{"duration_s": 1, "speed_m_s": 0.1}'
```

```python
from kural_skills import KuralSkills

with KuralSkills() as robot:  # Dry run: no robot connection.
    robot.base.forward(duration_s=1.0, speed_m_s=0.1)
    robot.base.steer_back_right(duration_s=1.0, yaw_rate_rad_s=0.2)
    robot.lift.up(duration_s=0.5)
    result = robot.gestures.wave()
    print(result.as_dict())
```

Left/right mean **strafe**. Steering means translation plus a heading turn.
Reverse steering names refer to heading yaw, not a car steering-wheel angle.
Velocities use m/s and rad/s. Timed commands are not distance or arrival goals.

## For agents

`kural-skills tools` returns function schemas. `kural-skills serve` accepts one
JSON request per line. Both use the same catalog and validation as Python.

```json
{"id": 1, "method": "call", "skill": "lift_up", "params": {"duration_s": 0.5}}
```

Responses state what happened. A dry run is never reported as physical success.
No API silently resumes an estop or retries uncertain movement.

## For developers

- `src/kural_skills/` — catalog, validation, SDK, backends, and CLI.
- `skills/phase1/` — the skill definition and verification requirements.
- `tests/` — standard-library tests; no robot environment needed.
- `AGENTS.md` — contribution rules for agents.

Run tests from the repository root:

```sh
.venv/bin/python -m unittest discover -s tests -v
```

The robot description, URDF/MJCF, meshes, controller, and authored gesture
keyframes remain in Kural's `kural_description` package. This repo does not create
a second robot model. Large assets, recordings, and secrets stay outside Git.

Read [Phase 1 usage](docs/PHASE1.md), [runtime integration requirements](docs/RUNTIME-CONTRACT.md),
[SDK inspiration](docs/SDK-INSPIRATION.md), and [verification](docs/VERIFICATION.md).
For the new ChatGPT Plugins platform, see [AI-agent integration research](docs/AI-AGENT-INTEGRATIONS.md).
For the actual Grok Bot, see [exact Grok tools and integrations](docs/GROK-TOOLS-INTEGRATIONS.md).
[Exa setup](docs/EXA-SETUP.md) records verified search access in the agent environment.
New skills start with a definition: purpose, inputs/outputs, prerequisites,
behavior, cancellation/failure, tests, and an honest status. Add code in small,
reviewable steps.
