# kural-skills

A home for the skills that give Kural useful things to do.

We will use this repository to define robot behaviors, implement them, and record
how they are tested. It is a small starting base for developers and AI agents to
build on together.

## What we are going to do

- Describe each skill clearly before implementing it.
- Define its inputs, outputs, requirements, and expected behavior.
- Add implementations and tests in small, reviewable steps.
- Keep track of what is proposed, implemented, and actually verified.

**Current status:** repository foundation only. No robot skills are implemented
or connected to a runtime yet. The first skills and their interfaces will be
defined next.

## What belongs here

Skill definitions, behavior code, tests, and usage documentation.

The robot model, URDF/MJCF, meshes, simulator, and robot-control infrastructure
remain in the Kural robot repository. This repository builds on those systems;
it does not create a second robot model or replace their safety controls.

Here, a *skill* means a robot behavior—not an agent-tool installation format.
The initial definitions do not require a particular framework or runtime.

## Starting structure

- `skills/` — skill definitions and, later, their implementations and tests.
- `AGENTS.md` — instructions for agents contributing to this repository.

## Adding a skill

Start with `skills/<skill-name>/README.md`. Describe:

1. **Purpose:** what the robot should accomplish.
2. **Inputs and outputs:** what the skill receives and returns.
3. **Requirements:** required capabilities, sensors, and runtime interfaces.
4. **Behavior:** steps, completion conditions, and limits.
5. **Safety and failure:** conditions that prevent execution, stop/cancel behavior,
   and what happens when information is missing or execution fails.
6. **Verification:** tests, expected results, and evidence of actual execution.
7. **Status:** proposed, implemented, simulation-verified, or hardware-verified.

Keep definitions small and explicit. Do not claim a skill works just because its
code exists. Agree on the required robot interfaces before wiring it into a
runtime.

## Working together

Developers and agents follow the same rules: make focused changes, document
assumptions, preserve robot safety controls, and report what was tested honestly.
Large assets, models, recordings, and secrets stay outside this repository.
