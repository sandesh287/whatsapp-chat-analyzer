# def fetch_stats(selected_user, df):
  
#   if selected_user == 'Overall':
#     # 1. fetch number of messages
#     num_messages = df.shape[0]
#     # 2. fetch number of words
#     words = []
#     for message in df['message']:
#       words.extend(message.split())
    
#     return num_messages, len(words)
  
#   else:
#     new_df = df[df['user'] == selected_user]
#     # 1. fetch number of messages
#     num_messages = new_df.shape[0]
#     # 2. fetch number of words
#     words = []
#     for message in new_df['message']:
#       words.extend(message.split())
    
#     return num_messages, len(words)



# Code restructuring

import pandas as pd
from collections import Counter
import re
import emoji

from urlextract import URLExtract
extract = URLExtract()

from wordcloud import WordCloud



# Fetch number of messages, words, media, links
def fetch_stats(selected_user, df):
  
  if selected_user != 'Overall':
    df = df[df['user'] == selected_user]
  
  # fetch number of messages
  num_messages = df.shape[0]
  
  # fetch total number of words
  words = []
  for message in df['message']:
    words.extend(message.split())
  
  # fetch number of media messages
  num_media_messages = df[
    df['message'].isin(['video omitted', 'image omitted'])
  ].shape[0]
  
  # fetch number of links shared
  links = []
  for message in df['message']:
    links.extend(extract.find_urls(message))
  
  return num_messages, len(words), num_media_messages, len(links)



# Function to determine most active users
def most_active_users(df):
  x = df['user'].value_counts().head()
  new_df = round((df['user'].value_counts()/df.shape[0])*100,2).reset_index().rename(columns={'user':'name', 'count':'percent'})
  
  return x, new_df



# Word cloud function
def create_wordcloud(selected_user, df):
  
  # Load stopwords
  with open('nepenglish_stopwords.txt', 'r', encoding='utf-8') as f:
    stop_words = set(f.read().split())
  
  if selected_user != 'Overall':
    df = df[df['user'] == selected_user]
  
  # Remove media / omitted messages
  temp = df[~df['message'].str.contains('omitted', case=False, na=False)]
  
  def remove_stop_words(message):
    y = []
    for word in message.lower().split():
      if word not in stop_words:
        y.append(word)
    return " ".join(y)
  
  wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
  
  temp['message'] = temp['message'].apply(remove_stop_words)
  
  df_wc = wc.generate(temp['message'].str.cat(sep=" "))
  
  return df_wc



# Most common words function
def most_common_words(selected_user, df):
  
  # Load stopwords
  with open('nepenglish_stopwords.txt', 'r', encoding='utf-8') as f:
    stop_words = set(f.read().split())
  
  # Filter user
  if selected_user != 'Overall':
    df = df[df['user'] == selected_user]
  
  # ignore system messages
  # df = df[df['user'] != 'group_notification']
  
  # Remove media / omitted messages
  temp = df[~df['message'].str.contains('omitted', case=False, na=False)]
  
  # Word extraction
  words = []

  for message in temp['message']:
    for word in message.lower().split():
      
      # remove punctuation and emoji
      word = re.sub(r'[^\w]', '', word)
      
      word = word.strip()
      
      if word and word not in stop_words:
          words.append(word)
  
  # Count
  most_common_df = pd.DataFrame(
    Counter(words).most_common(20),
    columns=['word', 'count']
  )
  
  return most_common_df




# Emoji helper
def emoji_helper(selected_user, df):
  
  # Filter user
  if selected_user != 'Overall':
    df = df[df['user'] == selected_user]
  
  emojis = []
  
  for message in df['message']:
    emojis.extend([e['emoji'] for e in emoji.emoji_list(message)])
  
  emoji_counts = Counter(emojis)
  
  emoji_df = pd.DataFrame(
    emoji_counts.most_common(),
    columns=['emoji', 'count']
  )
  
  return emoji_df




# Monthly Timeline
def monthly_timeline(selected_user, df):
  
  # Filter user
  if selected_user != 'Overall':
    df = df[df['user'] == selected_user]
  
  # extract only year, month_num and month from dataframe
  monthly_timeline = df.groupby(['year', 'month_num', 'month'])['message'].count().reset_index()
  
  monthly_timeline = monthly_timeline.sort_values(['year', 'month_num'])
  
  monthly_timeline['time'] = monthly_timeline['month'] + "-" + monthly_timeline['year'].astype(str)
  
  return monthly_timeline




# Daily timeline
def daily_timeline(selected_user, df):
  
  # Filter user
  if selected_user != 'Overall':
    df = df[df['user'] == selected_user]
  
  daily_timeline = df.groupby('only_date').count()['message'].reset_index()
  
  return daily_timeline




# Weekly Activity Map
def weekly_activity_map(selected_user, df):
  
  # Filter user
  if selected_user != 'Overall':
    df = df[df['user'] == selected_user]
  
  weekly_activity = df['day_name'].value_counts()
  
  return weekly_activity




# Monthly Activity Map
def monthly_activity_map(selected_user, df):
  
  # Filter user
  if selected_user != 'Overall':
    df = df[df['user'] == selected_user]
  
  monthly_activity = df['month'].value_counts()
  
  return monthly_activity





# Activity Heatmap
def activity_heatmap(selected_user, df):
  
  # Filter user
  if selected_user != 'Overall':
    df = df[df['user'] == selected_user]
  
  user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)
  
  return user_heatmap