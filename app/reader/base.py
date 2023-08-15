#!/usr/bin/env python3
from abc import ABC, abstractmethod

class BaseReader:

    @abstractmethod
    def __call__(self, uri) -> bytes:
        pass

    @abstractmethod
    def list(self, uri) -> list[str]:
        pass
