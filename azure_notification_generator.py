"""
Azure OpenAI Banking Notification Generator
==========================================

This file handles Azure OpenAI integration for generating banking push notifications.
Uses core_prompts.py for prompt definitions and processes product_classification.json data.
"""

import os
import dotenv
from langchain_openai import AzureChatOpenAI
import json
import csv
from datetime import datetime
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
# DATA PROCESSING FUNCTIONS
# =============================================================================

def load_client_data(json_file_path: str) -> list:
    """Load client data from product_classification.json"""
    with open(json_file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def normalize_product_name(product_type: str) -> str:
    """Normalize product names to match core_prompts.py definitions"""
    product_mapping = {
        "Депозит Мультивалютный": "Депозит мультивалютный",
        "Депозит Сберегательный": "Депозит сберегательный", 
        "Депозит Накопительный": "Депозит накопительный"
    }
    return product_mapping.get(product_type, product_type)

def extract_product_specific_data(client_data: dict, product_type: str) -> dict:
    """
    Extract product-specific data from client data based on product type.
    Maps the JSON structure to the format expected by core_prompts.py
    """
    # Normalize product type for consistent matching
    normalized_product_type = normalize_product_name(product_type)
    
    base_data = {
        'client_code': client_data['client_code'],
        'name': client_data['name'],
        'status': client_data['status'],
        'age': client_data['age'],
        'city': client_data['city'],
        'avg_monthly_balance_KZT': client_data['avg_monthly_balance'],
        'currencies': client_data.get('currencies', ['KZT'])
    }
    
    # Get current month for personalization
    current_month = datetime.now().strftime('%B').lower()
    month_names = {
        'january': 'январе', 'february': 'феврале', 'march': 'марте',
        'april': 'апреле', 'may': 'мае', 'june': 'июне',
        'july': 'июле', 'august': 'августе', 'september': 'сентябре',
        'october': 'октябре', 'november': 'ноябре', 'december': 'декабре'
    }
    month = month_names.get(current_month, 'августе')
    
    category_spending = client_data['top_5_category_spending']
    type_spending = client_data['top_5_type_spending']
    
    if normalized_product_type == "Карта для путешествий":
        return {
            **base_data,
            'taxi_rides_count': int(category_spending.get('Такси', 0) / 2000),  # Estimate rides
            'taxi_spent_amount': category_spending.get('Такси', 0),
            'travel_spent_amount': category_spending.get('Путешествия', 0),
            'hotels_spent_amount': category_spending.get('Отели', 0),
            'month': month
        }
    
    elif normalized_product_type == "Премиальная карта":
        return {
            **base_data,
            'restaurants_spent': category_spending.get('Кафе и рестораны', 0),
            'cosmetics_spent': category_spending.get('Косметика и Парфюмерия', 0),
            'jewelry_spent': category_spending.get('Ювелирные украшения', 0),
            'atm_withdrawals_count': int(type_spending.get('atm_withdrawal', 0) / 50000),  # Estimate count
            'transfers_count': int(type_spending.get('p2p_out', 0) / 100000)  # Estimate count
        }
    
    elif normalized_product_type == "Кредитная карта":
        # Get top 3 categories
        sorted_categories = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)
        top_categories = [cat[0] for cat in sorted_categories[:3]]
        
        return {
            **base_data,
            'top_category_1': top_categories[0] if len(top_categories) > 0 else 'Продукты питания',
            'top_category_2': top_categories[1] if len(top_categories) > 1 else 'Кафе и рестораны',
            'top_category_3': top_categories[2] if len(top_categories) > 2 else 'Такси',
            'online_services_spent': (
                category_spending.get('Едим дома', 0) + 
                category_spending.get('Смотрим дома', 0) + 
                category_spending.get('Играем дома', 0)
            ),
            'installment_payments': 'installment_payment_out' in type_spending,
            'cc_repayments': 'cc_repayment_out' in type_spending
        }
    
    elif normalized_product_type == "Обмен валют":
        # Determine main foreign currency based on client's actual currencies
        client_currencies = client_data.get('currencies', ['KZT'])
        foreign_currencies = [curr for curr in client_currencies if curr != 'KZT']
        
        if foreign_currencies:
            # Client has foreign currencies, use the first one
            main_foreign_currency = foreign_currencies[0]
        else:
            # Client only has KZT, don't suggest specific foreign currency
            main_foreign_currency = 'иностранной валюте'
        
        # Always provide the required fields for the prompt
        result_data = {
            **base_data,
            'fx_buy_count': int(type_spending.get('fx_buy', 0) / 1000000),  # Estimate count
            'fx_sell_count': int(type_spending.get('fx_sell', 0) / 1000000),  # Estimate count
            'main_foreign_currency': main_foreign_currency
        }
            
        return result_data
    
    elif normalized_product_type == "Кредит наличными":
        monthly_inflow = type_spending.get('salary_in', 0)
        monthly_outflow = type_spending.get('card_out', 0)
        
        return {
            **base_data,
            'monthly_inflow': monthly_inflow,
            'monthly_outflow': monthly_outflow,
            'loan_payments_count': int(type_spending.get('loan_payment_out', 0) / 100000),  # Estimate count
            'low_balance_days': 15 if monthly_outflow > monthly_inflow * 1.2 else 5,  # Estimate
            'cash_need_indicators': monthly_outflow > monthly_inflow * 1.1
        }
    
    elif normalized_product_type == "Депозит мультивалютный":
        return {
            **base_data,
            'free_balance': max(0, client_data['avg_monthly_balance'] - 50000),  # Estimate free balance
            'fx_activity_score': min(10, int(type_spending.get('fx_buy', 0) / 500000)),  # 1-10 scale
            'foreign_spending': category_spending.get('Путешествия', 0) + category_spending.get('Отели', 0),
            'deposit_fx_topup_count': int(type_spending.get('deposit_fx_topup_out', 0) / 200000),  # Estimate
            'deposit_fx_withdraw_count': int(type_spending.get('deposit_fx_withdraw_in', 0) / 200000)  # Estimate
        }
    
    elif normalized_product_type == "Депозит сберегательный":
        return {
            **base_data,
            'stable_balance': client_data['avg_monthly_balance'],
            'spending_volatility': 3 if client_data['avg_monthly_balance'] > 500000 else 7,  # 1-10 scale
            'deposit_topup_count': int(type_spending.get('deposit_topup_out', 0) / 200000),  # Estimate
            'deposit_withdraw_count': 0,  # No withdrawals for savings deposit
            'balance_stability_score': 9 if client_data['avg_monthly_balance'] > 500000 else 5  # 1-10 scale
        }
    
    elif normalized_product_type == "Депозит накопительный":
        return {
            **base_data,
            'regular_balance': client_data['avg_monthly_balance'],
            'periodic_topups': type_spending.get('deposit_topup_out', 0) > 0,
            'topup_frequency': int(type_spending.get('deposit_topup_out', 0) / 100000),  # Estimate frequency
            'savings_behavior_score': 8 if type_spending.get('deposit_topup_out', 0) > 500000 else 4,  # 1-10 scale
            'small_regular_amounts': type_spending.get('deposit_topup_out', 0) < 500000
        }
    
    elif normalized_product_type == "Инвестиции":
        return {
            **base_data,
            'available_funds': max(0, client_data['avg_monthly_balance'] - 100000),  # Estimate available funds
            'invest_in_count': int(type_spending.get('invest_in', 0) / 200000),  # Estimate count
            'invest_out_count': int(type_spending.get('invest_out', 0) / 200000),  # Estimate count
            'investment_interest_score': 8 if type_spending.get('invest_in', 0) > 0 else 3,  # 1-10 scale
            'risk_tolerance': 7 if client_data['age'] < 35 else 5  # 1-10 scale
        }
    
    elif normalized_product_type == "Золотые слитки":
        return {
            **base_data,
            'high_liquidity': client_data['avg_monthly_balance'] > 1000000,
            'gold_buy_count': int(type_spending.get('gold_buy_out', 0) / 500000),  # Estimate count
            'gold_sell_count': int(type_spending.get('gold_sell_in', 0) / 500000),  # Estimate count
            'jewelry_spent': category_spending.get('Ювелирные украшения', 0),
            'value_preservation_interest': 8 if type_spending.get('gold_buy_out', 0) > 0 else 5  # 1-10 scale
        }
    
    else:
        # Default fallback
        return base_data

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
        
        # Add humanization instructions to the prompt
        humanization_instructions = """

ВАЖНО: Создай уведомление, которое:
- Звучит как личное сообщение от банка, а не автоматическая рассылка
- Используй конкретные детали из трат клиента
- Добавляй личные наблюдения ("заметили", "видим", "видно")
- Включай эмоциональные слова ("удобно", "выгодно", "приятно")
- Создавай ощущение индивидуального подхода
- Избегай шаблонных фраз, будь естественным
- Показывай понимание потребностей клиента

Примеры человечных фраз:
- "заметили, что вы очень активно..."
- "видим, что вы часто тратите на..."
- "видно по вашим тратам, что..."
- "обратили внимание, что у вас..."
- "это видно по вашим тратам..."

Сделай уведомление живым и персональным!
"""
        
        # Combine the formatted prompt with humanization instructions
        full_prompt = formatted_prompt + humanization_instructions
        
        # Initialize Azure OpenAI LLM
        llm = get_azure_llm()
        
        # Generate the notification
        response = llm.invoke(full_prompt)
        
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


