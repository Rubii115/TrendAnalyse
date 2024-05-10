from enum import property
from .timepoint import Timepoint
from copy import copy, deepcopy

class Trend:
    max_back = 0.236
    def __init__(self, trends):
        self._include_list = []
        self._father_trend = None
        self.break_price = None
        self._is_sure = False
        if len(trends) == 0:
            return
        self._begin_time = copy(trends[0].begin_time)
        self._begin_price = trends[0].begin_price
        self._end_time = copy(trends[0].end_time)
        self.break_price = trends[-1].begin_price
        self._include_list.append(trends[0])
        for i in range(1,len(trends)):
            self.include_list_add(trends[i])

    def set(self,begin_time:Timepoint = None, end_time:Timepoint = None, begin_price = None, end_price = None):
        if begin_time is not None:
            self._begin_time = copy(begin_time)
        if end_time is not None:
            self._end_time = copy(end_time)
            if self.father_trend is not None:
                self.father_trend.set(end_time = end_time)
        if begin_price is not None:
            self._begin_price = begin_price
        if end_price is not None:
            self._end_price = end_price
            if ((self.break_price - self._begin_price)/(self._end_price - self._begin_price) < self.max_back
                and len(self.include_list) > 1
                and self._end_price == self._include_list[-1].end_price):
                self._include_list[-1].kill()
            if self.father_trend is not None:
                self.father_trend.set(end_price = end_price)

    def include_list_add(self, item):
        if item == self:
            raise Exception("trend include list add error: add self")
        if self.is_sure:
            raise Exception("trend is sure, can not add")
        if len(self._include_list) == 0:
            self._include_list = [item]
            item.father_trend = self
            self._begin_price=item.begin_price
            self._begin_time=copy(item.begin_time)
            self._end_price=item.end_price
            self._end_time=copy(item.end_time)
        elif item.begin_time == self.end_time:
            self._include_list.append(item)
            item.father_trend = self
            self.set(end_time=item.end_time,
                     end_price=item.end_price)
        elif item.end_time == self.begin_time:
            self._include_list.insert(0,item)
            item.father_trend = self
            self._begin_time = item.begin_time
            self._begin_price = item.begin_price
        else:
            print(self.end_time)
            print(item.begin_time)
            raise Exception("trend include list add error")
        

    def add_trendpair(self, trends, backed, new, pump, blankTrend):
        #先判断趋势对有没有继承自己的趋势:
        is_continue = (new < self.end_price)^pump
        #然后判断自己哪个子趋势被破了
        consider_trend = self
        while (pump^(backed < consider_trend.break_price)
               and consider_trend.is_sure == False):
            consider_trend = consider_trend.include_list[-1]
        consider_trend.is_sure = True
        if (is_continue and 
            consider_trend.father_trend is not None):
            consider_trend.father_trend.break_price = backed
            for item in trends:
                consider_trend.father_trend.include_list_add(item)
            consider_trend.father_trend.set(end_price=new)
            return self
        elif (is_continue and 
            consider_trend.father_trend is None):
            blankTrend.include_list_add(self)
            blankTrend.break_price = backed
            for item in trends:
                blankTrend.include_list_add(item)
            blankTrend.set(end_price = new)
            return blankTrend
        elif not is_continue:
            return None
        else:
            raise Exception("trend add trendpair error")
            

    def kill(self):
        if len(self._include_list) == 0:
            return
        self.father_trend.include_list_pop()
        self.father_trend.break_price = self.break_price
        for item in self._include_list:
            self.father_trend.include_list_add(item)
        self.father_trend.set(end_price = self.end_price)

    def include_list_pop(self):
        self._include_list.pop()
        self.set(end_price=self._include_list[-1].end_price,
                 end_time=self._include_list[-1].end_time)
        
    def is_sure_confirm(self,backed,pump):
        consider_trend = self
        while (pump^(backed > consider_trend.break_price)
               and consider_trend.is_sure == False):
            consider_trend = consider_trend._include_list[-1]
        consider_trend.is_sure = True

    
    @property
    def begin_time(self):
        return self._begin_time
    
    @property
    def end_time(self):
        return self._end_time
    
    @property
    def begin_price(self):
        return self._begin_price
    
    @property
    def end_price(self):
        return self._end_price
    
    @property
    def include_list(self):
        return self._include_list

    @property
    def father_trend(self):
        return self._father_trend
    
    @father_trend.setter
    def father_trend(self, trend):
        self._father_trend = trend
    
    @property
    def is_sure(self):
        return self._is_sure
    
    @is_sure.setter
    def is_sure(self, is_sure):
        self._is_sure = is_sure
        for item in self._include_list:
            item.is_sure = True
    
    
    
    def __str__(self) -> str:
        return f"{self._begin_time} to {self._end_time}, {self._begin_price} to {self._end_price}"
