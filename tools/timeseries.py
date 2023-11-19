# CREATE RANDOM DATASET
import random
from datetime import datetime, timedelta
import pandas as pd

def create_sample_timeserie(rows, columns):
    data = {}
    end_date = datetime.now()
    dates = pd.date_range(end=end_date, periods=rows, freq='1D')
    for i in range(columns):
        column_name = f"Column {i+1}"
        data[column_name] = [random.random() for _ in range(rows)]
    return pd.DataFrame(data, index=dates)

df = create_sample_timeserie(1000, 1)
df["EMA"] = df.ewm(span=55, adjust=False).mean()
df["EMA2"] = df.iloc[:,0].ewm(span=555, adjust=False).mean()
df