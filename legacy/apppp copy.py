
import streamlit as st
import time
from stock_copilot.legacy.epsilon_crew import create_crew, route_agent_to_tool_and_summarize, researcher
from tooling.polygon_tool import PolygonAPITool
from tooling.SEC_tool import SECApiTool  # Import the SEC API tool
from symbol import extract_stock_symbol
from report import generate_detailed_report

# Initialize the tools
polygon_tool = PolygonAPITool()
sec_tool = SECApiTool()

def submit_company():
    company_name = st.session_state.widget.strip().title()  # Normalize the company name
    if company_name:
        if company_name not in st.session_state["companies"]:
            st.session_state["companies"][company_name] = []
            st.session_state["active_company"] = company_name
            time.sleep(1)
            st.empty()
            st.success(f"New tab for {company_name} created!")
        else:
            st.session_state["active_company"] = company_name
            st.warning(f"Switched to {company_name}'s tab")
        
    # Clear the input field
    st.session_state.widget = ""

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



# Display company input bar only for Stock Analysis and Option tabs
if tab_selection in ["Stock Analysis", "Option"]:
    st.text_input("Enter Company Name", key="widget", placeholder="Apple, Google, Amazon,...", on_change=submit_company)
    
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
        time.sleep(1)
        st.empty()
    
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
                    st.markdown(f"**Finance Guru:** {entry['content']}")
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
        # Change subheader color to dark red
        st.markdown(f"<h3 style='color: #32CD32;'>{selected_company} 🏢</h3> ", unsafe_allow_html=True)
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

                    if stock_symbol:
                        st.warning(f"Generating detailed report for {stock_symbol}...")
                        
                        # Call generate_detailed_report with stock_symbol and display the result
                        result = generate_detailed_report(stock_symbol)

                        # Stream the result with character-by-character display (like your previous example)
                        response_placeholder = st.empty()
                        streamed_text = ""
                        for char in result:
                            streamed_text += char
                            response_placeholder.write(streamed_text)
                            time.sleep(0.005)  # Adjust for streaming effect

                        # Once streaming is done, clear and display the final response in a copyable format
                        response_placeholder.empty()
                        response_copyable = st.empty()
                        paragraph_format = streamed_text.replace("\n", "\n\n")
                        response_copyable.code(paragraph_format, language='markdown')

                        st.write("----------------------------------------")



                elif data_type == "Quick Ticker Data":
                    st.warning("Fetching quick ticker data...")
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
                                "Generate a concise, readable summary that explains the key details of this stock. Your output MUST have each sentence in a line to have more line breaks. Avoid paragraphs and make sure every line starts with a dash -."
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
                    st.warning("Fetching market trends...")
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
                    st.warning("Fetching SEC filing data...")
                    filing_data = sec_tool.get_filing_data(stock_symbol.upper())

                    if 'error' not in filing_data and "filings" in filing_data:
                        response_text = "Recent SEC Filings:\n"
                        
                        for idx, filing in enumerate(filing_data["filings"]):
                            filing_type = filing.get('formType', 'N/A')
                            filed_at = filing.get('filedAt', 'N/A')
                            filing_url = filing.get('linkToFilingDetails', '#')
                            
                            # Display filing header
                            filing_summary = f"**{idx+1}. {filing_type}** - Filed at {filed_at} [View filing]({filing_url})"
                            st.markdown(filing_summary)
                            response_text += f"{filing_summary}\n"

                            # Optional: Fetch full text of filing and display (controlled by a switch or button)
                            if st.button(f"Show full text for filing {idx+1}"):
                                filing_text = sec_tool.get_filing_full_text(filing_url)
                                st.write(filing_text)

                        update_conversation_history(selected_company, "assistant", response_text)
                    else:
                        response_text = "No recent filings available or an error occurred."
                        st.error(response_text)

                # Update conversation history with assistant's response
                #update_conversation_history(selected_company, "assistant", response_text)

# Option Tab
elif tab_selection == "Option":
    st.write("Options-related functionalities will be added soon.")

elif tab_selection == "General Questions":
    st.sidebar.subheader("General Questions")
    # Hide the company selection when this tab is selected
    selected_company = None
    st.sidebar.write("Company selection is hidden for general questions.")
    
    # Input for general question
    general_query = st.text_input("Ask a general question about the stock market, economy, etc.", placeholder="What is the current inflation rate?")

    if st.button("Submit"):
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

