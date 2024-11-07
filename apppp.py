
import streamlit as st
import time
from epsilon_crew import create_crew, route_agent_to_tool_and_summarize, researcher
from tooling.polygon_tool import PolygonAPITool
from tooling.SEC_tool import SECApiTool  # Import the SEC API tool
from symbol import extract_stock_symbol

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
    st.session_state["conversation"] = {}

# Initialize session state for companies
if "companies" not in st.session_state:
    st.session_state["companies"] = {}

# Initialize session state for active company
if "active_company" not in st.session_state:
    st.session_state["active_company"] = None

# App layout configuration
st.set_page_config(page_title="Stock Analysis and Data Hub", page_icon="💹", layout="wide")
st.title("Stock Analysis and Data Hub")

# Sidebar for tab selection and company list
tab_selection = st.sidebar.selectbox("Select a Tab", ["Stock Analysis", "Option", "General Questions"])

# Main page content
company_name_input = st.text_input("Enter Company Name", placeholder="Apple, Google, Amazon,...")

# Handle company input logic
if company_name_input:
    company_name = company_name_input.strip().title()  # Normalize the company name

    # If the company doesn't exist, create a new one
    if company_name not in st.session_state["companies"]:
        st.session_state["companies"][company_name] = []
        st.session_state.active_company = company_name
        st.write(f"New tab for {company_name} created!")
    else:
        st.session_state.active_company = company_name
        st.write(f"Switched to {company_name}'s tab")

    # Clear the input after submission
    st.session_state["company_input"] = ""  # Reset the input field


# Helper function to update conversation history for a specific company
def update_conversation_history(company, role, content):
    if company not in st.session_state["conversation"]:
        st.session_state["conversation"][company] = []
    st.session_state["conversation"][company].append({"role": role, "content": content})

# Helper function to delete the conversation history for a specific company and remove from the sidebar
def delete_conversation_history(company):
    # Remove the company's conversation history (if any)
    if company in st.session_state["conversation"]:
        del st.session_state["conversation"][company]
    
    # Remove the company from the companies list (sidebar)
    if company in st.session_state["companies"]:
        del st.session_state["companies"][company]
    
    # Ensure active company is updated after deletion
    if st.session_state["active_company"] == company:
        if st.session_state["companies"]:
            st.session_state["active_company"] = list(st.session_state["companies"].keys())[0]
            st.write(f"Switched to {st.session_state['active_company']}.")
        else:
            st.session_state["active_company"] = None
    
    st.success(f"Company '{company}' will be deleted from the sidebar. Confirm?")

# Display conversation history for a specific company
def display_conversation_history(company, visible=True):
    if company in st.session_state["conversation"]:
        if visible:
            for entry in st.session_state["conversation"][company]:
                if entry["role"] == "user":
                    st.markdown(f"**You:** {entry['content']}")
                else:
                    st.markdown(f"**Assistant:** {entry['content']}")
        else:
            st.markdown("Conversation history is hidden.")
    else:
        st.markdown("No conversation history yet.")

