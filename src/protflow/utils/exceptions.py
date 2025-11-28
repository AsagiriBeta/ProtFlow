"""
Exception classes for ProtFlow pipeline.
"""


class ProtFlowError(Exception):
    """Base exception for ProtFlow errors."""
    pass


class ConfigurationError(ProtFlowError):
    """Raised when there's a configuration error."""
    pass


class DependencyError(ProtFlowError):
    """Raised when a required dependency is missing."""
    pass


class ModelLoadError(ProtFlowError):
    """Raised when model loading fails."""
    pass


class PredictionError(ProtFlowError):
    """Raised when structure prediction fails."""
    pass


class PocketDetectionError(ProtFlowError):
    """Raised when pocket detection fails."""
    pass


class DockingError(ProtFlowError):
    """Raised when docking fails."""
    pass


class LigandPreparationError(ProtFlowError):
    """Raised when ligand preparation fails."""
    pass


class ParseError(ProtFlowError):
    """Raised when parsing GenBank files fails."""
    pass


class AntiSMASHError(ProtFlowError):
    """Raised when antiSMASH execution fails."""
    pass

