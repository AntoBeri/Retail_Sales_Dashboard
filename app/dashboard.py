import os
import streamlit as st
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(
    page_title="Retail Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Theme overrides
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    .metric-card {
        background: #ffffff;
        border: 1px solid #e8e8e8;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        border-left: 4px solid #0d9488;
    }
    .metric-label {
        font-size: 12px;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 600;
        color: #111827;
    }
    .metric-sub {
        font-size: 12px;
        color: #6b7280;
        margin-top: 2px;
    }
    .section-title {
        font-size: 14px;
        font-weight: 600;
        color: #374151;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin: 1.5rem 0 0.75rem;
        padding-bottom: 6px;
        border-bottom: 1px solid #f0f0f0;
    }
    [data-testid="stSidebar"] {
        background-color: #f9fafb;
        border-right: 1px solid #e5e7eb;
    }
    div[data-testid="metric-container"] { display: none; }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    df =pd.read_csv(os.path.join(BASE_DIR, '..', 'data', 'clean', 'retail_sales_dataset_clean.csv'))
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])

    return df

df = load_data()

# Sidebar filters
with st.sidebar:
    st.markdown("### Filters")
    st.markdown("---")

    year = st.multiselect(
        "Year",
        options=sorted(df['year'].unique()),
        default=sorted(df['year'].unique())
    )
    quarter = st.multiselect(
        "Quarter",
        options=sorted(df['quarter'].unique()),
        default=sorted(df['quarter'].unique()),
        format_func=lambda x: f"Q{x}"
    )
    region = st.multiselect(
        "Region",
        options=sorted(df['region'].unique()),
        default=sorted(df['region'].unique())
    )
    channel = st.multiselect(
        "Sales channel",
        options=sorted(df['sales_channel'].unique()),
        default=sorted(df['sales_channel'].unique())
    )
    segment = st.multiselect(
        "Customer segment",
        options=sorted(df['customer_segment'].unique()),
        default=sorted(df['customer_segment'].unique())
    )
    category = st.multiselect(
        "Category",
        options=sorted(df['category'].unique()),
        default=sorted(df['category'].unique())
    )

# Apply filters
mask = (
    df['year'].isin(year) &
    df['quarter'].isin(quarter) &
    df['region'].isin(region) &
    df['sales_channel'].isin(channel) &
    df['customer_segment'].isin(segment) &
    df['category'].isin(category)
)
filtered = df[mask]

# Header 
st.markdown("## Retail Sales Dashboard")
st.markdown(f"Showing **{len(filtered):,}** transactions · {filtered['transaction_date'].min().strftime('%b %Y')} – {filtered['transaction_date'].max().strftime('%b %Y')}")
st.markdown("---")

# KPI cards
total_revenue    = filtered['sales_amount'].sum()
total_txn        = len(filtered)
avg_order        = filtered['sales_amount'].mean()
discount_rate    = filtered['has_discount'].mean() * 100

k1, k2, k3, k4 = st.columns(4)

def kpi_card(col, label, value, sub=""):
    col.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

kpi_card(k1, "Total revenue",       f"${total_revenue:,.0f}",  f"{total_txn:,} transactions")
kpi_card(k2, "Avg order value",     f"${avg_order:,.2f}",      "per transaction")
kpi_card(k3, "Discount rate",       f"{discount_rate:.1f}%",   "of transactions with discount")
kpi_card(k4, "Filtered transactions", f"{len(filtered):,}",   f"of {len(df):,} total")

# Revenue over time
st.markdown('<div class="section-title">Revenue over time</div>', unsafe_allow_html=True)

col_left, col_right = st.columns([2, 1])

with col_left:
    # Monthly revenue — 2024 vs 2025 overlaid
    monthly = (
        filtered.groupby(['year', 'month', 'month_name'])['sales_amount']
        .sum()
        .reset_index()
        .sort_values('month')
    )

    fig_line = px.line(
        monthly,
        x='month_name',
        y='sales_amount',
        color='year',
        markers=True,
        labels={'sales_amount': 'Revenue ($)', 'month_name': '', 'year': 'Year'},
        color_discrete_map={2024: '#0d9488', 2025: '#94d1ce'},
        category_orders={'month_name': [
            'January','February','March','April','May','June',
            'July','August','September','October','November','December'
        ]}
    )
    fig_line.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend_title_text='',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=0, r=0, t=10, b=0),
        yaxis=dict(gridcolor='#f0f0f0', tickprefix='$', tickformat=',.0f'),
        xaxis=dict(gridcolor='#f0f0f0'),
        hovermode='x unified'
    )
    fig_line.update_traces(
        line=dict(width=2.5), 
        marker=dict(size=6)
        )
    fig_line.update_yaxes(rangemode='tozero')

    st.markdown("**Monthly revenue — 2024 vs 2025**")
    st.plotly_chart(fig_line, use_container_width=True)

