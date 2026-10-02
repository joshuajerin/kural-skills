# Agent contribution guide

## Purpose

Build a clear, small foundation for Kural robot skills. The initial repository
contains documentation only; do not assume any skill or runtime integration
already exists.

## Working rules

- Read the root README and the relevant skill definition before changing code.
- Define purpose, inputs/outputs, prerequisites, cancellation, failure handling,
  and verification before implementing a skill.
- Keep changes focused. Do not introduce a framework, dependencies, or runtime
  integration without an agreed need.
- Keep robot geometry and URDF/MJCF authority in `kural_description` in the Kural
  robot repository. Do not copy or invent a second robot model here.
- Use approved robot-control interfaces. Never bypass arbitration, stop/estop,
  operator takeover, or perception/clearance checks to make a skill succeed.
- Treat simulation truth as evaluation evidence, not a replacement for sensor
  inputs to a behavior.
- Distinguish proposed behavior, source code, test results, simulation execution,
  and hardware verification. Record failures and limitations.
- Do not start live robot motion or modify other repositories without permission.
- Keep secrets, downloaded models/assets, and recordings out of Git.
