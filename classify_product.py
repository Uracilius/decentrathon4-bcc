import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import os
import logging
from dataclasses import dataclass
import json
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

# Initialize logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ============================================
# Data Analysis Tools
# ============================================

class ClientAnalyzer:
    """Tools for analyzing client financial behavior"""
    
    def __init__(self, clients_df: pd.DataFrame, transactions_df: pd.DataFrame, transfers_df: pd.DataFrame):
        """
        Initialize analyzer with dataframes
        
        Args:
            clients_df: DataFrame with columns ['client_code', 'name', 'age', 'status', 'avg_monthly_balance_KZT', 'city']
            transactions_df: DataFrame with columns ['client_code', 'date', 'category', 'currency', 'amount']
            transfers_df: DataFrame with columns ['client_code', 'date', 'type', 'currency', 'amount']
        """
        self.clients_df = clients_df
        self.transactions_df = transactions_df
        self.transfers_df = transfers_df
        
        # Convert date columns to datetime
        self.transactions_df['date'] = pd.to_datetime(self.transactions_df['date'])
        self.transfers_df['date'] = pd.to_datetime(self.transfers_df['date'])
    
    def get_category_spending(self, client_code: str) -> Dict[str, float]:
        """
        Tool 1: Get spending by category for a specific client
        
        Args:
            client_code: Unique client identifier
            
        Returns:
            Dictionary with category as key and total amount spent as value
        """
        client_transactions = self.transactions_df[self.transactions_df['client_code'] == client_code]
        
        if client_transactions.empty:
            return {}
        
        category_spending = client_transactions.groupby('category')['amount'].sum().to_dict()
        return category_spending
    
    def get_type_spending(self, client_code: str) -> Dict[str, float]:
        """
        Tool 2: Get spending by transfer type for a specific client
        
        Args:
            client_code: Unique client identifier
            
        Returns:
            Dictionary with type as key and total amount as value
        """
        client_transfers = self.transfers_df[self.transfers_df['client_code'] == client_code]
        
        if client_transfers.empty:
            return {}
        
        type_spending = client_transfers.groupby('type')['amount'].sum().to_dict()
        return type_spending
    
    def get_currencies_used(self, client_code: str) -> List[str]:
        """
        Tool 3: Get all currencies used by a specific client
        
        Args:
            client_code: Unique client identifier
            
        Returns:
            List of unique currencies used
        """
        transactions_currencies = self.transactions_df[
            self.transactions_df['client_code'] == client_code
        ]['currency'].unique().tolist()
        
        transfers_currencies = self.transfers_df[
            self.transfers_df['client_code'] == client_code
        ]['currency'].unique().tolist()
        
        all_currencies = list(set(transactions_currencies + transfers_currencies))
        return all_currencies
    
    def get_avg_monthly_balance(self, client_code: str) -> Optional[float]:
        """
        Tool 4: Get average monthly balance in KZT for a specific client
        
        Args:
            client_code: Unique client identifier
            
        Returns:
            Average monthly balance in KZT or None if client not found
        """
        client_data = self.clients_df[self.clients_df['client_code'] == client_code]
        
        if client_data.empty:
            return None
        
        return client_data['avg_monthly_balance_KZT'].iloc[0]
    
    def get_comprehensive_client_profile(self, client_code: str) -> Dict:
        """
        Get comprehensive client profile including all analysis
        
        Args:
            client_code: Unique client identifier
            
        Returns:
            Dictionary with complete client profile
        """
        logger.debug("Building comprehensive profile for client_code=%s", client_code)
        client_info = self.clients_df[self.clients_df['client_code'] == client_code].to_dict('records')
        
        if not client_info:
            logger.warning("Client not found: client_code=%s", client_code)
            return {"error": "Client not found"}
        
        profile = {
            "client_info": client_info[0],
            "category_spending": self.get_category_spending(client_code),
            "type_spending": self.get_type_spending(client_code),
            "currencies_used": self.get_currencies_used(client_code),
            "avg_monthly_balance_KZT": self.get_avg_monthly_balance(client_code),
            "transaction_frequency": self._calculate_transaction_frequency(client_code),
            "spending_patterns": self._analyze_spending_patterns(client_code)
        }
        
        logger.debug(
            "Profile built for client_code=%s: categories=%d, types=%d, currencies=%d",
            client_code,
            len(profile.get('category_spending', {})) if profile.get('category_spending') else 0,
            len(profile.get('type_spending', {})) if profile.get('type_spending') else 0,
            len(profile.get('currencies_used', [])) if profile.get('currencies_used') else 0,
        )
        return profile
    
    def _calculate_transaction_frequency(self, client_code: str) -> Dict:
        """Calculate transaction frequency metrics"""
        client_transactions = self.transactions_df[self.transactions_df['client_code'] == client_code]
        client_transfers = self.transfers_df[self.transfers_df['client_code'] == client_code]
        
        if client_transactions.empty and client_transfers.empty:
            return {"monthly_avg_transactions": 0, "monthly_avg_transfers": 0}
        
        # Calculate date ranges
        trans_dates = client_transactions['date'] if not client_transactions.empty else pd.Series()
        transfer_dates = client_transfers['date'] if not client_transfers.empty else pd.Series()
        
        all_dates = pd.concat([trans_dates, transfer_dates])
        if all_dates.empty:
            return {"monthly_avg_transactions": 0, "monthly_avg_transfers": 0}
        
        date_range_months = (all_dates.max() - all_dates.min()).days / 30.0
        date_range_months = max(date_range_months, 1)  # At least 1 month
        
        return {
            "monthly_avg_transactions": len(client_transactions) / date_range_months,
            "monthly_avg_transfers": len(client_transfers) / date_range_months,
            "total_operations": len(client_transactions) + len(client_transfers)
        }
    
    def _analyze_spending_patterns(self, client_code: str) -> Dict:
        """Analyze spending patterns for better product recommendations"""
        client_transactions = self.transactions_df[self.transactions_df['client_code'] == client_code]
        
        if client_transactions.empty:
            return {}
        
        patterns = {
            "total_spending": client_transactions['amount'].sum(),
            "avg_transaction_amount": client_transactions['amount'].mean(),
            "max_transaction": client_transactions['amount'].max(),
            "min_transaction": client_transactions['amount'].min(),
            "most_frequent_category": client_transactions['category'].mode().iloc[0] if not client_transactions['category'].mode().empty else None,
            "category_diversity": len(client_transactions['category'].unique())
        }
        
        return patterns

