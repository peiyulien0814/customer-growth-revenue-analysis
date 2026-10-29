"""Portfolio dashboard | UCI real dataset only; run streamlit run app.py."""
from pathlib import Path
import json
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'outputs'
st.set_page_config(page_title='Retail Growth | Business Analytics',page_icon='📊',layout='wide',initial_sidebar_state='expanded')
st.markdown('''<style>.block-container{padding-top:2rem;max-width:1250px}.small-note{color:#65758a;font-size:0.87rem}h1{letter-spacing:-.04em}div[data-testid="stMetric"]{background:#f1f5f9;padding:16px;border-radius:12px;border:1px solid #dce4ed}div[data-testid="stMetricLabel"]{color:#475569}</style>''',unsafe_allow_html=True)
@st.cache_data
def load():
    k=json.loads((DATA/'kpis.json').read_text())
    df={name:pd.read_csv(DATA/f'{name}.csv') for name in ('monthly_sales','country_sales','top_products','customer_rfm','cohort_repeat')}
    return k,df
k,d=load()
colors=['#155e75','#0d9488','#f59e0b','#334155']
page=st.sidebar.radio('Explore the analysis',['Executive overview','Sales & product mix','Customer insights','Recommendations & methodology'])
st.sidebar.divider()
st.sidebar.caption('SOURCE · UCI Online Retail (2010–2011)\n\nReal historical transactions · British pounds (GBP). No demo data.')
st.sidebar.caption('Scope: positive sales only; refunds excluded, not net revenue.')
st.title('Customer Growth & Revenue Analysis')
st.caption('A business analytics case study using 541,909 real historical online retail records · Python · SQL · Excel · Streamlit')
if page=='Executive overview':
    a,b,c,e=st.columns(4)
    a.metric('Positive-sales amount',f"£{k['sales_gbp']/1e6:.2f}M")
    b.metric('Sales invoices',f"{k['orders']:,}")
    c.metric('Avg. amount / invoice',f"£{k['average_order_value_gbp']:,.2f}")
    e.metric('Identified customers',f"{k['identified_customers']:,}")
    st.subheader('Monthly positive sales')
    monthly=d['monthly_sales'].copy()
    fig=px.line(monthly,x='month',y='sales_gbp',markers=True,labels={'month':'Invoice month','sales_gbp':'Positive sales (£)'})
    fig.update_traces(line_color=colors[0],line_width=3)
    fig.update_layout(height=370,hovermode='x unified')
    st.plotly_chart(fig,use_container_width=True)
    st.warning('December 2010 and December 2011 are partial observation months; 2011-12 ends on December 9. Do not treat month-to-month differences as causal growth.')
    a,b,c=st.columns(3)
    a.info('**84.6% UK share**\n\n£9.03M of positive sales came from the United Kingdom.')
    b.info('**£1.51M in November 2011**\n\nHighest observed monthly positive sales total.')
    c.info('**65.6% repeat purchasers**\n\n2,845 of 4,338 identifiable customers had at least two orders.')
    st.caption('These are observations and hypotheses, not proven marketing impact. See Methodology for data limitations.')
elif page=='Sales & product mix':
    a,b=st.columns([1,1])
    with a:
        st.subheader('Country concentration')
        df=d['country_sales'].head(12)
        fig=px.bar(df.sort_values('sales_gbp'),x='sales_gbp',y='country',orientation='h',color_discrete_sequence=[colors[0]],labels={'sales_gbp':'Positive sales (£)','country':''})
        fig.update_layout(height=430)
        st.plotly_chart(fig,use_container_width=True)
    with b:
        st.subheader('Product & fee line-items')
        data=d['top_products'].copy()
        fee_pat=r'POSTAGE|DISCOUNT|CARRIAGE|BANK CHARGES|MANUAL|ADJUST|AMAZON FEE|DOTCOM|SAMPLES'
        merch_only=st.checkbox('Exclude likely non-merchandise items',value=True)
        if merch_only:data=data[~data['product'].fillna('').str.contains(fee_pat,case=False,regex=True)]
        fig=px.bar(data.head(10).sort_values('sales_gbp'),x='sales_gbp',y='product',orientation='h',color_discrete_sequence=[colors[1]],labels={'sales_gbp':'Positive sales (£)','product':''})
        fig.update_layout(height=430,yaxis={'tickfont':{'size':10}})
        st.plotly_chart(fig,use_container_width=True)
        st.caption('Filter is heuristic. A full merchandising audit must classify shipping, adjustments and unusual one-off transactions.')
    st.subheader('What should the business investigate?')
    st.write('Assess demand by market and product category. Review seasonality and validate whether large one-off orders or postage entries distort product rankings.')
