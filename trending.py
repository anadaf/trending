"""
Calculating trending items

- Author: Ali Nadaf
------------------------
The code spots the trending items for a given time period. Below I explain that how trendiness is determined.

Trendiness: Item is a trending item when it is mentioned (purchased, cliked, viewed,etc) more often than usual. 

Algorithm: rolling Z-score
This is the standard algorithm to find trending items and is simple to implement:

z=(x-\mu)/\sigma,

where \mu is the history mean and \sigme is the standard deviation of the history data. In the following code, for every point,
the above formula is re-applied with a decay factor so that the oldest points carry the less factor value. 

When a z-score is used, the higher or lower the z-score the more abnormal the trend, so for example if the z-score is highly
 positive then the trend is abnormally rising, while if it is highly negative it is abnormally falling. Hence, the z-score
  for all the candidate trends the highest 10 z-scores will relate to the most abnormally increasing z-scores.
  
Note:
    * You can user this trending method with a sliding window, for instance last 10-day transaction, if you wish to use the 
    recent transaction and not take much historical data into account. This can be done by cutting down on the transaction time 
    of the original data.
 
 """
# import libraries
from math import sqrt
import numpy as np
from seasonal import fit_seasons,adjust_seasons
import matplotlib.pyplot as plt
import pandas as pd
import datetime

"""
Trend class:
**parameters**
- inputs: 
    data: Database file path
    column: The field of the database for determining trending
"""


class trend():
    def __init__(self,decay=0.1,interval_days=7):
        self.max_length=None
        self.decay=decay
        self.int_days=interval_days

    def load_data(self,data,item_col='item_id',user_col='user_id',interaction_time='interaction_time'
                 ,interaction_type='interaction_type'):
        data = pd.read_csv(data)
        data[interaction_time]=pd.to_datetime(data[interaction_time])
        data = data.sort_values([interaction_time])
        today = pd.datetime.now()
        data['diff']=(((data[interaction_time] - pd.datetime.now().date()).dt.days) / self.int_days).astype(int)
        self.max_length = -data['diff'].min()
        df_group = data.groupby([item_col, 'diff'])[user_col].count().reset_index(name='user_count')
        self.item_list = df_group[item_col].unique()
        df_group.rename(columns={'diff': 'lag'}, inplace=True)
        self.data = df_group


    def calc(self):
        """
        Calculating the trending score for all items
        :return: trending scores table
        """
        df_trend = []
        for item in self.item_list:
            _score = self.zvalue(self.data, item, length=self.max_length)
            df_trend.append({'item': item, 'trending_score': _score})
        df_trend = pd.DataFrame(df_trend)
        df_trend = df_trend.sort_values("trending_score", ascending=False)
        return df_trend

    def zvalue(self,df,item,length):
        """
        Determining z_score value for the given item
        :param df: transaction data
        :param item: target item
        :param length: maximum lag length
        :return: z_value of the given item
        """
        vec=[0]*(length+1)
        df_filtered = df[df['item_id'] == item]
        if len(df_filtered)==1:
            z_value=-np.inf
        else:
            loc=[length+i for i in df_filtered.lag.tolist()]
            value=df_filtered.user_count.tolist()
            for i,j in zip(loc,range(len(value))):
                vec[i]=value[j]
            z_value=self.rolling_zscore(vec[:-1],vec[-1:],decay=self.decay)
        return z_value

    # plot the trending items over time
    def plot_trend(self,items):
        """
        :param items: list of items we wish to plot  
        :return: plot trending items
        """
        num_plots=len(items)
        plt.gca().set_prop_cycle(plt.cycler('color', plt.cm.Accent(np.linspace(0, 1, num_plots))))
        # colormap=plt.cm.gist_ncar
        # plt.gca().set_color_cycle([colormap(i) for i in np.linspace(0, 0.9, num_plots)])
        labels=[]
        for item in items:
            df_filtered = self.data[self.data['item_id'] == item]
            _lag = df_filtered.lag.tolist()[::-1]
            _num_user = df_filtered.user_count.tolist()[::-1]
            plt.plot(_lag,_num_user)
            labels.append(item)
        plt.legend(labels,ncol=5,loc='upper center')
        plt.title('Top Trending Items')
        plt.ylabel('Number of transactions')
        plt.xlabel('Month-end lag')
        return plt.show()

    def rolling_zscore(self,data, observed_window, decay=0.1):
        """
        The lowest the decay, the more important the new points
        Decay is there to ensure that new data is worth more than old data
        in terms of trendiness
        """
        # Set the average to a the first value of the history to start with
        avg = float(data[0])
        squared_average = float(data[0] ** 2)
        def add_to_history(point, average, sq_average):
            average = average * decay + point * (1 - decay)
            sq_average = sq_average * decay + (point ** 2) * (1 - decay)
            return average, sq_average

        def calculate_zscore(average, sq_average, value):
            std = round(sqrt(sq_average - avg ** 2))
            if std == 0:
                return value - average
            return (value - average) / std

        for point in data[1:]:
            avg, squared_average = add_to_history(point, avg, squared_average)
        trends = []
        # We recalculate the averages for each new point added to be more
        # accurate
        for point in observed_window:
            trends.append(calculate_zscore(avg, squared_average, point))
            avg, squared_average = add_to_history(point, avg, squared_average)
        # Close enough way to find a trend in the window
        return sum(trends) / len(trends) if len(trends) != 0 else 0

def app():
    # create a trend object
    print("Loading the trending object ...", end="")
    trend_obj=trend(decay=0.1,interval_days=40)
    trend_obj.load_data('transaction.csv',item_col='item_id',user_col='user_id',interaction_time='interaction_time',
                    interaction_type='interaction_type')
    print("Done!")
    print("Calculating the trending items...")
    trending_data=trend_obj.calc()
    top_trending_items=trending_data.head(3).item.tolist()
    print(trending_data.head(3))
    trend_obj.plot_trend(top_trending_items)
    return trending_data

if __name__=='__main__':
    app()