# ============================================
# Product Recommendation Engine
# ============================================

@dataclass
class Product:
    """Product definition"""
    name: str
    description: str
    key_features: List[str]
    target_audience: List[str]

class ProductRecommendationEngine:
    """OpenAI-based product recommendation system"""
    
    def __init__(self, api_key: str):
        """
        Initialize recommendation engine
        
        Args:
            api_key: OpenAI API key
        """
        # Prefer Azure OpenAI credentials from environment. Fall back to provided api_key if set.
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY") or api_key
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        self.azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT") or "gpt-4o-mini"
        
        # Initialize AzureChatOpenAI client if configuration is available
        self.llm = None
        try:
            if all([self.api_key, self.azure_endpoint, self.azure_api_version, self.azure_deployment]):
                self.llm = AzureChatOpenAI(
                    api_key=self.api_key,
                    azure_endpoint=self.azure_endpoint,
                    api_version=self.azure_api_version,
                    azure_deployment=self.azure_deployment,
                    temperature=0.3
                )
                logger.info(
                    "Azure OpenAI client initialized (deployment=%s, endpoint_configured=%s)",
                    self.azure_deployment,
                    bool(self.azure_endpoint)
                )
            else:
                logger.warning("Azure OpenAI client is not fully configured. Falling back to rule-based when needed.")
        except Exception as e:
            logger.error("Error initializing Azure OpenAI client: %s", e)
        self.products = self._initialize_products()
    
    def _initialize_products(self) -> Dict[str, Product]:
        """Initialize product definitions"""
        return {
            'Карта для путешествий': Product(
                name='Карта для путешествий',
                description='4% кешбэк на категорию «Путешествия», 4% кешбэк на такси, поезда, самолеты. Привилегии Visa Signature.',
                key_features=['travel_cashback', 'transport_cashback', 'visa_signature'],
                target_audience=['frequent_traveler', 'hotel_booker', 'high_transport_spending']
            ),
            'Премиальная карта': Product(
                name='Премиальная карта',
                description='2-4% кешбэк в зависимости от депозита. Повышенный кэшбэк на ювелирные изделия, парфюмерию и рестораны.',
                key_features=['high_balance_benefits', 'luxury_cashback', 'free_transfers'],
                target_audience=['high_balance', 'luxury_spending', 'frequent_transfers']
            ),
            'Кредитная карта': Product(
                name='Кредитная карта',
                description='Кредитный лимит до 2 млн ₸, до 10% кешбэк в выбранных категориях, рассрочка 3-24 мес.',
                key_features=['credit_line', 'category_cashback', 'installments'],
                target_audience=['credit_user', 'category_optimizer', 'installment_buyer']
            ),
            'Обмен валют': Product(
                name='Обмен валют',
                description='Выгодный курс в приложении без комиссии 24/7, автоматическая покупка при целевом курсе.',
                key_features=['multi_currency', 'no_commission', 'auto_exchange'],
                target_audience=['multi_currency_user', 'forex_trader', 'international_business']
            ),
            'Кредит наличными': Product(
                name='Кредит наличными',
                description='Без залога и справок, онлайн оформление, ставка 12-21%, досрочное погашение без штрафов.',
                key_features=['no_collateral', 'quick_approval', 'flexible_repayment'],
                target_audience=['quick_cash_need', 'no_collateral_available', 'online_preferring']
            ),
            'Депозит Мультивалютный': Product(
                name='Депозит Мультивалютный',
                description='Ставка 14,50%, поддержка KZT/USD/RUB/EUR, свободное пополнение и снятие.',
                key_features=['multi_currency_deposit', 'flexible_access', 'currency_rebalancing'],
                target_audience=['multi_currency_saver', 'flexible_access_need', 'currency_diversifier']
            ),
            'Депозит Сберегательный': Product(
                name='Депозит Сберегательный',
                description='Ставка 16,50%, защита KDIF, без пополнения и снятия до конца срока.',
                key_features=['highest_rate', 'deposit_protection', 'fixed_term'],
                target_audience=['long_term_saver', 'maximum_yield_seeker', 'capital_preserver']
            ),
            'Депозит Накопительный': Product(
                name='Депозит Накопительный',
                description='Ставка 15,50%, возможность пополнения, без снятия.',
                key_features=['accumulation', 'regular_deposits', 'good_rate'],
                target_audience=['regular_saver', 'goal_oriented_saver', 'discipline_builder']
            ),
            'Инвестиции': Product(
                name='Инвестиции',
                description='0% комиссии на сделки, порог входа от 6 ₸, без комиссий в первый год.',
                key_features=['zero_commission', 'low_entry', 'beginner_friendly'],
                target_audience=['investor', 'small_investor', 'investment_beginner']
            ),
            'Золотые слитки': Product(
                name='Золотые слитки',
                description='Слитки 999,9 пробы, покупка/продажа в отделениях, хранение в сейфовых ячейках.',
                key_features=['physical_gold', 'value_preservation', 'bank_storage'],
                target_audience=['gold_investor', 'diversification_seeker', 'long_term_preserver']
            )
        }
    
    def classify_client(self, client_profile: Dict) -> Dict[str, float]:
        """
        Classify client and recommend products using OpenAI
        
        Args:
            client_profile: Comprehensive client profile from ClientAnalyzer
            
        Returns:
            Dictionary with product names as keys and recommendation scores (0-1) as values
        """
        # Prepare context for OpenAI
        context = self._prepare_context(client_profile)
        
        # Create prompt
        prompt = self._create_classification_prompt(context)
        
        try:
            if not self.llm:
                raise RuntimeError("Azure OpenAI client is not configured. Check environment variables.")
            logger.debug("Invoking LLM with context length=%d", len(prompt))
            # Call Azure OpenAI via LangChain
            response = self.llm.invoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt)
            ])
            # Parse response
            recommendations = self._parse_recommendations(response.content)
            logger.info("Received %d recommendations from LLM", len(recommendations))
            return recommendations
        except Exception as e:
            logger.warning("LLM classification failed (%s). Using rule-based fallback.", e)
            # Fallback to rule-based classification
            return self._rule_based_classification(client_profile)
    
    def _prepare_context(self, client_profile: Dict) -> str:
        """Prepare context string from client profile"""
        context_parts = []
        
        # Basic info
        if 'client_info' in client_profile:
            info = client_profile['client_info']
            context_parts.append(f"Age: {info.get('age', 'unknown')}")
            context_parts.append(f"Status: {info.get('status', 'unknown')}")
            context_parts.append(f"City: {info.get('city', 'unknown')}")
        
        # Financial metrics
        balance = client_profile.get('avg_monthly_balance_KZT', 0)
        context_parts.append(f"Average monthly balance: {balance:,.0f} KZT")
        
        # Spending categories
        if client_profile.get('category_spending'):
            top_categories = sorted(
                client_profile['category_spending'].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3]
            context_parts.append(f"Top spending categories: {', '.join([f'{cat[0]} ({cat[1]:,.0f})' for cat in top_categories])}")
        
        # Transfer types
        if client_profile.get('type_spending'):
            top_types = sorted(
                client_profile['type_spending'].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3]
            context_parts.append(f"Top transfer types: {', '.join([f'{t[0]} ({t[1]:,.0f})' for t in top_types])}")
        
        # Currencies
        currencies = client_profile.get('currencies_used', [])
        if currencies:
            context_parts.append(f"Currencies used: {', '.join(currencies)}")
        
        # Transaction patterns
        if 'spending_patterns' in client_profile:
            patterns = client_profile['spending_patterns']
            context_parts.append(f"Total spending: {patterns.get('total_spending', 0):,.0f}")
            context_parts.append(f"Average transaction: {patterns.get('avg_transaction_amount', 0):,.0f}")
            context_parts.append(f"Category diversity: {patterns.get('category_diversity', 0)}")
        
        # Frequency
        if 'transaction_frequency' in client_profile:
            freq = client_profile['transaction_frequency']
            context_parts.append(f"Monthly transactions: {freq.get('monthly_avg_transactions', 0):.1f}")
            context_parts.append(f"Monthly transfers: {freq.get('monthly_avg_transfers', 0):.1f}")
        
        return "\n".join(context_parts)
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for OpenAI"""
        return """You are a banking product recommendation expert. Based on client financial behavior, 
        recommend suitable banking products. Return recommendations as JSON with product names as keys 
        and confidence scores (0-1) as values. Consider client's spending patterns, balance, currencies used, 
        and transaction behavior. Be precise and base recommendations on actual client data."""
    
    def _create_classification_prompt(self, context: str) -> str:
        """Create classification prompt"""
        products_desc = "\n\n".join([
            f"{name}: {prod.description}" 
            for name, prod in self.products.items()
        ])
        
        prompt = f"""Based on the following client profile, recommend suitable banking products.

