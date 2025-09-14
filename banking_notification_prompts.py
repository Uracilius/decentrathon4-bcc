"""
Banking Notification Generator - Main Entry Point
================================================

This is the main entry point that combines core prompts with Azure OpenAI integration.
Run this file to see all functionality in action.

Usage:
    python banking_notification_prompts.py
"""

# Import everything from both modules
from core_prompts import *
from azure_notification_generator import generate_notification, run_all_demos

# Re-export the main function for easy access
__all__ = ['generate_notification', 'get_prompt_for_product', 'format_prompt_with_data', 'get_available_products', 'BANKING_PROMPTS']

if __name__ == "__main__":
    print("🏦 BANKING NOTIFICATION GENERATOR")
    print("=" * 50)
    print("This is the main entry point for the banking notification system.")
    print("It combines core prompts with Azure OpenAI integration.")
    print("\n" + "=" * 50)
    
    # Run all demos and examples
    run_all_demos()
    
    print("\n" + "=" * 50)
    print("📋 AVAILABLE FUNCTIONS:")
    print("• generate_notification(product_name, **client_data) - Generate notification")
    print("• get_prompt_for_product(product_name) - Get prompt template")
    print("• format_prompt_with_data(prompt, **data) - Format prompt with data")
    print("• get_available_products() - List all products")
    print("\n📚 MODULES:")
    print("• core_prompts.py - Core prompt definitions")
    print("• azure_notification_generator.py - Azure OpenAI integration")
    print("\n✅ Ready to use!")
