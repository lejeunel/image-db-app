#!/usr/bin/env python3

class UpdateMixin:
    def update(self, data:dict):
        for key,value in data.items():
            setattr(self,key,value)
