"""
Azure OpenAI Banking Notification Generator
==========================================

This file handles Azure OpenAI integration for generating banking push notifications.
Uses core_prompts.py for prompt definitions.
"""

import os
import dotenv
from langchain_openai import AzureChatOpenAI
import json
from core_prompts import get_prompt_for_product, format_prompt_with_data, get_available_products

# =============================================================================
# AZURE OPENAI CONFIGURATION
# =============================================================================

# Load environment variables from .env file
dotenv.load_dotenv()

# Get Azure OpenAI configuration
api_key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

def get_azure_llm():
    """Initialize and return Azure OpenAI LLM instance"""
    if not all([api_key, endpoint, api_version]):
        raise ValueError("Missing required Azure OpenAI environment variables")
    
    return AzureChatOpenAI(
        api_key=api_key,
        azure_endpoint=endpoint,
        api_version=api_version,
        azure_deployment="gpt-4o-mini",
        temperature=0.7
    )

# =============================================================================
# NOTIFICATION GENERATION
# =============================================================================

def generate_notification(product_name: str, **client_data) -> dict:
    """
    Generate a personalized push notification using Azure OpenAI.
    
    Args:
        product_name: Name of the banking product
        **client_data: Client and product-specific data
        
    Returns:
        Dictionary with client_code, product, and push_notification
    """
    try:
        # Get the prompt for the product
        prompt = get_prompt_for_product(product_name)
        
        # Format the prompt with client data
        formatted_prompt = format_prompt_with_data(prompt, **client_data)
        
        # Initialize Azure OpenAI LLM
        llm = get_azure_llm()
        
        # Generate the notification
        response = llm.invoke(formatted_prompt)
        
        # Parse the JSON response (handle markdown formatting)
        content = response.content.strip()
        if content.startswith('```json'):
            # Remove markdown formatting
            content = content[7:]  # Remove ```json
            if content.endswith('```'):
                content = content[:-3]  # Remove ```
        elif content.startswith('```'):
            # Remove generic markdown formatting
            content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
        
        result = json.loads(content.strip())
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        print(f"Raw response: {response.content}")
        return {
            "client_code": client_data.get('client_code', 0),
            "product": product_name,
            "push_notification": "Ошибка генерации уведомления"
        }
    except Exception as e:
        print(f"Error generating notification: {e}")
        return {
            "client_code": client_data.get('client_code', 0),
            "product": product_name,
            "push_notification": "Ошибка генерации уведомления"
        }

# =============================================================================
# DEMO AND EXAMPLES
# =============================================================================

def demo_travel_card():
    """Demo travel card notification"""
    print("=== TRAVEL CARD DEMO ===")
    
    client_data = {
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
    }
    
    result = generate_notification("Карта для путешествий", **client_data)
    print(f"Client: {client_data['name']}, {client_data['status']}, {client_data['age']} лет")
    print(f"Notification: {result['push_notification']}")

def demo_premium_card():
    """Demo premium card notification"""
    print("\n=== PREMIUM CARD DEMO ===")
    
    client_data = {
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
    }
    
    result = generate_notification("Премиальная карта", **client_data)
    print(f"Client: {client_data['name']}, {client_data['status']}, {client_data['age']} лет")
    print(f"Notification: {result['push_notification']}")

def demo_young_student():
    """Demo notification for young student"""
    print("\n=== YOUNG STUDENT DEMO ===")
    
    client_data = {
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
    }
    
    result = generate_notification("Карта для путешествий", **client_data)
    print(f"Client: {client_data['name']}, {client_data['status']}, {client_data['age']} лет")
    print(f"Notification: {result['push_notification']}")

def demo_credit_card():
    """Demo credit card notification"""
    print("\n=== CREDIT CARD DEMO ===")
    
    client_data = {
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
    }
    
    result = generate_notification("Кредитная карта", **client_data)
    print(f"Client: {client_data['name']}, {client_data['status']}, {client_data['age']} лет")
    print(f"Notification: {result['push_notification']}")

