"""
Banking Notification Generator - Streamlit App
==============================================

Simple web interface to demonstrate the banking notification system.
Shows example data and provides a button to run all demos.
"""

import streamlit as st
import pandas as pd
from azure_notification_generator import run_all_demos, generate_notification
from core_prompts import get_available_products

# Page configuration
st.set_page_config(
    page_title="Banking Notification Generator",
    page_icon="🏦",
    layout="wide"
)

# Main title
st.title("🏦 Banking Notification Generator")
st.markdown("---")

# Sidebar with info
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This system generates personalized banking push notifications using Azure OpenAI.
    
    **Features:**
    - 10 banking products
    - Personalized TOV based on age/status
    - Behavioral analysis
    - Russian banking guidelines
    """)
    
    st.header("📊 Data Overview")
    st.metric("Clients", "60")
    st.metric("Transactions", "17,400")
    st.metric("Transfers", "18,000")
    st.metric("Products", "10")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📋 All Example Data for Generation")
    
    # All example client data used in demos
    all_example_data = [
        {
            "Product": "Карта для путешествий",
            "client_code": 123,
            "name": "Алия",
            "status": "Зарплатный клиент",
            "age": 28,
            "city": "Алматы",
            "avg_monthly_balance_KZT": 450000,
            "taxi_rides_count": 12,
            "taxi_spent_amount": 27400,
            "travel_spent_amount": 150000,
            "hotels_spent_amount": 80000,
            "month": "август"
        },
        {
            "Product": "Премиальная карта",
            "client_code": 456,
            "name": "Елена",
            "status": "Премиальный клиент",
            "age": 45,
            "city": "Нур-Султан",
            "avg_monthly_balance_KZT": 2000000,
            "restaurants_spent": 100000,
            "cosmetics_spent": 50000,
            "jewelry_spent": 200000,
            "atm_withdrawals_count": 2,
            "transfers_count": 25
        },
        {
            "Product": "Карта для путешествий (Студент)",
            "client_code": 789,
            "name": "Айдар",
            "status": "Студент",
            "age": 22,
            "city": "Алматы",
            "avg_monthly_balance_KZT": 50000,
            "taxi_rides_count": 8,
            "taxi_spent_amount": 15000,
            "travel_spent_amount": 30000,
            "hotels_spent_amount": 0,
            "month": "сентябре"
        },
        {
            "Product": "Кредитная карта",
            "client_code": 101,
            "name": "Данияр",
            "status": "Зарплатный клиент",
            "age": 35,
            "city": "Астана",
            "avg_monthly_balance_KZT": 200000,
            "top_category_1": "Продукты питания",
            "top_category_2": "Такси",
            "top_category_3": "Кино",
            "online_services_spent": 25000,
            "installment_payments": True,
            "cc_repayments": False
        },
        {
            "Product": "Обмен валют",
            "client_code": 102,
            "name": "Руслан",
            "status": "Премиальный клиент",
            "age": 48,
            "city": "Алматы",
            "avg_monthly_balance_KZT": 3000000,
            "fx_buy_count": 5,
            "fx_sell_count": 2,
            "usd_spent": 5000,
            "eur_spent": 3000,
            "main_foreign_currency": "USD"
        },
        {
            "Product": "Кредит наличными",
            "client_code": 103,
            "name": "Тимур",
            "status": "Зарплатный клиент",
            "age": 36,
            "city": "Караганда",
            "avg_monthly_balance_KZT": 150000,
            "monthly_inflow": 200000,
            "monthly_outflow": 180000,
            "loan_payments_count": 2,
            "low_balance_days": 5,
            "cash_need_indicators": "high_outflow"
        },
        {
            "Product": "Депозит мультивалютный",
            "client_code": 104,
            "name": "Елена",
            "status": "Премиальный клиент",
            "age": 45,
            "city": "Алматы",
            "avg_monthly_balance_KZT": 2500000,
            "free_balance": 500000,
            "fx_activity_score": 8,
            "foreign_spending": 100000,
            "deposit_fx_topup_count": 3,
            "deposit_fx_withdraw_count": 1
        },
        {
            "Product": "Депозит сберегательный",
            "client_code": 105,
            "name": "Мадина",
            "status": "Зарплатный клиент",
            "age": 33,
            "city": "Астана",
            "avg_monthly_balance_KZT": 1200000,
            "stable_balance": 800000,
            "spending_volatility": 3,
            "deposit_topup_count": 1,
            "deposit_withdraw_count": 0,
            "balance_stability_score": 9
        },
        {
            "Product": "Депозит накопительный",
            "client_code": 106,
            "name": "Сабина",
            "status": "Студент",
            "age": 22,
            "city": "Алматы",
            "avg_monthly_balance_KZT": 80000,
            "regular_balance": 50000,
            "periodic_topups": True,
            "topup_frequency": 4,
            "savings_behavior_score": 7,
            "small_regular_amounts": 10000
        },
        {
            "Product": "Инвестиции",
            "client_code": 107,
            "name": "Арман",
            "status": "Премиальный клиент",
            "age": 55,
            "city": "Алматы",
            "avg_monthly_balance_KZT": 4000000,
            "available_funds": 300000,
            "invest_in_count": 2,
            "invest_out_count": 0,
            "investment_interest_score": 8,
            "risk_tolerance": 6
        },
        {
            "Product": "Золотые слитки",
            "client_code": 108,
            "name": "Камилла",
            "status": "Премиальный клиент",
            "age": 45,
            "city": "Алматы",
            "avg_monthly_balance_KZT": 2000000,
            "high_liquidity": True,
            "gold_buy_count": 1,
            "gold_sell_count": 0,
            "jewelry_spent": 150000,
            "value_preservation_interest": 9
        }
    ]
    
    # Display all example data as DataFrame
    df = pd.DataFrame(all_example_data)
    st.dataframe(df, width='stretch')
    
    st.header("🎯 Available Banking Products")
    products = get_available_products()
    
    # Display products in a nice format
    for i, product in enumerate(products, 1):
        st.write(f"{i}. **{product}**")

with col2:
    st.header("🚀 Demo Controls")
    
    st.markdown("Click the button below to run all notification demos and see the system in action.")
    
    # Demo button
    if st.button("🎬 Run All Demos", type="primary", width='stretch'):
        st.markdown("---")
        st.header("📱 Generated Notifications")
        
        # Create a placeholder for the demo output
        demo_placeholder = st.empty()
        
        with demo_placeholder.container():
            st.markdown("**Running demos...**")
            
            # Capture the demo output
            import io
            import sys
            from contextlib import redirect_stdout, redirect_stderr
            
            # Redirect stdout to capture demo output
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = io.StringIO()
            sys.stderr = io.StringIO()
            
            try:
                # Run the demos
                run_all_demos()
                
                # Get the captured output
                demo_output = sys.stdout.getvalue()
                error_output = sys.stderr.getvalue()
                
            finally:
                # Restore stdout/stderr
                sys.stdout = old_stdout
                sys.stderr = old_stderr
            
            # Display the captured output
            if demo_output:
                st.text(demo_output)
            if error_output:
                st.error(f"Errors: {error_output}")
    
    st.markdown("---")
    st.markdown("### 🔧 Technical Details")
    st.markdown("""
    - **Framework**: Streamlit
    - **AI Model**: Azure OpenAI GPT-4o-mini
    - **Language**: Python
    - **Data**: 3 months of financial behavior
    """)

# Footer
st.markdown("---")
st.markdown("Built for Decentrathon 4 BCC Competition | Case 1: Personalized Banking Notifications")
