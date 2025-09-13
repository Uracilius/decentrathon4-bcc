import os
import dotenv
from langchain_openai import AzureChatOpenAI

# Load environment variables from .env file
dotenv.load_dotenv()

# Add error checking for environment variables
api_key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

# Debug: Print loaded values (remove after testing)
print(f"API Key loaded: {'Yes' if api_key else 'No'}")
print(f"Endpoint: {endpoint}")
print(f"API Version: {api_version}")

if not all([api_key, endpoint, api_version]):
    raise ValueError("Missing required environment variables")

llm = AzureChatOpenAI(
    api_key=api_key,
    azure_endpoint=endpoint,
    api_version=api_version,
    azure_deployment="gpt-4o-mini",
    temperature=0.5
)

# Example usage
response = llm.invoke("What is LLM?")
print(response.content)

