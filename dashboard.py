import json
from datetime import timedelta
import redis
import streamlit as st
from data import config
from helpers import format_number

# st.title('Dashboard')
from iex import IEXStock

redis_client = redis.Redis(host='localhost', port=6379, db=0)

symbol = st.sidebar.text_input('Symbol', value='AAPL')

stock = IEXStock(config.API_TOKEN, symbol)
screen = st.sidebar.selectbox('View', ('Overview', 'Fundamentals', 'News', 'Ownership', 'Technicals'), index=0)

st.write(symbol)

st.title(screen)
if screen == 'Overview':

    logo_key = f'{symbol}_logo'
    logo = redis_client.get(logo_key)

    if logo is None:
        print('could not find logo in cache, retrieving from IEX Cloud API')
        logo = stock.get_logo()
        redis_client.set(logo_key, json.dumps(logo))
    else:
        print('found logo in cache, serving from redis')
        logo = json.loads(logo)

    company_key = f'{symbol}_company'
    company = redis_client.get(company_key)

    if company is None:
        print('getting info from IEX Cloud')
        company = stock.get_company_info()
        redis_client.set(company_key, json.dumps(company))
        redis_client.expire(company_key, timedelta(seconds=30))
    else:
        print('getting info from cache')
        company = json.loads(company)

    col1, col2 = st.beta_columns([1, 4])

    with col1:
        st.image(logo['url'])

    with col2:
        st.subheader('Company')
        st.write(company['companyName'])
        st.subheader('Sector')
        st.write(company['sector'])
        st.subheader('Industry')
        st.write(company['industry'])
        st.subheader('Description')
        st.write(company['description'])
        st.subheader('CEO')
        st.write(company['CEO'])
        st.subheader('Site')
        st.write(company['website'])

if screen == 'Fundamentals':
    stats = stock.get_stats()
    st.subheader('Total Cash')
    st.write(format_number(stats['totalCash']))
    st.write(stats)
