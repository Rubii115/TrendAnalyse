from .trend import Trend
from .kline_client import Kline_client
from .timepoint import Timepoint
from copy import copy
from enum import property

class Analyse_area:
    def __init__(self, begin:Timepoint, end:Timepoint, kline_clt:Kline_client):
        if not begin < end:
            raise ValueError('begin must be less than end')
        self.begin = begin
        self.end = copy(begin)
        self.kline_client = kline_clt
        self._trendlist = []
        self.k_newest = self.kline_client.get_kline(self.begin)
        self.pumping = self.k_newest['open'] < self.k_newest['close']
        self.synchronize(end)

    def synchronize(self, new_time:Timepoint):
        while self.end < new_time:
            self.end.next()
            newkline = self.kline_client.get_kline(self.end)
            if newkline['high'] == newkline['low']:
                newkline['high'] += 0.01
            self.add_kline(newkline)
            

    def add_kline(self, kline):
        #当你调用这个函数的时候，end应该已经是新时间了。
        trend_to_add = Trend([])
        k_pre = self.k_newest
        k_now = kline
        if k_now['high'] > k_pre['high'] and k_now['low'] > k_pre['low']:
            self.pumping= True
            trend_to_add.set(begin_time=self.end.get_before(), 
                                end_time=self.end, 
                                begin_price=k_pre['low'], 
                                end_price=k_now['high'])
        elif k_now['high'] < k_pre['high'] and k_now['low'] < k_pre['low']:
            self.pumping = False
            trend_to_add.set(begin_time=self.end.get_before(), 
                                end_time=self.end, 
                                begin_price=k_pre['high'], 
                                end_price=k_now['low'])
        else:
            if self.pumping:
                trend_to_add.set(begin_time=self.end.get_before(), 
                                    end_time=self.end, 
                                    begin_price=k_pre['high'], 
                                    end_price=k_now['low'])
                self.pumping = False
            else:
                trend_to_add.set(begin_time=self.end.get_before(), 
                                    end_time=self.end, 
                                    begin_price=k_pre['low'], 
                                    end_price=k_now['high'])
                self.pumping = True
        self.k_newest = copy(k_now)
        trend_to_add.is_sure = True
        trend_to_add.break_price = trend_to_add.end_price
        self.add_trend(trend_to_add)

    def add_trend(self, trend_to_add: Trend):
        #按理说趋势合并应该有非常简洁的表达，但是这个函数如此丑陋的核心原因就是趋势可能不连贯，存在跳变
        #用了很多迭代，希望不要爆栈
        if len(self._trendlist) == 0:
            self._trendlist.append(trend_to_add)
            return
        backed_price = trend_to_add.begin_price
        new_price = trend_to_add.end_price
        #如果趋势与前一个趋势不连贯
        if trend_to_add.begin_price != self._trendlist[-1].end_price:
            #如果新趋势把前一个趋势的起始价格破了
            if (backed_price > self._trendlist[-1].begin_price)^self.pumping:
                self._trendlist[-1].is_sure = True
                #如果前一个趋势和前前个趋势也不连贯
                if len(self._trendlist) > 1 and self._trendlist[-1].begin_price != self._trendlist[-2].end_price:
                    self._trendlist[-1].set(begin_price=self._trendlist[-2].end_price , end_price=backed_price)
                    self.add_trend(trend_to_add)
                #或者前一个趋势和前前个趋势连贯
                elif len(self._trendlist) > 1 and self._trendlist[-1].begin_price == self._trendlist[-2].end_price:
                    #如果前一个趋势没把前前个趋势破了，就直接把前一个趋势加到前前趋势里
                    if (self._trendlist[-1].end_price > self._trendlist[-2].break_price)^self.pumping:
                        self._trendlist[-2].add_trendpair([self._trendlist[-1]],self._trendlist[-1].end_price,backed_price)
                        # self._trendlist[-2].include_list_add(self._trendlist[-1])
                        # self._trendlist[-2].set(end_price=backed_price)
                        new_trend = self._trendlist[-2]
                        self._trendlist.pop()
                        self._trendlist.pop()
                        self.pumping = not self.pumping
                        self.add_trend(new_trend)
                        self.pumping = not self.pumping
                        self.add_trend(trend_to_add)
                    else:
                        self._trendlist[-2].is_sure = True
                        new_trend = Trend([self._trendlist[-2],self._trendlist[-1]])
                        new_trend.set(begin_price=self._trendlist[-2].begin_price,end_price=backed_price)
                        new_trend.break_price = self._trendlist[-1].end_price
                        self._trendlist.pop()
                        self._trendlist.pop()
                        self.pumping = not self.pumping
                        self.add_trend(new_trend)
                        self.pumping = not self.pumping
                        self.add_trend(trend_to_add)
                elif len(self._trendlist) < 2:
                    if (backed_price > self._trendlist[-1].break_price)^self.pumping:
                        self._trendlist[-1].is_sure = True
                    self._trendlist.append(trend_to_add)
                else:
                    raise ValueError('add_trend position 1 error')
            #如果新趋势没超过前一个趋势的结束价格
            elif (new_price > self._trendlist[-1].end_price)^self.pumping:
                if (backed_price > self._trendlist[-1].break_price)^self.pumping:
                    self._trendlist[-1].is_sure = True
                self._trendlist.append(trend_to_add)
            else:
                #如果新趋势没破前一个趋势
                if (backed_price < self._trendlist[-1].break_price)^self.pumping:
                    self._trendlist[-1].add_trendpair([trend_to_add],backed_price,new_price)
                    new_trend = self._trendlist[-1]
                    self._trendlist.pop()
                    self.add_trend(new_trend)
                else:
                    self._trendlist[-1].is_sure = True
                    new_trend = Trend([self._trendlist[-1],trend_to_add])
                    new_trend.set(begin_price=self._trendlist[-1].begin_price,end_price=new_price)
                    new_trend.break_price = backed_price
                    self._trendlist.pop()
                    self.add_trend(new_trend)

        else:
            #如果前一个趋势和前前个趋势不连贯
            if len(self._trendlist) > 1 and self._trendlist[-1].begin_price != self._trendlist[-2].end_price:
                #如果新趋势破了前一个趋势的起始价格
                if (new_price < self._trendlist[-1].begin_price)^self.pumping:
                    self._trendlist[-1].is_sure = True
                    new_trend = Trend([self._trendlist[-1],trend_to_add])
                    new_trend.set(begin_price=self._trendlist[-2].end_price, end_price=new_price)
                    new_trend.break_price = backed_price
                    self._trendlist.pop()
                    self.add_trend(new_trend)
                else:
                    if (backed_price > self._trendlist[-1].break_price)^self.pumping:
                        self._trendlist[-1].is_sure = True
                    self._trendlist.append(trend_to_add)
            #如果前一个趋势和前前个趋势连贯
            elif len(self._trendlist) > 1 and self._trendlist[-1].begin_price == self._trendlist[-2].end_price:
                #如果新趋势没破前一个趋势的起始价格
                if (new_price > self._trendlist[-1].begin_price)^self.pumping:
                    trend_here = self.trendlist[-1]
                    while ((trend_here.break_price < new_price)^self.pumping 
                           and len(trend_here.include_list) != 0):
                        trend_here = trend_here.include_list[-1]
                    if not (trend_here.break_price < new_price)^self.pumping:
                        trend_here.is_sure = True
                    self._trendlist.append(trend_to_add)
                else:
                    self._trendlist[-1].is_sure = True
                    if ( backed_price > self._trendlist[-2].begin_price)^self.pumping:
                        self._trendlist.append(trend_to_add)
                    #如果前前个趋势已经被破了
                    elif (backed_price > self._trendlist[-2].break_price)^self.pumping:
                        self._trendlist[-2].is_sure = True
                        new_trend = Trend([self._trendlist[-2],self._trendlist[-1],trend_to_add])
                        new_trend.break_price = backed_price
                        self._trendlist.pop()
                        self._trendlist.pop()
                        self.add_trend(new_trend)
                    else:
                        self._trendlist[-2].add_trendpair([self._trendlist[-1],trend_to_add],backed_price,new_price)
                        new_trend = self._trendlist[-2]
                        self._trendlist.pop()
                        self._trendlist.pop()
                        self.add_trend(new_trend)
            elif len(self._trendlist) < 2:
                if (new_price < self._trendlist[-1].break_price)^self.pumping:
                    self._trendlist[-1].is_sure = True
                self._trendlist.append(trend_to_add)
            else:
                raise ValueError('add_trend position 2 error')
            
    @property
    def trendlist(self):
        return self._trendlist



        
            
    

                
                    
            