"""
Schemas for API Testing module
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum


class HTTPMethod(str, Enum):
    """HTTP methods for API testing"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class AuthType(str, Enum):
    """Authentication types"""
    NONE = "none"
    BEARER = "bearer"
    BASIC = "basic"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"


class TestStatus(str, Enum):
    """Test execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class APIEndpoint:
    """API endpoint definition"""
    url: str
    method: HTTPMethod
    description: Optional[str] = None
    required_params: Optional[List[str]] = None
    optional_params: Optional[List[str]] = None


@dataclass
class ValidationRule:
    """Validation rule for API responses"""
    field_path: str  # JSONPath to field
    rule_type: str  # equals, contains, regex, type, range
    expected_value: Any
    error_message: Optional[str] = None


@dataclass
class ExtractedValue:
    """Value extracted from API response"""
    name: str
    path: str  # JSONPath
    value: Any
    extracted_at: str


__all__ = [
    'HTTPMethod',
    'AuthType',
    'TestStatus',
    'APIEndpoint',
    'ValidationRule',
    'ExtractedValue'
]
