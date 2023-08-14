#!/usr/bin/env python3
from abc import ABC, abstractmethod

class BaseReader:

    @abstractmethod
    def __call__(self, uri):
        pass

    @abstractmethod
    def list(self, uri) -> list:
        pass
