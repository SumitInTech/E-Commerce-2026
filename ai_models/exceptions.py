"""
Self-contained Domain Exceptions for AI Models.
"""

class ModelException(Exception):
    """Base exception for all AI model errors."""
    pass

class ModelArtifactNotFoundException(ModelException):
    """Raised when model weights or metadata artifacts are missing."""
    pass

class InvalidSilhouetteException(ModelException):
    """Raised when uploaded silhouette masks fail biomechanical validation."""
    pass

class IngestionException(ModelException):
    """Raised when vector knowledge base ingestion fails."""
    pass
