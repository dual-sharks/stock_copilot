from langchain_openai import ChatOpenAI
import os

# Initialize LLM for symbol extraction
llm = ChatOpenAI(model_name="gpt-4", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))

# Function to extract stock symbol from company name
def extract_stock_symbol(company_name):
    prompt = f"Extract the stock symbol for the company '{company_name}'. For example, Apple -> AAPL, Google -> GOOGL. You MUST return ONLY the stock symbol with no other text with it."
    
    # Get the response from the LLM
    response = llm.predict(prompt)
    
    # Assuming response is the symbol, clean it
    stock_symbol = response.strip().upper()  # Ensures symbol is uppercase
    return stock_symbol
