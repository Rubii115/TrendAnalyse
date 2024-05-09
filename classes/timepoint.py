import pandas as pd
from datetime import timedelta
from copy import copy, deepcopy

class Timepoint:
    def __init__(self, year, month, day, hour, minute):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
         
    def get_pdtimepoint(self):
        return pd.to_datetime(f"{self.year}-{self.month}-{self.day} {self.hour}:{self.minute}", format="%Y-%m-%d %H:%M")
    
    def previous(self, delta = 1):
        current_time = self.get_pdtimepoint()
        one_minute_before = current_time - timedelta(minutes=delta)
        self.year = one_minute_before.year
        self.month = one_minute_before.month
        self.day = one_minute_before.day
        self.hour = one_minute_before.hour
        self.minute = one_minute_before.minute
    
    def next(self, delta = 1):
        current_time = self.get_pdtimepoint()
        one_minute_after = current_time + timedelta(minutes=delta)
        self.year = one_minute_after.year
        self.month = one_minute_after.month
        self.day = one_minute_after.day
        self.hour = one_minute_after.hour
        self.minute = one_minute_after.minute

    def get_before(self, delta = 1):
        tp_copy = copy(self)
        tp_copy.previous(delta)
        return tp_copy
    
    def get_after(self, delta = 1):
        tp_copy = copy(self)
        tp_copy.next(delta)
        return tp_copy

    def __eq__(self, value: object) -> bool:
        return self.get_pdtimepoint() == value.get_pdtimepoint()
    
    def __lt__(self, value: object) -> bool:
        return self.get_pdtimepoint() < value.get_pdtimepoint()
    
    def __gt__(self, value: object) -> bool:
        return self.get_pdtimepoint() > value.get_pdtimepoint()

    def __str__(self) -> str:
        return f"{self.year:0>4}-{self.month:0>2}-{self.day:0>2} {self.hour:0>2}:{self.minute:0>2}"
    
    def __copy__(self):
        return Timepoint(self.year, self.month, self.day, self.hour, self.minute)
    
    def __deepcopy__(self, memo):
        return Timepoint(self.year, self.month, self.day, self.hour, self.minute)
    
    def __le__(self, value: object) -> bool:
        return self.get_pdtimepoint() <= value.get_pdtimepoint()
    
    def __ge__(self, value: object) -> bool:
        return self.get_pdtimepoint() >= value.get_pdtimepoint()
