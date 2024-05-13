import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY
import mplfinance as mpf
from matplotlib.patches import FancyArrowPatch
import pandas as pd
import numpy as np

from .trend import Trend
from .kline_client import Kline_client
from .timepoint import Timepoint
from .analyse_area import Analyse_area

class Plot_driver:
    def __init__(self, kline_clt: Kline_client, config=None):
        self.kline_client = kline_clt
        self.config = config

    def draw(self, area : Analyse_area ,range_index = None, layer = 3):
        if range_index is None:
            range_index = (0,len(area.trendlist))
        elif len(range_index) == 1:
            range_index = (range_index[0],len(area.trendlist))

        self.kdata = self.kline_client.get_kline_list(area.trendlist[range_index[0]].begin_time, 
                                                      area.trendlist[range_index[1]-1].end_time)
        df = self.kdata.copy()

        cmap_sure = plt.get_cmap('Blues')
        cmap_notsure = plt.get_cmap('Reds')
        colors = [[cmap_notsure(i) for i in np.linspace(0.8/layer, 0.8, layer)],
                  [cmap_sure(i) for i in np.linspace(0.8/layer, 0.8, layer)]]

        # 希望迭代不要爆栈
        # 列出需要画的趋势以及子趋势的线段端点和颜色
        def getsegs_from_trend(trend,layer_num):
            if layer_num < 1:
                return [],[]
            seglist = []
            colorlist = []
            for item in trend.include_list:
                segitem, coloritem = getsegs_from_trend(item, layer_num - 1)
                seglist = seglist + segitem
                colorlist = colorlist + coloritem
            seglist = seglist + \
                [[(trend.begin_time.get_pdtimepoint(), trend.begin_price),(trend.end_time.get_pdtimepoint(), trend.end_price)]]
            colorlist = colorlist + \
                [colors[trend.is_sure][layer_num-1]]
            return seglist, colorlist
        
        seglist = []
        colorlist = []
        
        for trend in area.trendlist[range_index[0]:range_index[1]]:
            segitem, coloritem = getsegs_from_trend(trend, layer)
            seglist = seglist + segitem
            colorlist = colorlist + coloritem

        mpf.plot(df, 
                 type='candle', 
                 volume = True,
                 alines=dict(alines=seglist,
                     colors=colorlist,
                     linewidths=1)
                     )



