from textwrap import dedent
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from tooling.polygon_api_tool import PolygonAPITool
from utils import route_agent_to_tool_and_summarize

# Initialize the Polygon API tool
polygon_tool = PolygonAPITool()

# Set up the LLM
llm = ChatOpenAI(model_name="gpt-4", temperature=0.7)

# Initialize agents
manager = Agent(
    role="Project Manager",
    goal="Efficiently manage the crew and ensure high-quality task completion",
    backstory="You're an experienced project manager, skilled in overseeing complex projects.",
    allow_delegation=True
)

researcher = Agent(
    role="Researcher",
    goal="Conduct thorough research on any given topic. If the topic is related to stocks, use the stock tool to fetch data.",
    backstory="You're a versatile researcher, capable of delving into any subject matter.",
    allow_delegation=False,
    tools=[polygon_tool],  # Add the tool for stock data retrieval
    llm=llm
)

writer = Agent(
    role="Writer",
    goal="Create well-crafted reports on any given topic",
    backstory="You're an experienced writer who can produce high-quality content across various domains.",
    allow_delegation=False,
    llm=llm
)

# Function to create a dynamic crew instance
def create_crew(topic, agent):
    """Create a dynamic Crew instance with the agent assigned to the task."""
    task = Task(
        description=dedent(
            f"""
            Write a comprehensive report on the topic: {topic}.
            Include key points, in-depth analysis, and takeaways.
            """
        ),
        expected_output="Detailed report with analysis and takeaways.",
        agent=agent
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential
    )
    return crew

# Function to generate a detailed report using the Crew framework
def generate_detailed_report(topic):
    """Generate a detailed report using the Crew framework."""
    crew = create_crew(topic, researcher)
    result = route_agent_to_tool_and_summarize(researcher, topic)
    return result
