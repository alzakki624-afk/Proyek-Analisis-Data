import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import streamlit as st

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="E-Commerce Dashboard",
    page_icon="🛒",
    layout="wide"
)

# Resolve path relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ===== LOAD DATA =====
@st.cache_data
def load_main_data():
    df = pd.read_csv(os.path.join(SCRIPT_DIR, "main_data.csv"))
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    return df

@st.cache_data
def load_rfm_data():
    return pd.read_csv(os.path.join(SCRIPT_DIR, "rfm_data.csv"))

main_df = load_main_data()
rfm_df = load_rfm_data()

# ===== SIDEBAR =====
st.sidebar.header("Filter Data")

min_date = main_df['order_purchase_timestamp'].min().date()
max_date = main_df['order_purchase_timestamp'].max().date()

date_range = st.sidebar.date_input(
    "Rentang Tanggal",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = min_date
    end_date = max_date

# Filter data berdasarkan tanggal
filtered_df = main_df[
    (main_df['order_purchase_timestamp'].dt.date >= start_date) &
    (main_df['order_purchase_timestamp'].dt.date <= end_date)
]

# ===== HEADER =====
st.title("🛒 E-Commerce Public Dashboard")
st.markdown("Dashboard analisis data e-commerce untuk memonitor performa penjualan, segmentasi pelanggan, dan distribusi geografis.")
st.markdown("---")

# ===== KPI METRICS =====
col1, col2, col3, col4 = st.columns(4)

total_orders = filtered_df['order_id'].nunique()
total_revenue = filtered_df['price'].sum()
avg_review = filtered_df['review_score'].mean()
total_customers = filtered_df['customer_unique_id'].nunique()

with col1:
    st.metric("Total Pesanan", f"{total_orders:,}")
with col2:
    st.metric("Total Revenue", f"R$ {total_revenue:,.2f}")
with col3:
    st.metric("Rata-rata Review", f"{avg_review:.2f} ⭐")
with col4:
    st.metric("Total Pelanggan", f"{total_customers:,}")

st.markdown("---")

# ===== SECTION 1: TREN PENJUALAN BULANAN =====
st.subheader("📈 Tren Penjualan Bulanan")

filtered_df_copy = filtered_df.copy()
filtered_df_copy['order_month'] = filtered_df_copy['order_purchase_timestamp'].dt.to_period('M')

monthly_orders = filtered_df_copy.groupby('order_month').agg(
    total_orders=('order_id', 'nunique'),
    total_revenue=('price', 'sum')
).reset_index()
monthly_orders['order_month'] = monthly_orders['order_month'].astype(str)

fig, ax1 = plt.subplots(figsize=(14, 5))

color_revenue = '#2E86AB'
ax1.set_xlabel('Bulan', fontsize=11)
ax1.set_ylabel('Total Revenue (R$)', color=color_revenue, fontsize=11)
line1 = ax1.plot(monthly_orders['order_month'], monthly_orders['total_revenue'],
                 color=color_revenue, linewidth=2.5, marker='o', markersize=5, label='Revenue')
ax1.tick_params(axis='y', labelcolor=color_revenue)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'R$ {x:,.0f}'))

ax2 = ax1.twinx()
color_orders = '#A23B72'
ax2.set_ylabel('Jumlah Pesanan', color=color_orders, fontsize=11)
line2 = ax2.plot(monthly_orders['order_month'], monthly_orders['total_orders'],
                 color=color_orders, linewidth=2.5, marker='s', markersize=5, linestyle='--', label='Orders')
ax2.tick_params(axis='y', labelcolor=color_orders)

plt.xticks(rotation=45, ha='right')
lines = line1 + line2
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='upper left', fontsize=10)
ax1.set_title('Tren Revenue dan Jumlah Pesanan per Bulan', fontsize=13, fontweight='bold')
fig.tight_layout()
st.pyplot(fig)

st.markdown("---")

# ===== SECTION 2: TOP KATEGORI PRODUK =====
st.subheader("🏆 Top 10 Kategori Produk Terlaris")

top_categories = filtered_df.groupby('product_category_name_english').agg(
    total_orders=('order_id', 'nunique'),
    total_revenue=('price', 'sum')
).sort_values('total_orders', ascending=False).head(10)

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = sns.color_palette("coolwarm", n_colors=10)
    bars = ax.barh(top_categories.index[::-1], top_categories['total_orders'][::-1], color=colors)
    ax.set_xlabel('Jumlah Pesanan', fontsize=11)
    ax.set_title('Berdasarkan Jumlah Pesanan', fontsize=12, fontweight='bold')
    for bar, val in zip(bars, top_categories['total_orders'][::-1]):
        ax.text(val + 30, bar.get_y() + bar.get_height()/2, f'{val:,}',
                va='center', fontsize=9, fontweight='bold')
    fig.tight_layout()
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.barh(top_categories.index[::-1], top_categories['total_revenue'][::-1], color=colors)
    ax.set_xlabel('Total Revenue (R$)', fontsize=11)
    ax.set_title('Berdasarkan Revenue', fontsize=12, fontweight='bold')
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'R$ {x:,.0f}'))
    for bar, val in zip(bars, top_categories['total_revenue'][::-1]):
        ax.text(val + 1000, bar.get_y() + bar.get_height()/2, f'R$ {val:,.0f}',
                va='center', fontsize=9)
    fig.tight_layout()
    st.pyplot(fig)