Client Profile:
{context}

Available Products:
{products_desc}

Return a JSON object with product names as keys and recommendation confidence scores (0-1) as values.
Consider only products that match the client's actual behavior and needs.
Example format: {{"Карта для путешествий": 0.85, "Депозит Накопительный": 0.65}}

Recommendations:"""
        
        return prompt
    
    def _parse_recommendations(self, response_text: str) -> Dict[str, float]:
        """Parse OpenAI response to extract recommendations"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                recommendations = json.loads(json_match.group())
                # Normalize scores to 0-1 range
                for product in recommendations:
                    if product in self.products:
                        recommendations[product] = max(0, min(1, float(recommendations[product])))
                return recommendations
        except:
            pass
        
        # Fallback to empty recommendations
        return {}
    
    def _rule_based_classification(self, client_profile: Dict) -> Dict[str, float]:
        """Fallback rule-based classification"""
        recommendations = {}
        
        # Extract key metrics
        balance = client_profile.get('avg_monthly_balance_KZT', 0)
        currencies = client_profile.get('currencies_used', [])
        categories = client_profile.get('category_spending', {})
        patterns = client_profile.get('spending_patterns', {})
        
        # High balance products
        if balance > 6000000:
            recommendations['Премиальная карта'] = 0.9
            recommendations['Депозит Сберегательный'] = 0.8
        elif balance > 1000000:
            recommendations['Премиальная карта'] = 0.7
            recommendations['Депозит Накопительный'] = 0.75
        
        # Multi-currency users
        if len(currencies) > 2:
            recommendations['Обмен валют'] = 0.85
            recommendations['Депозит Мультивалютный'] = 0.8
        
        # Travel spending
        if 'travel' in str(categories).lower() or 'transport' in str(categories).lower():
            recommendations['Карта для путешествий'] = 0.85
        
        # High transaction diversity
        if patterns.get('category_diversity', 0) > 5:
            recommendations['Кредитная карта'] = 0.7
        
        # Low balance but active
        if balance < 500000 and patterns.get('total_spending', 0) > balance * 2:
            recommendations['Кредит наличными'] = 0.6
            recommendations['Кредитная карта'] = 0.75
        
        # Investment potential
        if balance > 2000000:
            recommendations['Инвестиции'] = 0.7
            recommendations['Золотые слитки'] = 0.6
        
        return recommendations

