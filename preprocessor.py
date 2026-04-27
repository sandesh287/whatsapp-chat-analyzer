import pandas as pd
import re

def preprocess(data):
    pattern = r'(?:\u200e)?\[(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}:\d{2})\]\s(.*?)(?=\n(?:\u200e)?\[|$)'
  
    matches = re.findall(pattern, data, re.DOTALL)
  
    df = pd.DataFrame(matches, columns = ["date", "time", "user_message"])
  
    df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'], dayfirst=True)
  
    df['user_message'] = df['user_message'].str.replace('\u200e', '', regex=False)
  
    df = df[['datetime', 'user_message']]
  
    df2 = df.copy()
  
    # separate without regex
    users = []
    messages = []

    for message in df2['user_message']:

        if ':' in message:
            user, msg = message.split(':', 1)
            users.append(user.strip())
            messages.append(msg.strip())

        else:
            users.append('group_notification')
            messages.append(message.strip())

    df2['user'] = users
    df2['message'] = messages

    df2.drop(columns=['user_message'], inplace=True)
  
  
    df2['only_date'] = df2['datetime'].dt.date
    df2['year'] = df2['datetime'].dt.year
    df2['month'] = df2['datetime'].dt.month_name()
    df2['month_num'] = df2['datetime'].dt.month
    df2['day'] = df2['datetime'].dt.day
    df2['hour'] = df2['datetime'].dt.hour
    df2['minute'] = df2['datetime'].dt.minute
    df2['second'] = df2['datetime'].dt.second
    df2['day_name'] = df2['datetime'].dt.day_name()
  
  
    period = []
    for hour in df2[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour+1))
        else:
            period.append(str(hour) + "-" + str(hour+1))

    df2['period'] = period
    
    
    return df2