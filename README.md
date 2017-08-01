# Trending
## How to determine the trending of items
The code spots the trending items for a given time period. Below I explain that how trendiness is determined.

Trendiness: Item is a trending item when it is mentioned (purchased, cliked, viewed,etc) more often than usual. 

### Algorithm: rolling z-score
This is the standard algorithm to find trending items and is simple to implement:
```
z=(x-\mu)/\sigma,
```
where \mu is the history mean and \sigma is the standard deviation of the history data. In the following code, for every point,
the above formula is re-applied with a decay factor so that the oldest points carry the less factor value. 

When a z-score is used, the higher or lower the z-score the more abnormal the trend, so for example if the z-score is highly
 positive then the trend is abnormally rising, while if it is highly negative it is abnormally falling. Hence, the z-score
  for all the candidate trends the highest top_n z-scores will relate to the most abnormally increasing z-scores.
  
Note:
    * You can user this trending method with a sliding window, for instance last 10-day transaction, if you wish to use the 
    recent transaction and not take much historical data into account. This can be done by cutting down on the transaction time 
    of the original data.
    
## References:
https://vincent.is/finding-trending-things/
https://www.isixsigma.com/tools-templates/statistical-analysis/improved-forecasting-moving-averages-and-z-scores/
