import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Trader Behavior Dashboard", layout="wide")

st.title("📊 Trader Behavior vs Market Sentiment")

# 📌 Insights section
st.markdown("""
### 📌 Key Insights
- 📈 Higher profits observed during Greed phases
- ⚠️ Fear phases show higher volatility
- 📊 Neutral markets show lower opportunities
""")

# Load data
trades = pd.read_csv("data/historical_data.csv")
sentiment = pd.read_csv("data/fear_greed_index.csv")

# Clean columns
trades.columns = trades.columns.str.strip().str.lower().str.replace(" ", "_")
sentiment.columns = sentiment.columns.str.strip().str.lower()

# Convert dates
trades['timestamp_ist'] = pd.to_datetime(trades['timestamp_ist'], format='%d-%m-%Y %H:%M')
trades['date'] = trades['timestamp_ist'].dt.date
sentiment['date'] = pd.to_datetime(sentiment['date']).dt.date

# Merge
merged = trades.merge(sentiment[['date', 'classification', 'value']], on='date')

# Features
merged['is_profit'] = merged['closed_pnl'] > 0
merged['trade_size'] = merged['size_usd'].abs()
merged['sentiment'] = merged['classification'].replace({
    'Extreme Fear': 'Fear',
    'Extreme Greed': 'Greed'
})

# 🔥 Sidebar Filters
st.sidebar.title("Filters")

selected_sentiment = st.sidebar.multiselect(
    "Select Sentiment",
    options=merged['sentiment'].unique(),
    default=merged['sentiment'].unique()
)

selected_coin = st.sidebar.multiselect(
    "Select Coin",
    options=merged['coin'].unique(),
    default=merged['coin'].unique()
)

# Apply filters
filtered = merged[
    (merged['sentiment'].isin(selected_sentiment)) &
    (merged['coin'].isin(selected_coin))
]

# 📊 Metrics (dynamic)
col1, col2, col3 = st.columns(3)

col1.metric("📈 Avg PnL", f"{filtered['closed_pnl'].mean():.2f}")
col2.metric("✅ Win Rate", f"{filtered['is_profit'].mean()*100:.2f}%")
col3.metric("💰 Avg Trade Size", f"{filtered['trade_size'].mean():.2f}")

st.markdown("---")

# 📊 Charts
st.subheader("📈 Average PnL by Sentiment")
pnl = filtered.groupby('sentiment')['closed_pnl'].mean()
fig1, ax1 = plt.subplots()
sns.barplot(x=pnl.index, y=pnl.values, ax=ax1)
st.pyplot(fig1)

st.subheader("📊 Win Rate by Sentiment")
win = filtered.groupby('sentiment')['is_profit'].mean() * 100
fig2, ax2 = plt.subplots()
sns.barplot(x=win.index, y=win.values, ax=ax2)
st.pyplot(fig2)

st.subheader("📉 PnL Distribution")
fig3, ax3 = plt.subplots()
sns.boxplot(x='sentiment', y='closed_pnl', data=filtered, ax=ax3)
st.pyplot(fig3)

# 🏆 Top Traders
st.subheader("🏆 Top Traders by PnL")

top_traders = (
    filtered.groupby('account')['closed_pnl']
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

st.dataframe(top_traders)

# Raw data
if st.checkbox("Show Raw Data"):
    st.dataframe(filtered.head(100))
