# Banking Notification Generator

A streamlined system for generating personalized banking push notifications using Azure OpenAI.

## 🎯 Overview

This system analyzes client behavior data and generates personalized push notifications for 10 different banking products, following Russian TOV (Tone of Voice) guidelines.

## 🚀 Quick Start

1. **Setup Environment**

   ```bash
   pip install python-dotenv langchain-openai
   ```

2. **Configure Azure OpenAI**
   Create `.env` file with your Azure OpenAI credentials:

   ```env
   AZURE_OPENAI_API_KEY=your_api_key
   AZURE_OPENAI_ENDPOINT=your_endpoint
   AZURE_OPENAI_API_VERSION=your_version
   ```

3. **Generate Notifications**

   ```python
   from banking_notification_prompts import generate_notification

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
       "month": "августе"
   }

   result = generate_notification("Карта для путешествий", **client_data)
   print(result['push_notification'])
   ```

## 📋 Supported Products

1. **Карта для путешествий** (Travel Card)
2. **Премиальная карта** (Premium Card)
3. **Кредитная карта** (Credit Card)
4. **Обмен валют** (Currency Exchange)
5. **Кредит наличными** (Cash Loan)
6. **Депозит мультивалютный** (Multi-currency Deposit)
7. **Депозит сберегательный** (Savings Deposit)
8. **Депозит накопительный** (Accumulative Deposit)
9. **Инвестиции** (Investments)
10. **Золотые слитки** (Gold Bars)

## 🏗️ Architecture

### Core Components

- **`banking_notification_prompts.py`** - Main module with prompts and Azure OpenAI integration
- **`data/`** - Sample data files for testing
- **`.env`** - Environment configuration

### Key Features

- ✅ **Pre-calculated instructions** - Age and status-based tone optimization
- ✅ **Azure OpenAI integration** - Real-time notification generation
- ✅ **TOV compliance** - Russian banking tone guidelines
- ✅ **Product-specific prompts** - Tailored for each banking product
- ✅ **JSON output** - Structured response format

## 🧪 Testing

Run the test suite:

```bash
python -m pytest test_banking_notifications.py
```

Or run the simple test:

```bash
python banking_notification_prompts.py
```

## 📊 Data Requirements

### Client Profile

- `client_code` - Unique client identifier
- `name` - Client name
- `status` - Client status (Студент, Зарплатный клиент, Премиальный клиент, Стандартный клиент)
- `age` - Client age
- `city` - Client city
- `avg_monthly_balance_KZT` - Average monthly balance in KZT

### Product-Specific Data

Each product requires specific behavioral data (see individual prompts for details).

## 🎨 TOV Guidelines

- **Age-based tone**: Younger clients get more casual tone, adults get professional tone
- **Status-based tone**: Students get informal, premium clients get respectful tone
- **Format**: 80-120 characters, no CAPS, max one exclamation mark
- **Numbers**: Comma for decimals, spaces for thousands (2 490 ₸)
- **CTA**: Clear call-to-action phrases

## 📈 Performance

- **Optimized prompts** reduce AI processing time
- **Pre-calculated instructions** eliminate redundant AI work
- **Structured output** ensures consistent JSON format
- **Error handling** provides graceful fallbacks

## 🔧 Development

### Adding New Products

1. Add product prompt to `BANKING_PROMPTS` dictionary
2. Define required data fields in prompt template
3. Add test cases in test file

### Customizing TOV

Modify `get_age_instructions()` and `get_status_instructions()` functions in the main module.

## 📝 License

This project is part of the Decentrathon 4 BCC competition.