with col_right:
    # Revenue by quarter
    quarterly = (
        filtered.groupby(['year', 'quarter'])['sales_amount']
        .sum()
        .reset_index()
    )
    quarterly['label'] = quarterly.apply(lambda r: f"Q{int(r['quarter'])} {int(r['year'])}", axis=1)
    quarterly = quarterly.sort_values(['year', 'quarter'])

    fig_bar = px.bar(
        quarterly,
        x='label',
        y='sales_amount',
        labels={'sales_amount': 'Revenue ($)', 'label': ''},
        color_discrete_sequence=['#0d9488']
    )
    fig_bar.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=0, r=0, t=10, b=0),
        yaxis=dict(gridcolor='#f0f0f0', tickprefix='$', tickformat=',.0f'),
        xaxis=dict(gridcolor='#f0f0f0'),
    )
    fig_bar.update_traces(marker_color=[
        '#0d9488','#0d9488','#0d9488','#0d9488',
        '#94d1ce','#94d1ce','#94d1ce','#94d1ce'
    ])

    st.markdown("**Revenue by quarter**")
    st.plotly_chart(fig_bar, use_container_width=True)

# Product performance
st.markdown('<div class="section-title">Product performance</div>', unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1])

with col_left:
    # Top 10 categories by revenue
    cat_revenue = (
        filtered.groupby('category')['sales_amount']
        .sum()
        .reset_index()
        .sort_values('sales_amount', ascending=True)
        .tail(10)
    )

    fig_cat = px.bar(
        cat_revenue,
        x='sales_amount',
        y='category',
        orientation='h',
        labels={'sales_amount': 'Revenue ($)', 'category': ''},
        color_discrete_sequence=['#0d9488']
    )
    fig_cat.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(gridcolor='#f0f0f0', tickprefix='$', tickformat=',.0f'),
        yaxis=dict(gridcolor='#f0f0f0'),
    )

    st.markdown("**Top categories by revenue**")
    st.plotly_chart(fig_cat, use_container_width=True)

with col_right:
    # Avg revenue per unit by category
    pu_data = (
        filtered.groupby('category')['revenue_per_unit']
        .mean()
        .reset_index()
        .sort_values('revenue_per_unit', ascending=True)
    )

    fig_pu = px.bar(
        pu_data,
        x='revenue_per_unit',
        y='category',
        orientation='h',
        labels={'revenue_per_unit': 'Avg revenue per unit ($)', 'category': ''},
        color_discrete_sequence=['#94d1ce']
    )
    fig_pu.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(gridcolor='#f0f0f0', tickprefix='$', tickformat=',.2f'),
        yaxis=dict(gridcolor='#f0f0f0'),
    )

    st.markdown("**Avg revenue per unit by category**")
    st.plotly_chart(fig_pu, use_container_width=True)

# Sales tier distribution
tier_order = ['Small', 'Medium', 'Large', 'Premium']
tier_data = (
    filtered.groupby('sales_tier')['sales_amount']
    .agg(count='count', total='sum')
    .reindex(tier_order)
    .reset_index()
)

col_a, col_b = st.columns([1, 1])

with col_a:
    fig_tier_count = px.bar(
        tier_data,
        x='sales_tier',
        y='count',
        labels={'count': 'Number of transactions', 'sales_tier': ''},
        color_discrete_sequence=['#0d9488']
    )
    fig_tier_count.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=0, r=0, t=10, b=0),
        yaxis=dict(gridcolor='#f0f0f0'),
        xaxis=dict(gridcolor='#f0f0f0'),
    )
    st.markdown("**Transaction count by sales tier**")
    st.plotly_chart(fig_tier_count, use_container_width=True)

with col_b:
    fig_tier_rev = px.bar(
        tier_data,
        x='sales_tier',
        y='total',
        labels={'total': 'Total revenue ($)', 'sales_tier': ''},
        color_discrete_sequence=['#94d1ce']
    )
    fig_tier_rev.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=0, r=0, t=10, b=0),
        yaxis=dict(gridcolor='#f0f0f0', tickprefix='$', tickformat=',.0f'),
        xaxis=dict(gridcolor='#f0f0f0'),
    )
    st.markdown("**Total revenue by sales tier**")
    st.plotly_chart(fig_tier_rev, use_container_width=True)

# Customer insights
st.markdown('<div class="section-title">Customer insights</div>', unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1])

