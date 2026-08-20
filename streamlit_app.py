from pathlib import Path

import pandas as pd
import streamlit as st

from upload_preview import render_upload_preview


st.set_page_config(page_title="StreamSight Analytics", page_icon="📊", layout="wide")


@st.cache_data
def load_default_data(path):
	"""Load the validated dataset once across Streamlit reruns."""
	source = Path(path)
	if not source.exists():
		return pd.DataFrame()
	data = pd.read_csv(source)
	if "transaction_date" in data.columns:
		data["transaction_date"] = pd.to_datetime(data["transaction_date"], errors="coerce")
	return data


def render_overview(df):
	st.title("Business Overview")
	st.caption("A quick read on activity, revenue, and data coverage.")
	if df.empty:
		st.info("No validated data is available yet. Open Data Explorer to upload a file.")
		return

	revenue = float(df["amount"].sum()) if "amount" in df else 0.0
	customers = int(df["customer_id"].nunique()) if "customer_id" in df else 0
	transactions = len(df)
	completion = float(df["completion_rate"].mean()) if "completion_rate" in df else 0.0
	columns = st.columns(4)
	columns[0].metric("Revenue", f"${revenue:,.0f}")
	columns[1].metric("Customers", f"{customers:,}")
	columns[2].metric("Transactions", f"{transactions:,}")
	columns[3].metric("Completion Rate", f"{completion:.1f}%")

	st.divider()
	st.header("Data Health")
	health = pd.DataFrame({
		"Measure": ["Rows", "Columns", "Missing values", "Duplicate rows"],
		"Value": [len(df), len(df.columns), int(df.isna().sum().sum()), int(df.duplicated().sum())],
	})
	st.dataframe(health, use_container_width=True, hide_index=True)


def render_trends(df):
	st.title("Trend Analysis")
	st.caption("Follow revenue and engagement over time.")
	if not {"transaction_date", "amount"}.issubset(df.columns):
		st.warning("Trend charts require transaction_date and amount columns.")
		return
	trend = df.dropna(subset=["transaction_date"]).set_index("transaction_date")["amount"].resample("M").sum()
	st.subheader("Monthly Revenue")
	st.line_chart(trend)
	if "completion_rate" in df.columns:
		engagement = df.set_index("transaction_date")["completion_rate"].resample("M").mean()
		st.subheader("Average Completion Rate")
		st.line_chart(engagement)


def render_segments(df):
	st.title("Segment Breakdown")
	st.caption("Compare revenue across the dimensions available in the dataset.")
	dimensions = [column for column in ("customer_type", "product_category") if column in df.columns]
	if "amount" not in df.columns or not dimensions:
		st.info("Segment charts require amount and a customer_type or product_category column.")
		return
	dimension = st.selectbox("Break down by", dimensions)
	summary = df.groupby(dimension)["amount"].sum().sort_values(ascending=False)
	st.bar_chart(summary)
	with st.expander("View segment table"):
		st.dataframe(summary.rename("Revenue").to_frame(), use_container_width=True)


def render_data_explorer(df):
	st.title("Data Explorer")
	st.caption("Upload a dataset or inspect the validated source used by the dashboard.")
	uploaded_file = st.file_uploader("Upload CSV or JSON", type=["csv", "json"])
	if uploaded_file is not None:
		render_upload_preview(uploaded_file)
		return
	if df.empty:
		st.info("Upload a CSV or JSON file to begin exploring data.")
		return

	with st.expander("Filters", expanded=True):
		filtered_df = df
		if "product_category" in df.columns:
			categories = st.multiselect("Product category", sorted(df["product_category"].dropna().unique()))
			if categories:
				filtered_df = filtered_df[filtered_df["product_category"].isin(categories)]
	with st.expander("View raw data"):
		st.dataframe(filtered_df, use_container_width=True, hide_index=True)
		st.download_button("Download filtered CSV", filtered_df.to_csv(index=False), "filtered_data.csv", "text/csv")


def main():
	st.sidebar.title("StreamSight")
	st.sidebar.caption("Analytics workspace")
	page = st.sidebar.radio("Navigate", ["Overview", "Trends", "Segments", "Data Explorer"])
	df = load_default_data(Path(__file__).parent / "output" / "validated_engagement_data.csv")

	if page == "Overview":
		render_overview(df)
	elif page == "Trends":
		render_trends(df)
	elif page == "Segments":
		render_segments(df)
	else:
		render_data_explorer(df)


if __name__ == "__main__":
	main()
