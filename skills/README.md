# Skills

[Phase 1](phase1/README.md) defines basic base movement, lift actions, and the
existing named gestures. Its Python/CLI callable layer is implemented; execution
is dry-run only until a reviewed robot gateway is integrated.

New skills get one directory per skill or coherent family. Define purpose,
inputs/outputs, prerequisites, behavior, cancellation/failure, verification,
and status before adding implementation. Reuse the shared SDK dispatcher.
