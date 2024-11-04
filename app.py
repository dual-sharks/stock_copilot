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

# Streamlit app function
def main():
    st.title("Stock Analysis and Data Hub")
    st.write("Select the type of data you want to view:")

    # User selection for data type
    data_type = st.radio(
        "Choose data type:",
        ("Detailed Report", "Quick Ticker Data", "Market Trends", "SEC Filing Data")
    )

    # User input for the topic or ticker symbol
    user_input = st.text_input("Enter your ticker symbol or topic", placeholder="e.g., 'AAPL' or 'AAPL analysis'")

    if st.button("Generate"):
        if user_input:
            if data_type == "Detailed Report":
                # Use the Crew framework for complex report generation
                st.write("Generating detailed report...")
                result = generate_detailed_report(user_input)

                if result and hasattr(result, 'content'):
                    report_text = result.content
                else:
                    report_text = str(result)

                if report_text:
                    st.write("Generated Summary Report:")
                    placeholder = st.empty()

                    words = report_text.split()
                    full_text = ""
                    for word in words:
                        full_text += word + " "
                        placeholder.markdown(f"{full_text}")
                        time.sleep(0.05)  # Adjust speed as needed
                else:
                    st.warning("No relevant data found.")

            elif data_type == "Quick Ticker Data":
                # Fetch ticker data quickly using the Polygon API tool
                st.write("Fetching quick ticker data...")
                ticker_data = polygon_tool.get_stock_info(user_input.upper())

                if 'error' not in ticker_data:
                    st.write("Quick Ticker Data:")
                    st.json(ticker_data)
                else:
                    st.error(ticker_data['error'])

            elif data_type == "Market Trends":
                st.write("Fetching market trends...")
                market_trends = polygon_tool.analyze_market_trends(user_input.upper())

                if 'error' not in market_trends:
                    st.write("Market Trend Summary and Sentiment Analysis:")
                    st.markdown(market_trends)
                else:
                    st.error(market_trends)

            elif data_type == "SEC Filing Data":
                # Fetch SEC filing data using the SECApiTool
                st.write("Fetching SEC filing data...")
                filing_data = sec_tool.get_filing_data(user_input.upper())
                
                if 'error' not in filing_data and "filings" in filing_data:
                    st.write("Recent SEC Filings:")
                    for idx, filing in enumerate(filing_data["filings"]):
                        filing_type = filing.get('formType', 'N/A')
                        filed_at = filing.get('filedAt', 'N/A')
                        filing_url = filing.get('linkToTxt', '#')

                        st.markdown(f"**{idx + 1}. {filing_type} filed on {filed_at}**")
                        st.markdown(f"[View Filing]({filing.get('linkToFilingDetails', '#')})")

                        if filing_url:
                            with st.spinner(f"Summarizing filing {idx + 1}..."):
                                summary = sec_tool.summarize_filing_content(filing_url)
                                st.markdown(f"**Summary**: {summary}")
                                st.markdown("---")
                else:
                    st.error(filing_data.get('error', 'No filings found.'))
        else:
            st.warning("Please enter a ticker symbol or topic before generating the report.")

if __name__ == "__main__":
    main()
