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

class Feb_line():
    def __init__(self, minchange = 0.01):
        self.minchange = minchange
    def name(self):
        return 'Feb_line'