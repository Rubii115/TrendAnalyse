import pandas as pd
from .timepoint import Timepoint
from datetime import timedelta

class Kline_client:
    config = {
        'file_path': 'Candle_data/1mhistory_data.csv',
    }
    def __init__(self, config = None):
        if config is not None:
            self.config = config
        self.update()

    def update(self):
        # 更新k线数据
        df = pd.read_csv(self.config['file_path'])
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')
        df.set_index('date', inplace=True)
        self.df = df

    def get_kline(self, time:Timepoint):
        # 获取指定时间段的k线数据
        pdtime = time.get_pdtimepoint()
        _dict={}
        _dict['high'] = self.df.loc[pdtime]['high'].astype(float)
        _dict['low'] = self.df.loc[pdtime]['low'].astype(float)
        _dict['open'] = self.df.loc[pdtime]['open'].astype(float)
        _dict['close'] = self.df.loc[pdtime]['close'].astype(float)
        _dict['volume'] = self.df.loc[pdtime]['volume'].astype(float)
        return _dict
    
    def get_kline_list(self, begintime:Timepoint, endtime:Timepoint):
        # 获取指定时间段的k线数据列表
        begintime_pd = begintime.get_pdtimepoint()
        endtime_pd = endtime.get_pdtimepoint()
        df = self.df.loc[begintime_pd:endtime_pd + timedelta(minutes=1)]
        return df 