# ============================================
# API Endpoint Implementation
# ============================================

class BankingRecommendationAPI:
    """Complete API implementation for banking recommendations"""
    
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        self.analyzer = None
        logger.info("Initializing ProductRecommendationEngine")
        self.recommender = ProductRecommendationEngine(openai_api_key)
    
    def load_data(self, clients_path: str, transactions_path: str, transfers_path: str):
        """Load CSV data files"""
        logger.info("Loading data: clients=%s, transactions=%s, transfers=%s", clients_path, transactions_path, transfers_path)
        clients_df = pd.read_csv(clients_path)
        transactions_df = pd.read_csv(transactions_path)
        transfers_df = pd.read_csv(transfers_path)
        
        logger.info(
            "Data loaded: clients=%d, transactions=%d, transfers=%d",
            len(clients_df), len(transactions_df), len(transfers_df)
        )
        self.analyzer = ClientAnalyzer(clients_df, transactions_df, transfers_df)
    
    def get_recommendations(self, client_code: str, threshold: float = 0.5) -> Dict:
        """
        Get product recommendations for a client
        
        Args:
            client_code: Client identifier
            threshold: Minimum confidence score to include recommendation
            
        Returns:
            Dictionary with recommendations and client profile
        """
        if not self.analyzer:
            logger.error("Analyzer not initialized. Call load_data first.")
            return {"error": "Data not loaded. Please load CSV files first."}
        
        # Get comprehensive client profile
        logger.info("Generating profile and recommendations for client_code=%s", client_code)
        profile = self.analyzer.get_comprehensive_client_profile(client_code)
        
        if "error" in profile:
            logger.warning("Cannot generate recommendations: %s", profile["error"])
            return profile
        
        # Get recommendations
        recommendations = self.recommender.classify_client(profile)
        logger.debug("Raw recommendations: %s", recommendations)
        
        # Filter by threshold
        filtered_recommendations = {
            product: score 
            for product, score in recommendations.items() 
            if score >= threshold
        }
        logger.info(
            "Filtered recommendations count=%d (threshold=%.2f)",
            len(filtered_recommendations), threshold
        )
        
        # Sort by score
        sorted_recommendations = dict(
            sorted(filtered_recommendations.items(), key=lambda x: x[1], reverse=True)
        )
        logger.debug("Sorted recommendations: %s", sorted_recommendations)
        
        # Derive structured output
        product_type = next(iter(sorted_recommendations)) if sorted_recommendations else (
            max(recommendations, key=recommendations.get) if recommendations else ""
        )
        
        cat_spending = profile.get('category_spending', {}) or {}
        top5_cat_items = sorted(cat_spending.items(), key=lambda x: x[1], reverse=True)[:5]
        top_5_category_spending = {k: int(round(v)) for k, v in top5_cat_items}
        
        type_spending = profile.get('type_spending', {}) or {}
        top5_type_items = sorted(type_spending.items(), key=lambda x: x[1], reverse=True)[:5]
        top_5_type_spending = {k: int(round(v)) for k, v in top5_type_items}
        
        avg_balance_val = profile.get('avg_monthly_balance_KZT')
        avg_monthly_balance = int(round(avg_balance_val)) if avg_balance_val is not None else 0
        
        return {
            "product_type": product_type,
            "top_5_category_spending": top_5_category_spending,
            "top_5_type_spending": top_5_type_spending,
            "avg_monthly_balance": avg_monthly_balance
        }
    
    def _get_top_category(self, profile: Dict) -> Optional[str]:
        """Get top spending category"""
        categories = profile.get('category_spending', {})
        if not categories:
            return None
        return max(categories.items(), key=lambda x: x[1])[0]

# ============================================
# Usage Example
# ============================================

def main():
    """Example usage of the banking recommendation system"""
    
    # Initialize API with OpenAI key
    api = BankingRecommendationAPI(openai_api_key="your-openai-api-key-here")
    
    # Load data
    api.load_data(
        clients_path="processed/clients.csv",
        transactions_path="processed/all_transactions.csv",
        transfers_path="processed/all_transfers.csv"
    )
    
    # Batch classify clients 1..60 and save to JSON array
    results = []
    for client_code in range(1, 61):
        res = api.get_recommendations(client_code, threshold=0.4)
        if isinstance(res, dict) and res.get("error"):
            logger.warning("Skipping client_code=%s due to error: %s", client_code, res.get("error"))
            continue
        results.append({"client_code": client_code, **res})
    
    output_path = os.path.join(os.path.dirname(__file__), 'processed', "product_classification.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(results)} records to {output_path}")

if __name__ == "__main__":
    main()