st.markdown("---")

# ===== SECTION 3: SEGMENTASI RFM =====
st.subheader("👥 Segmentasi Pelanggan (RFM Analysis)")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(8, 6))
    segment_counts = rfm_df['segment'].value_counts()
    colors_segment = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B', '#44BBA4', '#E94F37', '#393E41']
    bars = ax.barh(segment_counts.index, segment_counts.values, color=colors_segment[:len(segment_counts)])
    ax.set_xlabel('Jumlah Pelanggan', fontsize=11)
    ax.set_title('Distribusi Segmen Pelanggan', fontsize=12, fontweight='bold')
    for bar, val in zip(bars, segment_counts.values):
        ax.text(val + 50, bar.get_y() + bar.get_height()/2, f'{val:,}',
                va='center', fontsize=9, fontweight='bold')
    fig.tight_layout()
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(8, 6))
    segment_monetary = rfm_df.groupby('segment')['monetary'].mean().sort_values(ascending=True)
    bars = ax.barh(segment_monetary.index, segment_monetary.values, color=colors_segment[:len(segment_monetary)])
    ax.set_xlabel('Rata-rata Monetary (R$)', fontsize=11)
    ax.set_title('Rata-rata Monetary per Segmen', fontsize=12, fontweight='bold')
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'R$ {x:,.0f}'))
    for bar, val in zip(bars, segment_monetary.values):
        ax.text(val + 3, bar.get_y() + bar.get_height()/2, f'R$ {val:,.0f}',
                va='center', fontsize=9)
    fig.tight_layout()
    st.pyplot(fig)

# RFM Summary Table
st.markdown("#### Rangkuman Segmentasi RFM")
rfm_summary = rfm_df.groupby('segment').agg(
    Jumlah_Pelanggan=('customer_unique_id', 'count'),
    Avg_Recency=('recency', 'mean'),
    Avg_Frequency=('frequency', 'mean'),
    Avg_Monetary=('monetary', 'mean')
).sort_values('Avg_Monetary', ascending=False)

rfm_summary['Avg_Recency'] = rfm_summary['Avg_Recency'].round(1)
rfm_summary['Avg_Frequency'] = rfm_summary['Avg_Frequency'].round(2)
rfm_summary['Avg_Monetary'] = rfm_summary['Avg_Monetary'].apply(lambda x: f'R$ {x:,.2f}')

st.dataframe(rfm_summary, width=None)

st.markdown("---")

# ===== SECTION 4: DISTRIBUSI GEOGRAFIS =====
st.subheader("🗺️ Distribusi Pelanggan per State")

state_data = filtered_df.groupby('customer_state').agg(
    total_customers=('customer_unique_id', 'nunique'),
    total_revenue=('price', 'sum')
).sort_values('total_revenue', ascending=False).reset_index()

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(8, 7))
    top_states = state_data.head(10)
    colors_state = sns.color_palette("viridis", n_colors=10)
    bars = ax.barh(top_states['customer_state'][::-1], top_states['total_revenue'][::-1], color=colors_state)
    ax.set_xlabel('Total Revenue (R$)', fontsize=11)
    ax.set_title('Top 10 State by Revenue', fontsize=12, fontweight='bold')
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'R$ {x:,.0f}'))
    for bar, val in zip(bars, top_states['total_revenue'][::-1]):
        ax.text(val + 5000, bar.get_y() + bar.get_height()/2, f'R$ {val:,.0f}',
                va='center', fontsize=9)
    fig.tight_layout()
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(8, 7))
    bars = ax.barh(top_states['customer_state'][::-1], top_states['total_customers'][::-1], color=colors_state)
    ax.set_xlabel('Jumlah Pelanggan', fontsize=11)
    ax.set_title('Top 10 State by Jumlah Pelanggan', fontsize=12, fontweight='bold')
    for bar, val in zip(bars, top_states['total_customers'][::-1]):
        ax.text(val + 50, bar.get_y() + bar.get_height()/2, f'{val:,}',
                va='center', fontsize=9)
    fig.tight_layout()
    st.pyplot(fig)

st.markdown("---")

# ===== FOOTER =====
st.caption("Copyright (c) 2024 - E-Commerce Data Analysis Dashboard")
