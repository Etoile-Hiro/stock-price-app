import streamlit as st
import yfinance as yf
import datetime
import altair as alt  # 忘れずに追加

st.title("Etoile-Hiro's Stock Dashboard")

# --- サイドバー ---
st.sidebar.write("### オプション設定")
tickers = st.sidebar.multiselect(
    "銘柄を選択してください",
    ["AAPL", "GOOGL", "META", "AMZN", "MSFT", "TSLA", "NVDA"],
    default=["AAPL", "GOOGL"]
)
days = st.sidebar.slider("表示日数", 1, 365, 30)
price_range = st.sidebar.slider("株価の範囲指定 (USD)", 0.0, 1000.0, (0.0, 500.0))

# --- データ取得 ---
if not tickers:
    st.warning("少なくとも一社選んでください")
else:
    try:
        # 期間計算のロジック
        start_date = datetime.date.today() - datetime.timedelta(days=days)
        
        # データの取得
        raw_data = yf.download(tickers, start=start_date)
        
        # 単一銘柄と複数銘柄でデータの構造が変わるのを防ぐ処理
        if len(tickers) == 1:
            data = raw_data['Close'].to_frame()
            data.columns = tickers
        else:
            data = raw_data['Close']
        
        st.write(f"### 過去 {days} 日間の株価チャート")
        
        # --- AltairによるY軸制御の実装 ---
        # 1. データを縦持ち（Long-form）に変換
        df_plot = data.reset_index()
        chart_data = df_plot.melt('Date', var_name='Ticker', value_name='Price')

        # 2. チャート定義：y軸のScaleにスライダーの値を流し込む
        chart = alt.Chart(chart_data).mark_line().encode(
            x=alt.X('Date:T', title='日付'),
            y=alt.Y('Price:Q', 
                    scale=alt.Scale(domain=[price_range[0], price_range[1]]), 
                    title='株価 (USD)'),
            color='Ticker:N'
        ).properties(
            height=400
        ).interactive()

        # 3. 表示
        st.altair_chart(chart, use_container_width=True)
        
        st.write("最新データ（詳細）", data.tail())

    except Exception as e:
        st.error(f"データの取得に失敗しました。理由: {e}")