def process_single_client(client_data: dict, use_azure: bool = True) -> dict:
    """
    Process a single client and generate notification.
    
    Args:
        client_data: Client data from JSON
        use_azure: Whether to use Azure OpenAI or template-based approach
        
    Returns:
        Dictionary with client_code, product, and push_notification
    """
    product_type = client_data['product_type']
    normalized_product_type = normalize_product_name(product_type)
    
    try:
        if use_azure:
            # Extract product-specific data and generate with Azure OpenAI
            product_data = extract_product_specific_data(client_data, product_type)
            notification_result = generate_notification(normalized_product_type, **product_data)
            return notification_result
        else:
            # Generate template-based notification
            name = client_data['name']
            age = client_data['age']
            status = client_data['status']
            category_spending = client_data['top_5_category_spending']
            type_spending = client_data['top_5_type_spending']
            currencies = client_data.get('currencies', ['KZT'])
            
            notification_text = generate_template_notification(
                normalized_product_type, name, age, status, category_spending, type_spending, currencies
            )
            
            return {
                "client_code": client_data['client_code'],
                "product": product_type,
                "push_notification": notification_text
            }
            
    except Exception as e:
        print(f"  ✗ Error processing client {client_data['client_code']}: {e}")
        return {
            "client_code": client_data['client_code'],
            "product": product_type,
            "push_notification": f"Ошибка генерации уведомления для {product_type}"
        }