# Stock Analysis Tab
if tab_selection == "Stock Analysis":
    # Display the list of companies directly on the sidebar
    if st.session_state["companies"]:
        selected_company = st.sidebar.radio(
        "Select a Company", 
        list(st.session_state["companies"].keys()), 
        key="company_selectbox",
        index=list(st.session_state["companies"].keys()).index(st.session_state["active_company"]) if st.session_state["active_company"] else 0
    )
    else:
        selected_company = None
        st.sidebar.write("No companies available.")

    if selected_company:
        display_conversation_history(selected_company, visible=True)

        # Adding a button to delete conversation history and remove from sidebar
        delete_button = st.button(f"Delete {selected_company}'s Chat History and Remove")
        if delete_button:
            delete_conversation_history(selected_company)

        # Selecting data type for the chosen company
        data_type = st.radio(
            "Choose data type:",
            ("Detailed Report", "Quick Ticker Data", "Market Trends", "SEC Filing Data")
        )

        if st.button("Generate"):
            if selected_company:
                # Save user input in session state and display it
                update_conversation_history(selected_company, "user", selected_company)
                response_text = ""
                stock_symbol = extract_stock_symbol(selected_company)
                st.write(f"Stock symbol for {selected_company} is {stock_symbol}.")
                if data_type == "Detailed Report":
                    st.write("Generating detailed report...")
                    result = generate_detailed_report(stock_symbol)
                    st.markdown(f"**Assistant:** {result}")
                    response_text = result

                elif data_type == "Quick Ticker Data":
                    st.write("Fetching quick ticker data...")
                    ticker_data = polygon_tool.get_stock_info(stock_symbol.upper())
                    response_text = str(ticker_data) if 'error' not in ticker_data else ticker_data['error']

                    if 'error' not in ticker_data:
                        # Create two columns: one for JSON and one for the LLM-generated text
                        col1, col2 = st.columns(2)

                        with col1:
                            st.subheader("Ticker JSON Data")
                            st.json(ticker_data)  # Display raw JSON data

                        with col2:
                            st.subheader("Summary")
                            # Send JSON data to LLM to generate a textual summary
                            ticker_summary_prompt = (
                                f"Here is the stock data for {stock_symbol}:\n\n{str(ticker_data)}\n"
                                "Generate a concise, readable summary that explains the key details of this stock. Your output MUST have each sentence in a line to have more line breaks."
                            )
                            # Get the summary from LLM
                            summary_response = polygon_tool.llm(ticker_summary_prompt)
                            summary_text = summary_response.content if hasattr(summary_response, 'content') else str(summary_response)

                            # Stream the response character by character
                            response_placeholder = st.empty()
                            streamed_text = ""
                            for char in summary_text:
                                streamed_text += char
                                response_placeholder.write(streamed_text)
                                time.sleep(0.005)  # Adjust for streaming effect

                            # Once streaming is done, clear and display final response in a copyable format
                            response_placeholder.empty()
                            response_copyable = st.empty()
                            paragraph_format = streamed_text.replace("\n", "\n\n")
                            response_copyable.code(paragraph_format, language='markdown')
                            update_conversation_history(selected_company, "assistant", streamed_text)
                            st.write("----------------------------------------")
                    else:
                        st.error(response_text)

                elif data_type == "Market Trends":
                    st.write("Fetching market trends...")
                    market_trends = polygon_tool.analyze_market_trends(stock_symbol.upper())
                    response_text = market_trends if 'error' not in market_trends else market_trends['error']

                    if 'error' not in market_trends:
                        # Create a placeholder for streaming the text
                        response_placeholder = st.empty()
                        streamed_text = ""
                        
                        # Stream the response character by character for a delay effect
                        for char in response_text:
                            streamed_text += char
                            response_placeholder.write(streamed_text)
                            time.sleep(0.005)  # Adjust for streaming effect
                        
                        # Once streaming is done, clear and display the final response in a copyable format
                        response_placeholder.empty()

                        # Format the text for better readability (paragraphs)
                        paragraph_format = streamed_text.replace("\n", "\n\n")

                        # Display the text as markdown for easier copying
                        response_copyable = st.empty()
                        response_copyable.code(paragraph_format, language='markdown')

                        # Update conversation history
                        update_conversation_history(selected_company, "assistant", streamed_text)
                        st.write("----------------------------------------")
                    else:
                        st.error(response_text)

                elif data_type == "SEC Filing Data":
                    st.write("Fetching SEC filing data...")
                    filing_data = sec_tool.get_filing_data(stock_symbol.upper())

                    if 'error' not in filing_data and "filings" in filing_data:
                        response_text = "Recent SEC Filings:\n"
                        
                        for idx, filing in enumerate(filing_data["filings"]):
                            filing_type = filing.get('formType', 'N/A')
                            filed_at = filing.get('filedAt', 'N/A')
                            filing_url = filing.get('linkToFilingDetails', '#')
                            
                            # Display filing header
                            filing_summary = f"**{idx + 1}. {filing_type} filed on {filed_at}**\n[View Filing]({filing.get('linkToFilingDetails', '#')})"
                            st.markdown(filing_summary)

                            # Stream the summary for each filing
                            if filing_url:
                                with st.spinner(f"Summarizing filing {idx + 1}..."):
                                    summary = sec_tool.summarize_filing_content(filing_url)

                                    # Streaming effect for each summary
                                    response_placeholder = st.empty()
                                    streamed_text = ""
                                    for char in summary:
                                        streamed_text += char
                                        response_placeholder.write(streamed_text)
                                        time.sleep(0.005)  # Adjust the delay for streaming effect

                                    # Once streaming is done, clear the placeholder
                                    response_placeholder.empty()

                                    # Display the summary in a copyable format
                                    response_copyable = st.empty()
                                    paragraph_format = streamed_text.replace("\n", "\n\n")
                                    response_copyable.code(paragraph_format, language='markdown')

                                    # Update the response text for conversation history
                                    response_text += f"{idx + 1}. {filing_type} Summary: {summary}\n"
                                    st.markdown("---")

                        # Update conversation history with the final response text
                        update_conversation_history(selected_company, "assistant", response_text)
                        st.write("----------------------------------------")
                        
                    else:
                        response_text = filing_data.get('error', 'No filings found.')
                        st.error(response_text)

elif tab_selection == "General Questions":
    st.sidebar.subheader("General Questions")
    # Hide the company selection when this tab is selected
    selected_company = None
    st.sidebar.write("Company selection is hidden for general questions.")
    
    # Input for general question
    general_query = st.text_input("Ask a general question:")

    if st.button("Get General Response"):
        with st.spinner("Loading..."):
            # Construct the prompt for general finance-related questions
            general_prompt = f"Your output MUST have each sentence in a line to have more line breaks. Please provide a detailed and concise response to the following question related to finance:\n\n{general_query}\n"
            
            # Get the response from the LLM
            general_answer = polygon_tool.llm(general_prompt)
            
            # Stream the response character by character
            response_placeholder = st.empty()
            response_text = ""
            for char in general_answer.content:
                response_text += char
                response_placeholder.write(response_text)
                time.sleep(0.005)  # Adjust the delay for streaming effect
            
            response_placeholder.empty()  # Clear streaming placeholder
            st.subheader("Response")
            st.code(response_text, language='markdown')  # Displaying the answer in a code block


            
# Hide conversation history in other tabs
else:
    if selected_company:
        display_conversation_history(selected_company, visible=False)