with col_left:
    seg_data = (
        filtered.groupby('customer_segment')['sales_amount']
        .mean()
        .reindex(['New', 'Returning', 'Loyal', 'VIP'])
        .reset_index()
    )
    fig_seg = px.bar(
        seg_data,
        x='customer_segment',
        y='sales_amount',
        labels={'sales_amount': 'Avg order value ($)', 'customer_segment': ''},
        color_discrete_sequence=['#0d9488']
    )
    fig_seg.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=0, r=0, t=10, b=0),
        yaxis=dict(gridcolor='#f0f0f0', tickprefix='$', tickformat=',.2f'),
        xaxis=dict(gridcolor='#f0f0f0'),
    )
    st.markdown("**Avg order value by customer segment**")
    st.plotly_chart(fig_seg, use_container_width=True)

with col_right:
    age_gender = (
        filtered.groupby(['customer_age_group', 'customer_gender'])['sales_amount']
        .count()
        .reset_index()
        .rename(columns={'sales_amount': 'transactions'})
    )
    fig_age = px.bar(
        age_gender,
        x='customer_age_group',
        y='transactions',
        color='customer_gender',
        barmode='group',
        labels={'transactions': 'Transactions', 'customer_age_group': '', 'customer_gender': ''},
        color_discrete_map={'Male': '#0d9488', 'Female': '#94d1ce', 'Other': '#e2f5f3'}
    )
    fig_age.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=0, r=0, t=10, b=0),
        yaxis=dict(gridcolor='#f0f0f0'),
        xaxis=dict(gridcolor='#f0f0f0'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    st.markdown("**Transactions by age group and gender**")
    st.plotly_chart(fig_age, use_container_width=True)

# Channel & payment
st.markdown('<div class="section-title">Channel & payment</div>', unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1])

with col_left:
    channel_data = (
        filtered.groupby('sales_channel')['sales_amount']
        .sum()
        .reset_index()
    )
    fig_channel = px.pie(
        channel_data,
        names='sales_channel',
        values='sales_amount',
        hole=0.5,
        color_discrete_sequence=['#0d9488', '#94d1ce', '#d1f0ed']
    )
    fig_channel.update_layout(
        paper_bgcolor='white',
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5)
    )
    fig_channel.update_traces(textposition='inside', textinfo='percent+label')
    st.markdown("**Revenue share by sales channel**")
    st.plotly_chart(fig_channel, use_container_width=True)

with col_right:
    payment_data = (
        filtered.groupby('payment_method')['sales_amount']
        .sum()
        .reset_index()
        .sort_values('sales_amount', ascending=True)
    )
    fig_pay = px.bar(
        payment_data,
        x='sales_amount',
        y='payment_method',
        orientation='h',
        labels={'sales_amount': 'Revenue ($)', 'payment_method': ''},
        color_discrete_sequence=['#0d9488']
    )
    fig_pay.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(gridcolor='#f0f0f0', tickprefix='$', tickformat=',.0f'),
        yaxis=dict(gridcolor='#f0f0f0'),
    )
    st.markdown("**Revenue by payment method**")
    st.plotly_chart(fig_pay, use_container_width=True)

# Discount analysis
st.markdown('<div class="section-title">Discount analysis</div>', unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1])

with col_left:
    disc_compare = (
        filtered.groupby('has_discount')['sales_amount']
        .mean()
        .reset_index()
    )
    disc_compare['label'] = disc_compare['has_discount'].map({True: 'With discount', False: 'No discount'})

    fig_disc = px.bar(
        disc_compare,
        x='label',
        y='sales_amount',
        labels={'sales_amount': 'Avg order value ($)', 'label': ''},
        color_discrete_sequence=['#0d9488', '#94d1ce'],
        color='label'
    )
    fig_disc.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=0, r=0, t=10, b=0),
        yaxis=dict(gridcolor='#f0f0f0', tickprefix='$', tickformat=',.2f'),
        xaxis=dict(gridcolor='#f0f0f0'),
        showlegend=False
    )
    st.markdown("**Avg order value — discounted vs full price**")
    st.plotly_chart(fig_disc, use_container_width=True)

with col_right:
    seg_disc = (
        filtered.groupby('customer_segment')['has_discount']
        .mean()
        .mul(100)
        .reindex(['New', 'Returning', 'Loyal', 'VIP'])
        .reset_index()
    )
    fig_seg_disc = px.bar(
        seg_disc,
        x='customer_segment',
        y='has_discount',
        labels={'has_discount': 'Discount rate (%)', 'customer_segment': ''},
        color_discrete_sequence=['#94d1ce']
    )
    fig_seg_disc.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=0, r=0, t=10, b=0),
        yaxis=dict(gridcolor='#f0f0f0', ticksuffix='%'),
        xaxis=dict(gridcolor='#f0f0f0'),
    )
    st.markdown("**Discount rate by customer segment**")
    st.plotly_chart(fig_seg_disc, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#9ca3af; font-size:12px;'>"
    "Retail Sales Dashboard · Built with Python & Streamlit · Data: 2024–2025"
    "</p>",
    unsafe_allow_html=True
)