def save_results_to_csv(results: list, output_csv_path: str) -> None:
    """Save results to CSV file"""
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['client_code', 'product', 'push_notification']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow(result)

def generate_all_notifications(json_file_path: str, output_csv_path: str, use_azure: bool = True) -> None:
    """
    Generate notifications for all clients and save to CSV file.
    
    Args:
        json_file_path: Path to product_classification.json
        output_csv_path: Path for output CSV file
        use_azure: Whether to use Azure OpenAI or template-based approach
    """
    print("Loading client data...")
    clients_data = load_client_data(json_file_path)
    
    method = "Azure OpenAI" if use_azure else "template-based"
    print(f"Processing {len(clients_data)} clients using {method} approach...")
    
    results = []
    
    for i, client_data in enumerate(clients_data, 1):
        print(f"Processing client {i}/{len(clients_data)}: {client_data['name']} (ID: {client_data['client_code']})")
        
        result = process_single_client(client_data, use_azure)
        results.append(result)
        
        print(f"  ✓ Generated notification for {client_data['product_type']}")
    
    # Save to CSV
    print(f"\nSaving results to {output_csv_path}...")
    save_results_to_csv(results, output_csv_path)
    
    print(f"✓ Successfully generated {len(results)} notifications")
    print(f"✓ Results saved to {output_csv_path}")