elif page=='Customer insights':
    a,b=st.columns([1.2,1])
    with a:
        st.subheader('Repeat purchase by first-order cohort')
        fig=px.bar(d['cohort_repeat'],x='cohort',y='repeat_pct',color_discrete_sequence=[colors[0]],labels={'cohort':'First observed order month','repeat_pct':'% with 2+ orders'})
        fig.update_layout(height=380)
        st.plotly_chart(fig,use_container_width=True)
        st.caption('Later cohorts have less time to repeat. This is NOT a censoring-adjusted retention curve.')
    with b:
        st.subheader('Customer metrics: RFM')
        r=d['customer_rfm']
        st.metric('Purchasers with 2+ invoices','2,845 / 4,338')
        st.metric('Missing customer IDs (sale lines)','132,220')
        st.write('RFM stands for Recency, Frequency and Monetary value. It is an exploratory way to understand customer purchasing patterns.')
    st.subheader('Inspect customers (identified orders only)')
    n=st.slider('Customers to display',10,100,25,step=5)
    st.dataframe(d['customer_rfm'].head(n),hide_index=True,use_container_width=True)
    st.download_button('Download RFM CSV',d['customer_rfm'].to_csv(index=False),'customer_rfm.csv','text/csv')
else:
    st.subheader('Business recommendations: test, do not assume')
    for heading,observation,test,kpi in [
        ('01 · Repeat-purchase experiment','65.6% of identified customers ordered twice or more during the observation period.','Randomize eligible first-time customers to a follow-up reminder versus control.','30/60-day repeat order rate; incremental revenue per eligible customer.'),
        ('02 · Basket-size experiment','Average positive-sales value per invoice is £534.40, but costs and margins are unknown.','Test a shipping threshold or bundle against the status quo after collecting unit-level margin.','Average order value and contribution margin (both required).'),
        ('03 · Catalog and identity quality','Some top stock codes are charges; 132,220 included sales lines have no customer ID.','Classify non-merchandise rows and audit anonymous-customer coverage.','Product-ranking accuracy and percent of transactions with an ID.')]:
        with st.expander(heading,expanded=True):
            st.write('**Evidence:** '+observation)
            st.write('**Proposed test:** '+test)
            st.write('**Success metric:** '+kpi)
    st.divider()
    st.subheader('Source and method')
    st.write('**Dataset:** UCI Online Retail, Dec 2010–Dec 2011, 541,909 raw rows, licensed CC BY 4.0. Reference: Chen, D., Online Retail, DOI: 10.24432/C5BW33.')
    st.write('**Included records:** 530,104 positive-sale line items; remove invoices marked as cancellations, quantities ≤ 0 and unit prices ≤ 0. Revenue = Quantity × UnitPrice. An invoice is a distinct non-cancelled invoice number. Customer RFM excludes missing IDs.')
    st.write('**Limitations:** Positive sales are not net revenue (returns not reconciled) or profit. There is no advertising spend, web-visit traffic, production cost, or randomized trial; therefore this data cannot establish marketing ROI, web conversion rate, margin or causal impact. Missing customer IDs affect customer analysis.')
    st.markdown('[Original dataset — UCI](https://archive.ics.uci.edu/dataset/352/online+retail)')
