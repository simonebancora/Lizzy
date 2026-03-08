class LizzyError(Exception):
    """Base exception for all Lizzy errors."""


class StateError(LizzyError):
    """Method called in wrong model state (pre-init vs post-init)."""


class ConfigurationError(LizzyError):
    """Missing or invalid setup: unassigned resin, duplicate names, multiple vents, etc."""


class MeshError(LizzyError):
    """Mesh-related error: missing physical tag, unassigned element material."""