def generate_template_notification(product_type: str, name: str, age: int, status: str, 
                                 category_spending: dict, type_spending: dict, currencies: list = None) -> str:
    """Generate a template-based notification without Azure OpenAI"""
    
    # Get current month
    current_month = datetime.now().strftime('%B').lower()
    month_names = {
        'january': 'январе', 'february': 'феврале', 'march': 'марте',
        'april': 'апреле', 'may': 'мае', 'june': 'июне',
        'july': 'июле', 'august': 'августе', 'september': 'сентябре',
        'october': 'октябре', 'november': 'ноябре', 'december': 'декабре'
    }
    month = month_names.get(current_month, 'августе')
    
    # Import CTA variants function
    from core_prompts import get_cta_variants
    import random
    
    # Get random CTA for variety
    cta_options = get_cta_variants(product_type)
    cta = random.choice(cta_options)
    
    # Get currency symbol
    from core_prompts import get_currency_symbol
    if currencies and len(currencies) > 0:
        currency_symbol = get_currency_symbol(currencies[0])
    else:
        currency_symbol = "₸"
    
    # Humanized observation phrases
    observation_phrases = [
        "заметили, что",
        "видим, что", 
        "видно, что",
        "обратили внимание, что",
        "видно по вашим тратам, что"
    ]
    
    # Get random observation phrase
    observation = random.choice(observation_phrases)
    
    if product_type == "Карта для путешествий":
        taxi_spent = category_spending.get('Такси', 0)
        travel_spent = category_spending.get('Путешествия', 0)
        hotels_spent = category_spending.get('Отели', 0)
        
        if taxi_spent > 100000 or travel_spent > 100000:
            cashback = int((taxi_spent + travel_spent + hotels_spent) * 0.04)
            return f"{name}, {observation} в {month} вы очень активно пользовались такси — {taxi_spent:,} {currency_symbol}. С картой для путешествий вернули бы около {cashback:,} {currency_symbol} кешбэка. {cta}."
        else:
            return f"{name}, {observation} вы часто путешествуете и пользуетесь такси. С картой для путешествий получили бы кешбэк с каждой поездки. {cta}."
    
    elif product_type == "Премиальная карта":
        balance = type_spending.get('salary_in', 0)
        restaurants = category_spending.get('Кафе и рестораны', 0)
        cosmetics = category_spending.get('Косметика и Парфюмерия', 0)
        jewelry = category_spending.get('Ювелирные украшения', 0)
        
        if balance > 1000000:
            if cosmetics > 100000 or jewelry > 100000:
                return f"{name}, {observation} у вас высокий остаток и активные траты на косметику и ювелирку. Премиальная карта даст до 5% кешбэка в этих категориях. {cta}."
            else:
                return f"{name}, {observation} у вас стабильно высокий остаток. Премиальная карта даст до 4% кешбэка на все покупки и бесплатные снятия. {cta}."
        else:
            return f"{name}, {observation} вы часто тратите в ресторанах. С премиальной картой получили бы повышенный кешбэк и бесплатные снятия. {cta}."
    
    elif product_type == "Кредитная карта":
        # Get top 3 categories
        sorted_categories = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)
        top_categories = [cat[0] for cat in sorted_categories[:3]]
        
        cat1 = top_categories[0] if len(top_categories) > 0 else 'Продукты питания'
        cat2 = top_categories[1] if len(top_categories) > 1 else 'Кафе и рестораны'
        cat3 = top_categories[2] if len(top_categories) > 2 else 'Такси'
        
        return f"{name}, {observation} вы часто тратите на {cat1.lower()}, {cat2.lower()} и {cat3.lower()}. Кредитная карта даст до 10% кешбэка именно в ваших любимых категориях. {cta}."
    
    elif product_type == "Обмен валют":
        fx_activity = type_spending.get('fx_buy', 0)
        foreign_currencies = [curr for curr in currencies if curr != 'KZT'] if currencies else []
        
        if foreign_currencies:
            # Client has foreign currencies, use the first one
            foreign_currency = foreign_currencies[0]
            return f"{name}, {observation} вы часто работаете с валютой. В приложении выгодный обмен и авто-покупка по целевому курсу. {cta}."
        elif fx_activity > 1000000:
            return f"{name}, {observation} у вас активность с валютными операциями. В приложении выгодный обмен и авто-покупка по целевому курсу. {cta}."
        else:
            return f"{name}, {observation} вы можете работать с валютой. В приложении выгодный обмен валют и авто-покупка по целевому курсу. {cta}."
    
    elif product_type == "Кредит наличными":
        return f"{name}, {observation} у вас могут быть крупные траты. Если нужен запас — можно оформить кредит наличными с гибкими выплатами. {cta}."
    
    elif product_type == "Депозит мультивалютный":
        return f"{name}, {observation} у вас остаются свободные средства. Мультивалютный депозит даст проценты и удобство хранения в разных валютах. {cta}."
    
    elif product_type == "Депозит сберегательный":
        return f"{name}, {observation} у вас стабильный остаток. Сберегательный депозит даст максимальную ставку за счёт отсутствия снятий. {cta}."
    
    elif product_type == "Депозит накопительный":
        return f"{name}, {observation} вы регулярно откладываете средства. Накопительный депозит поможет эффективно копить с повышенной ставкой. {cta}."
    
    elif product_type == "Инвестиции":
        return f"{name}, {observation} у вас есть свободные средства. Инвестиции дадут возможность роста с низким порогом входа. {cta}."
    
    elif product_type == "Золотые слитки":
        return f"{name}, {observation} у вас высокая ликвидность средств. Золотые слитки — надёжный защитный актив для диверсификации. {cta}."
    
    else:
        return f"{name}, {observation} у нас есть специальное предложение для вас. {cta}."

if __name__ == "__main__":
    # Configuration
    JSON_FILE_PATH = "processed/product_classification.json"
    OUTPUT_CSV_PATH = "banking_notifications.csv"
    
    print("=== Banking Notification Generator ===")
    print("This script generates personalized push notifications for banking products")
    print("based on client spending patterns from product_classification.json")
    print()
    
    # Check if Azure OpenAI is available
    try:
        # Try to initialize Azure OpenAI
        llm = get_azure_llm()
        print("✓ Azure OpenAI connection available")
        print("Using Azure OpenAI for notification generation...")
        print()
        
        # Generate notifications with Azure OpenAI
        generate_all_notifications(JSON_FILE_PATH, OUTPUT_CSV_PATH, use_azure=True)
        
    except Exception as e:
        print(f"⚠ Azure OpenAI not available: {e}")
        print("Falling back to template-based generation...")
        print()
        
        # Generate notifications with template-based approach
        generate_all_notifications(JSON_FILE_PATH, OUTPUT_CSV_PATH, use_azure=False)
    
    print("\n=== Generation Complete ===")
    print(f"Results saved to: {OUTPUT_CSV_PATH}")
    print("You can now use this CSV file for your banking notification campaign!")
