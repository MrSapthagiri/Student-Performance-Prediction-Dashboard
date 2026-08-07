import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def make_performance_chart(df: pd.DataFrame):
    fig = px.bar(df, x="Category", y="Count", color="Category", title="Performance Distribution")
    return fig


def make_distribution_chart(df: pd.DataFrame):
    fig = px.histogram(df, x="Attendance", title="Attendance Distribution")
    return fig


def make_corr_heatmap(df: pd.DataFrame):
    numeric_df = df.select_dtypes(include=["number"]).copy()
    corr = numeric_df.corr()
    fig = go.Figure(data=go.Heatmap(z=corr.values, x=corr.columns, y=corr.columns, colorscale="Viridis"))
    fig.update_layout(title="Correlation Heatmap")
    return fig
