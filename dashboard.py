import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

st.set_page_config(page_title="Supermarket Sales Dashboard", layout="wide")

MONTHS = ["January", "February", "March"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


@st.cache_data
def load_data():
    d = pd.read_csv("supermarket_clean.csv", parse_dates=["Date"])

    # K-Means: group sales by unit price and quantity (3 groups)
    z = StandardScaler().fit_transform(d[["Unit price", "Quantity"]])
    d["Group"] = KMeans(n_clusters=3, n_init=10, random_state=42).fit_predict(z)

    # Give each group a readable name
    means = d.groupby("Group")[["Unit price", "Quantity"]].mean()
    cheap = means["Unit price"].idxmin()
    rest = means.drop(cheap)
    bulk = rest["Quantity"].idxmax()
    names = {cheap: "Cheap items"}
    for g in rest.index:
        names[g] = "Expensive, bought in bulk" if g == bulk else "Expensive, bought a few at a time"
    d["Segment"] = d["Group"].map(names)
    return d


data = load_data()

st.title("Supermarket Sales Dashboard")
st.caption("Data warehouse project (CSE4005): 200 sales from three branches, January to March 2019")

# ---------- Filters ----------
st.sidebar.header("Filters")
city = st.sidebar.multiselect("City", sorted(data["City"].unique()), default=sorted(data["City"].unique()))
product = st.sidebar.multiselect("Product line", sorted(data["Product line"].unique()),
                                 default=sorted(data["Product line"].unique()))
ctype = st.sidebar.multiselect("Customer type", sorted(data["Customer type"].unique()),
                               default=sorted(data["Customer type"].unique()))
month = st.sidebar.multiselect("Month", MONTHS, default=MONTHS)

df = data[data["City"].isin(city) & data["Product line"].isin(product)
          & data["Customer type"].isin(ctype) & data["Month"].isin(month)]

if df.empty:
    st.warning("No sales match these filters. Please select more options on the left.")
    st.stop()

# ---------- Key numbers ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total sales", f"{df['Total'].sum():,.0f}")
c2.metric("Number of sales", f"{len(df)}")
c3.metric("Average bill", f"{df['Total'].mean():,.1f}")
c4.metric("Average rating", f"{df['Rating'].mean():.2f}")

tab1, tab2, tab3 = st.tabs(["Sales overview", "Customers and payments", "Sales groups (K-Means)"])

# ---------- Tab 1 ----------
with tab1:
    a, b = st.columns(2)
    by_city = df.groupby("City", as_index=False)["Total"].sum().sort_values("Total")
    a.plotly_chart(px.bar(by_city, x="Total", y="City", orientation="h", title="Sales by city"),
                   width="stretch")
    by_prod = df.groupby("Product line", as_index=False)["Total"].sum().sort_values("Total")
    b.plotly_chart(px.bar(by_prod, x="Total", y="Product line", orientation="h",
                          title="Sales by product line"), width="stretch")

    a, b = st.columns(2)
    by_month = df.groupby("Month", as_index=False)["Total"].sum()
    by_month["Month"] = pd.Categorical(by_month["Month"], categories=MONTHS, ordered=True)
    by_month = by_month.sort_values("Month")
    a.plotly_chart(px.line(by_month, x="Month", y="Total", markers=True, title="Sales by month"),
                   width="stretch")
    by_day = df.groupby("Weekday", as_index=False)["Total"].sum()
    by_day["Weekday"] = pd.Categorical(by_day["Weekday"], categories=DAYS, ordered=True)
    by_day = by_day.sort_values("Weekday")
    b.plotly_chart(px.bar(by_day, x="Weekday", y="Total", title="Sales by day of the week"),
                   width="stretch")

# ---------- Tab 2 ----------
with tab2:
    a, b = st.columns(2)
    pay = df.groupby("Payment", as_index=False)["Total"].sum()
    a.plotly_chart(px.pie(pay, names="Payment", values="Total", hole=0.4,
                          title="Share of sales by payment method"), width="stretch")
    cust = df.groupby("Customer type", as_index=False)["Total"].mean()
    b.plotly_chart(px.bar(cust, x="Customer type", y="Total", title="Average bill: members vs normal"),
                   width="stretch")
    st.plotly_chart(px.histogram(df, x="Rating", nbins=10, title="Customer ratings"),
                    width="stretch")

# ---------- Tab 3 ----------
with tab3:
    st.write("K-Means grouped the sales into 3 types by unit price and quantity.")
    st.plotly_chart(px.scatter(df, x="Unit price", y="Quantity", color="Segment",
                               hover_data=["City", "Product line", "Total"],
                               title="Sales groups"), width="stretch")
    summary = df.groupby("Segment").agg(
        Sales=("Total", "size"), Average_price=("Unit price", "mean"),
        Average_quantity=("Quantity", "mean"), Average_bill=("Total", "mean")).round(1)
    st.dataframe(summary, width="stretch")

with st.expander("Show the data"):
    st.dataframe(df, width="stretch")