def demo_currency_exchange():
    """Demo currency exchange notification"""
    print("\n=== CURRENCY EXCHANGE DEMO ===")
    
    client_data = {
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
    }
    
    result = generate_notification("Обмен валют", **client_data)
    print(f"Client: {client_data['name']}, {client_data['status']}, {client_data['age']} лет")
    print(f"Notification: {result['push_notification']}")

def demo_cash_loan():
    """Demo cash loan notification"""
    print("\n=== CASH LOAN DEMO ===")
    
    client_data = {
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
    }
    
    result = generate_notification("Кредит наличными", **client_data)
    print(f"Client: {client_data['name']}, {client_data['status']}, {client_data['age']} лет")
    print(f"Notification: {result['push_notification']}")

def demo_multi_currency_deposit():
    """Demo multi-currency deposit notification"""
    print("\n=== MULTI-CURRENCY DEPOSIT DEMO ===")
    
    client_data = {
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
    }
    
    result = generate_notification("Депозит мультивалютный", **client_data)
    print(f"Client: {client_data['name']}, {client_data['status']}, {client_data['age']} лет")
    print(f"Notification: {result['push_notification']}")

def demo_savings_deposit():
    """Demo savings deposit notification"""
    print("\n=== SAVINGS DEPOSIT DEMO ===")
    
    client_data = {
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
    }
    
    result = generate_notification("Депозит сберегательный", **client_data)
    print(f"Client: {client_data['name']}, {client_data['status']}, {client_data['age']} лет")
    print(f"Notification: {result['push_notification']}")

def demo_accumulative_deposit():
    """Demo accumulative deposit notification"""
    print("\n=== ACCUMULATIVE DEPOSIT DEMO ===")
    
    client_data = {
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
    }
    
    result = generate_notification("Депозит накопительный", **client_data)
    print(f"Client: {client_data['name']}, {client_data['status']}, {client_data['age']} лет")
    print(f"Notification: {result['push_notification']}")

def demo_investments():
    """Demo investments notification"""
    print("\n=== INVESTMENTS DEMO ===")
    
    client_data = {
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
    }
    
    result = generate_notification("Инвестиции", **client_data)
    print(f"Client: {client_data['name']}, {client_data['status']}, {client_data['age']} лет")
    print(f"Notification: {result['push_notification']}")

def demo_gold_bars():
    """Demo gold bars notification"""
    print("\n=== GOLD BARS DEMO ===")
    
    client_data = {
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
    
    result = generate_notification("Золотые слитки", **client_data)
    print(f"Client: {client_data['name']}, {client_data['status']}, {client_data['age']} лет")
    print(f"Notification: {result['push_notification']}")

def show_available_products():
    """Show all available products"""
    print("\n=== AVAILABLE PRODUCTS ===")
    products = get_available_products()
    for i, product in enumerate(products, 1):
        print(f"{i}. {product}")

def run_all_demos():
    """Run all demo examples"""
    print("🏦 BANKING NOTIFICATION GENERATOR DEMO")
    print("=" * 50)
    
    try:
        # Show available products
        show_available_products()
        
        # Run all 10 product demos
        demo_travel_card()
        demo_premium_card()
        demo_young_student()
        demo_credit_card()
        demo_currency_exchange()
        demo_cash_loan()
        demo_multi_currency_deposit()
        demo_savings_deposit()
        demo_accumulative_deposit()
        demo_investments()
        demo_gold_bars()
        
        print("\n✅ Demo completed successfully!")
        print("\nTo generate your own notifications:")
        print("1. Import: from azure_notification_generator import generate_notification")
        print("2. Call: result = generate_notification('Product Name', **client_data)")
        print("3. Access: result['push_notification']")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("Make sure your .env file contains valid Azure OpenAI credentials.")

if __name__ == "__main__":
    run_all_demos()
