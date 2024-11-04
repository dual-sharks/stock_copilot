import streamlit as st
import time
from epsilon_crew import create_crew, route_agent_to_tool_and_summarize, researcher
from tooling.polygon_tool import PolygonAPITool
from tooling.SEC_tool import SECApiTool  # Import the SEC API tool

# Initialize the tools
polygon_tool = PolygonAPITool()
sec_tool = SECApiTool()

# Function to generate a detailed report using the Crew framework
def generate_detailed_report(topic):
    """Generate a detailed report using the Crew framework."""
    crew = create_crew(topic, researcher)
    result = route_agent_to_tool_and_summarize(researcher, topic)
    return result

# Initialize session state for conversation history
if "conversation" not in st.session_state:
    st.session_state["conversation"] = []

# Streamlit app function
def main():
    st.title("Stock Analysis and Data Hub")

    # Display conversation history from session state
    for entry in st.session_state["conversation"]:
        if entry["role"] == "user":
            st.markdown(f"**You:** {entry['content']}")
        else:
            st.markdown(f"**Assistant:** {entry['content']}")

    # User input section at the bottom of the app
    user_input = st.text_input("Enter your ticker symbol or topic", placeholder="e.g., 'AAPL' or 'AAPL analysis'")
    data_type = st.radio(
        "Choose data type:",
        ("Detailed Report", "Quick Ticker Data", "Market Trends", "SEC Filing Data")
    )

    if st.button("Generate"):
        if user_input:
            # Save user input in the session state and display it
            st.session_state["conversation"].append({"role": "user", "content": user_input})

            response_text = ""
            if data_type == "Detailed Report":
                st.write("Generating detailed report...")
                result = generate_detailed_report(user_input)
                response_text = result.content if result and hasattr(result, 'content') else "No relevant data found."
                st.markdown(f"**Assistant:** {response_text}")

            elif data_type == "Quick Ticker Data":
                st.write("Fetching quick ticker data...")
                ticker_data = polygon_tool.get_stock_info(user_input.upper())
                response_text = str(ticker_data) if 'error' not in ticker_data else ticker_data['error']
                if 'error' not in ticker_data:
                    st.json(ticker_data)
                else:
                    st.error(response_text)
                st.markdown(f"**Assistant:** {response_text}")

            elif data_type == "Market Trends":
                st.write("Fetching market trends...")
                market_trends = polygon_tool.analyze_market_trends(user_input.upper())
                response_text = market_trends if 'error' not in market_trends else market_trends['error']
                if 'error' not in market_trends:
                    st.markdown(market_trends)
                else:
                    st.error(response_text)
                st.markdown(f"**Assistant:** {response_text}")

            elif data_type == "SEC Filing Data":
                st.write("Fetching SEC filing data...")
                filing_data = sec_tool.get_filing_data(user_input.upper())
                
                if 'error' not in filing_data and "filings" in filing_data:
                    response_text = "Recent SEC Filings:\n"
                    for idx, filing in enumerate(filing_data["filings"]):
                        filing_type = filing.get('formType', 'N/A')
                        filed_at = filing.get('filedAt', 'N/A')
                        filing_url = filing.get('linkToTxt', '#')

                        filing_summary = f"**{idx + 1}. {filing_type} filed on {filed_at}**\n[View Filing]({filing.get('linkToFilingDetails', '#')})"
                        st.markdown(filing_summary)

                        if filing_url:
                            with st.spinner(f"Summarizing filing {idx + 1}..."):
                                summary = sec_tool.summarize_filing_content(filing_url)
                                st.markdown(f"**Summary**: {summary}")
                                st.markdown("---")
                                response_text += f"{idx + 1}. {filing_type} Summary: {summary}\n"
                    
                else:
                    response_text = filing_data.get('error', 'No filings found.')
                    st.error(response_text)
                    st.markdown(f"**Assistant:** {response_text}")

            # Save the response in the session state
            st.session_state["conversation"].append({"role": "assistant", "content": response_text})

        else:
            st.warning("Please enter a ticker symbol or topic before generating the report.")

if __name__ == "__main__":
    main()
