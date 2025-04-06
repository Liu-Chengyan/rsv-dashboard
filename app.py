import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

# 修复 numpy >= 1.24 的 bool8 错误
if not hasattr(np, 'bool8'):
    np.bool8 = np.bool_

# 设置页面配置
st.set_page_config(page_title="RSV Vaccine Coverage Dashboard", layout="wide")

# 加载数据
@st.cache_data
def load_data():
    df = pd.read_csv("Weekly_Differences_in_Cumulative_RSV_Vaccination_Coverage.csv")
    df.columns = df.columns.str.strip()  # 去除列名空格，防止 KeyError
    df["Week Ending"] = pd.to_datetime(df["Week Ending"])
    return df

df = load_data()

# 侧边栏控件
st.sidebar.header("🧭 Filters")

age_group = st.sidebar.selectbox("Select Age Group", sorted(df["age_group"].dropna().unique()))
demo_level = st.sidebar.selectbox("Select Demographic Dimension", sorted(df["Demographic Level"].dropna().unique()))

# 提取 Comparison Group 1 和 2 的所有分组
group1 = df[
    (df["age_group"] == age_group) & 
    (df["Demographic Level"] == demo_level)
]["Comparison Group 1"].dropna()

group2 = df[
    (df["age_group"] == age_group) & 
    (df["Demographic Level"] == demo_level)
]["Comparison Group 2"].dropna()

all_groups = pd.Series(group1.tolist() + group2.tolist()).dropna().unique()
selected_groups = st.sidebar.multiselect("Select Population Groups", sorted(all_groups), default=list(all_groups))

# 页面主标题
st.title("📊 RSV Vaccination Coverage Among Adults Aged 60+")

# 筛选 Group 1 数据
df1 = df[
    (df["age_group"] == age_group) &
    (df["Demographic Level"] == demo_level) &
    (df["Comparison Group 1"].isin(selected_groups))
][["Week Ending", "Comparison Group 1", "Comparison Group 1 Estimate"]].rename(
    columns={
        "Comparison Group 1": "Group",
        "Comparison Group 1 Estimate": "Coverage"
    }
)

# 筛选 Group 2 数据
df2 = df[
    (df["age_group"] == age_group) &
    (df["Demographic Level"] == demo_level) &
    (df["Comparison Group 2"].isin(selected_groups))
][["Week Ending", "Comparison Group 2", "Comparison Group 2 Estimate"]].rename(
    columns={
        "Comparison Group 2": "Group",
        "Comparison Group 2 Estimate": "Coverage"
    }
)

# 合并两个组数据
plot_df = pd.concat([df1, df2], ignore_index=True)

# 绘图
if plot_df.empty:
    st.warning("⚠ No data available for the selected filters.")
else:
    fig = px.line(
        plot_df,
        x="Week Ending",
        y="Coverage",
        color="Group",
        markers=True,
        title=f"RSV Vaccine Coverage – {age_group} – {demo_level}",
        labels={"Coverage": "% Vaccinated"},
    )
    fig.update_layout(
        legend_title_text="Group",
        yaxis_range=[0, 100],
        title_x=0.05
    )
    st.plotly_chart(fig, use_container_width=True)
