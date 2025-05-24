"""
Error Response Models
Provides consistent error response schemas for the API
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class ErrorDetail(BaseModel):
    """Individual error detail"""
    field: Optional[str] = None
    message: str
    type: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response format"""
    error_code: str
    message: str
    details: Optional[List[ErrorDetail]] = None
    request_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "error_code": "RESOURCE_NOT_FOUND",
                "message": "The requested resource was not found",
                "details": [
                    {
                        "field": "client_id",
                        "message": "Client with this ID does not exist",
                        "type": "not_found"
                    }
                ],
                "request_id": "req_123456"
            }
        }


class ValidationErrorResponse(BaseModel):
    """Validation error response format"""
    error_code: str = "VALIDATION_ERROR"
    message: str = "Invalid input data"
    errors: List[Dict[str, Any]]
    
    class Config:
        json_schema_extra = {
            "example": {
                "error_code": "VALIDATION_ERROR",
                "message": "Invalid input data",
                "errors": [
                    {
                        "loc": ["body", "age"],
                        "msg": "ensure this value is greater than or equal to 1",
                        "type": "value_error.number.not_ge"
                    }
                ]
            }
        }


# Standard error codes
class ErrorCode:
    """Standard error codes used across the application"""
    # Client errors (4xx)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    DUPLICATE_RESOURCE = "DUPLICATE_RESOURCE"
    
    # Server errors (5xx)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
