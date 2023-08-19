#!/usr/bin/env python3
from abc import ABC, abstractmethod
from urllib.parse import urlparse
from app.exceptions import ParsingException
import functools

class BaseReader:

    @abstractmethod
    def __call__(self, uri) -> bytes:
        pass

    @abstractmethod
    def list(self, uri) -> list[str]:
        pass
