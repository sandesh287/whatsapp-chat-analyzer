# import libraries
import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
from matplotlib import font_manager
import seaborn as sns


# page config
st.set_page_config(page_title="WhatsApp Analyzer", layout="wide")

plt.rcParams['font.family'] = 'DejaVu Sans'

# font path for emoji
# font_path = "C:/Windows/Fonts/seguiemj.ttf"  # Segoe UI Emoji
# prop = font_manager.FontProperties(fname=font_path)

# ---- HEADER ----
st.title("📊 WhatsApp Chat Analyzer")
st.markdown("Upload your exported WhatsApp chat and explore insights.")

# ---- SIDEBAR ----
st.sidebar.title("📁 Upload & Filter")
uploaded_file = st.sidebar.file_uploader("Upload WhatsApp Chat (.txt)")

# Cache preprocessing
@st.cache_data
def load_data(data):
  return preprocessor.preprocess(data)


if uploaded_file is not None:
  data = uploaded_file.getvalue().decode("utf-8")
  df = load_data(data)

  # user selection
  user_list = sorted(df['user'].unique().tolist())
  user_list.insert(0, "Overall")
  selected_user = st.sidebar.selectbox("Select User", user_list)

  if st.sidebar.button("🚀 Show Analysis"):
    
    # ---- FILTER ONCE ----
    filtered_df = df if selected_user == "Overall" else df[df['user'] == selected_user]

    # ---- METRICS ----
    num_messages, words, num_media_messages, num_links = helper.fetch_stats("Overall", filtered_df)


    # 🔹 1. Metrics (TOP)
    st.markdown("## 📌 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Messages", num_messages)
    col2.metric("Words", words)
    col3.metric("Media", num_media_messages)
    col4.metric("Links", num_links)

    st.markdown("---")  # divider


    # 🔹 2. Activity Insights
    st.markdown("## 📊 Activity Insights")
    
    # i. finding the most active user in the group (group level)
    if selected_user == 'Overall':
      st.subheader("Most Active Users")
      x, new_df = helper.most_active_users(df)
      
      col1, col2 = st.columns(2)
      
      with col1:
        fig, ax = plt.subplots()
        ax.bar(x.index, x.values, color='orange')
        plt.xticks(rotation=45)
        st.pyplot(fig)
      
      with col2:
        st.dataframe(new_df)
      
    st.markdown("---")
    
    
    # ii. Most Common Words
    st.subheader("Most Common Words")
    
    most_common_df = helper.most_common_words("Overall", filtered_df)
    
    if not most_common_df.empty:
      col1, col2 = st.columns(2)
    
      with col1:
        st.dataframe(most_common_df)
    
      with col2:
        fig, ax = plt.subplots()
        ax.barh(most_common_df['word'], most_common_df['count'], color='green')
        ax.invert_yaxis()
        ax.set_title("Most Common Words")
        plt.xticks(rotation=45)
        st.pyplot(fig)

    st.markdown("---")
    
    
    # iii. Emoji Analysis
    st.subheader("Emoji Analysis")
    
    emoji_df = helper.emoji_helper("Overall", filtered_df)
    
    if not emoji_df.empty:
      col1, col2 = st.columns(2)
    
      with col1:
        fig, ax = plt.subplots()
        ax.pie(
          emoji_df['count'].head(), 
          labels=emoji_df['emoji'].head(), 
          # textprops={'fontproperties': prop, 'fontsize': 6},
          textprops={'fontsize': 6},
          autopct="%1.1f%%",
          startangle=90,
          labeldistance=1.1,    # move labels outward
          pctdistance=0.75      # move % inside slightly
        )
        ax.axis('equal')
        st.pyplot(fig)
    
      with col2:
        st.dataframe(emoji_df)
    
    st.markdown("---")
    
    
    # iv. Timeline Analysis
    st.subheader("Timeline Analysis")
    
    # a. Monthly message timeline
    st.markdown("#### Monthly Message Timeline")
    
    monthly_timeline = helper.monthly_timeline("Overall", filtered_df)
    
    if not monthly_timeline.empty:
      fig, ax = plt.subplots() 
      ax.plot(monthly_timeline['time'], monthly_timeline['message'], marker='o', color='purple')
      ax.grid(alpha=0.3)
      plt.xticks(rotation=45)
      ax.set_title("Monthly Message Timeline")
      st.pyplot(fig)
    
    st.markdown("---")
    
    
    # b. Daily message timeline
    st.markdown("#### Daily Message Timeline")
    
    daily_timeline = helper.daily_timeline("Overall", filtered_df)
    
    if not daily_timeline.empty:
      fig, ax = plt.subplots()
      ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black', linewidth=2)
      plt.xticks(rotation=45)
      ax.set_title("Daily Message Timeline")
      st.pyplot(fig)
    
    st.markdown("---")
    
    
    # c. Activity Map
    
    st.subheader("Activity Map")
    
    col1, col2 = st.columns(2)
    
    with col1:
      st.markdown("**Messages by Day of Week**")
      busy_day = helper.weekly_activity_map("Overall", filtered_df)
      fig, ax = plt.subplots()
      ax.bar(busy_day.index, busy_day.values, color='yellow')
      plt.xticks(rotation=45)
      st.pyplot(fig)
    
    with col2:
      st.markdown("**Messages by Month**")
      busy_month = helper.monthly_activity_map("Overall", filtered_df)
      fig, ax = plt.subplots()
      ax.bar(busy_month.index, busy_month.values, color='red')
      plt.xticks(rotation=45)
      st.pyplot(fig)
    
    st.markdown("---")
    
    
    # d. User Activity Heatmap
    
    st.subheader("User Activity Heatmap")
    
    user_heatmap = helper.activity_heatmap("Overall", filtered_df)
    
    fig, ax = plt.subplots()
    
    sns.heatmap(
      user_heatmap,
      cmap="YlGnBu",
      linewidths=0.5,
      annot=True
    )
    
    plt.yticks(rotation=0)
    plt.xticks(rotation=45)
    
    st.pyplot(fig)
    
    st.markdown("---")


    # 🔹 3. Word Analysis / Extra
    st.markdown("## ☁️ Word Cloud")
    
    df_wc = helper.create_wordcloud("Overall", filtered_df)
    
    fig, ax = plt.subplots()
    ax.set_title("Word Cloud")
    ax.imshow(df_wc)
    ax.axis('off')
    st.pyplot(fig)
        
    st.markdown("---")


    # 🔹 4. Raw Data (BOTTOM)
    with st.expander("🔍 View Raw Data"):
      st.write(f"Showing {filtered_df.shape[0]} messages")
      st.dataframe(filtered_df)
