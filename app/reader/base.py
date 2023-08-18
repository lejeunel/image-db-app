#!/usr/bin/env python3
from abc import ABC, abstractmethod
from urllib.parse import urlparse
from app.exceptions import ParsingException
import functools

def validate_uri():
    """
    Decorator that validate an URI for a given BaseReader.
    The latter must define attribute self.allowed_schemes
    """
    def decorator(function):
        @functools.wraps(function)
        def wrapper(self, uri):
            if uri[-1] != "/":
                raise ParsingException(
                    message="Provided URI must end with '/'",
                    payload={"operation": "list location"},
                )

            scheme = urlparse(uri).scheme
            if not hasattr(self, "allowed_schemes"):
                pass

            elif scheme not in self.allowed_schemes:
                raise ParsingException(
                    message=f"Provided scheme \"{scheme}\" in URI {uri} not supported",
                    payload={"operation": "list location"},
                )

            return function(self, uri)
        return wrapper
    return decorator


class BaseReader:

    @abstractmethod
    def __call__(self, uri) -> bytes:
        pass

    @abstractmethod
    def list(self, uri) -> list[str]:
        pass
