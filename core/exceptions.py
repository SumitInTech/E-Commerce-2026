"""
Domain-specific exceptions and error handling abstractions.
"""
from fastapi import HTTPException, status


class AnthropometricException(Exception):
    """Base exception for all anthropometric domain errors."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class InvalidSilhouetteException(AnthropometricException):
    """Raised when an uploaded mask or image does not contain a valid full-body human silhouette."""
    pass


class ModelArtifactNotFoundException(AnthropometricException):
    """Raised when serialized model weights or scalers are missing."""
    pass


class RAGInferenceException(AnthropometricException):
    """Raised when the vector retrieval or LLM generation fails."""
    pass


def map_domain_exception_to_http(exc: AnthropometricException) -> HTTPException:
    """Maps domain exceptions to standard HTTP error responses."""
    if isinstance(exc, InvalidSilhouetteException):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error_code": "INVALID_SILHOUETTE", "message": exc.message}
        )
    if isinstance(exc, ModelArtifactNotFoundException):
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error_code": "MODEL_UNAVAILABLE", "message": exc.message}
        )
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={"error_code": "INTERNAL_SERVER_ERROR", "message": str(exc)}
    )
