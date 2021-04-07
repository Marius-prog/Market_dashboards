import json
from datetime import timedelta, datetime
import redis
import streamlit as st
from data import config
from helpers import format_number
from iex import IEXStock

redis_client = redis.Redis(host='localhost', port=6379, db=0)

symbol = st.sidebar.text_input('Symbol', value='AAPL')

stock = IEXStock(config.API_TOKEN, symbol)

screen = st.sidebar.selectbox('View', ('Overview', 'Fundamentals', 'News', 'Ownership', 'Technicals', 'Charts'),
                              index=0)

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

if screen == 'News':
    news_key = f"{symbol}_news"
    news = redis_client.get(news_key)

    if news is not None:
        news = json.loads(news)
    else:
        news = stock.get_company_news()
        redis_client.set(news_key, json.dumps(news))

    for article in news:
        st.subheader(article['headline'])
        dt = datetime.utcfromtimestamp(article['datetime'] / 1000).isoformat()
        st.write(f"Posted by {article['source']} at {dt}")
        st.write(article['url'])
        st.write(article['summary'])
        st.image(article['image'])

# if screen == 'Fundamentals':
#     stats = stock.get_stats()
#     st.subheader('Total Cash')
#     st.write(format_number(stats['totalCash']))
#     st.write(stats)


if screen == 'Fundamentals':
    stats_key = f"{symbol}_stats"
    stats = redis_client.get(stats_key)

    if stats is None:
        stats = stock.get_stats()
        redis_client.set(stats_key, json.dumps(stats))
    else:
        stats = json.loads(stats)

    st.header('Ratios')

    col1, col2 = st.beta_columns(2)

    with col1:
        st.subheader('P/E')
        st.write(stats['peRatio'])
        st.subheader('Forward P/E')
        st.write(stats['forwardPERatio'])
        st.subheader('PEG Ratio')
        st.write(stats['pegRatio'])
        st.subheader('Price to Sales')
        st.write(stats['priceToSales'])
        st.subheader('Price to Book')
        st.write(stats['priceToBook'])
    with col2:
        st.subheader('Revenue')
        st.write(format_number(stats['revenue']))
        st.subheader('Cash')
        st.write(format_number(stats['totalCash']))
        st.subheader('Debt')
        st.write(format_number(stats['currentDebt']))
        st.subheader('200 Day Moving Average')
        st.write(stats['day200MovingAvg'])
        st.subheader('50 Day Moving Average')
        st.write(stats['day50MovingAvg'])

    fundamentals_cache_key = f"{symbol}_fundamentals"
    fundamentals = redis_client.get(fundamentals_cache_key)

    if fundamentals is None:
        fundamentals = stock.get_fundamentals('quarterly')
        redis_client.set(fundamentals_cache_key, json.dumps(fundamentals))
    else:
        fundamentals = json.loads(fundamentals)

    for quarter in fundamentals:
        st.header(f"Q{quarter['fiscalQuarter']} {quarter['fiscalYear']}")
        st.subheader('Filing Date')
        st.write(quarter['filingDate'])
        st.subheader('Revenue')
        st.write(format_number(quarter['revenue']))
        st.subheader('Net Income')
        st.write(format_number(quarter['incomeNet']))

    st.header("Dividends")

    dividends_cache_key = f"{symbol}_dividends"
    dividends = redis_client.get(dividends_cache_key)

    if dividends is None:
        dividends = stock.get_dividends()
        redis_client.set(dividends_cache_key, json.dumps(dividends))
    else:
        dividends = json.loads(dividends)

    for dividend in dividends:
        st.write(dividend['paymentDate'])
        st.write(dividend['amount'])

if screen == 'Ownership':
    st.subheader("Institutional Ownership")

    institutional_ownership_key = f"{symbol}_institutional"
    institutional_ownership = redis_client.get(institutional_ownership_key)

    if institutional_ownership is None:
        institutional_ownership = stock.get_institutional_ownership()
        redis_client.set(institutional_ownership_key, json.dumps(institutional_ownership))
    else:
        print("getting inst ownership from cache")
        institutional_ownership = json.loads(institutional_ownership)

    for institution in institutional_ownership:
        st.write(institution['date'])
        st.write(institution['entityProperName'])
        st.write(institution['reportedHolding'])

    st.subheader("Insider Transactions")

    insider_transactions_cache_key = f"{symbol}_insider_transactions"

    insider_transactions = redis_client.get(insider_transactions_cache_key)
    if insider_transactions is None:
        insider_transactions = stock.get_insider_transactions()
        redis_client.set(insider_transactions_cache_key, json.dumps(insider_transactions))
    else:
        print("getting insider transactions from cache")
        insider_transactions = json.loads(insider_transactions)

    for transaction in insider_transactions:
        st.write(transaction['filingDate'])
        st.write(transaction['fullName'])
        st.write(transaction['transactionShares'])
        st.write(transaction['transactionPrice'])