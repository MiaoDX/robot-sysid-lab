"""Compatibility shim for the canonical :mod:`sysid_lab` L0 implementation."""

from sysid_lab.l0_inertia_damping import *
from sysid_lab.l0_inertia_damping import (
    _run_least_squares,
    _validate_bounds,
    main,
)

if __name__ == "__main__":
    raise SystemExit(main())
