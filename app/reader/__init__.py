#!/usr/bin/env python3

class ReaderException(Exception):
    def __init__(self, message, operation):
        self.message = message
        self.operation = operation
