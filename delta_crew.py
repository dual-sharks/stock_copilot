from textwrap import dedent
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

# Set up the LLM
llm = ChatOpenAI(model_name="gpt-4", temperature=0.7)

# Define the agents with a more generic purpose
manager = Agent(
    role="Project Manager",
    goal="Efficiently manage the crew and ensure high-quality task completion",
    backstory="You're an experienced project manager, skilled in overseeing complex projects and guiding teams to success. Your role is to coordinate the efforts of the crew members, ensuring that each task is completed on time and to the highest standard.",
    allow_delegation=True,
)

researcher = Agent(
    role="Researcher",
    goal="Conduct thorough research on any given topic",
    backstory="You're a versatile researcher, capable of delving into any subject matter with attention to detail and thorough analysis.",
    allow_delegation=False,
)

writer = Agent(
    role="Writer",
    goal="Create well-crafted reports on any given topic",
    backstory="You're an experienced writer who can produce high-quality content across various domains.",
    allow_delegation=False,
)

def create_crew(topic):
    """Create a dynamic Crew instance based on the provided topic."""
    task = Task(
        description=dedent(
            f"""
            Write a comprehensive report on the topic: {topic}.
            Include key points, in-depth analysis, and important takeaways.
            """
        ),
        expected_output="Detailed report with analysis and takeaways."
    )

    crew = Crew(
        agents=[researcher, writer],
        tasks=[task],
        manager_agent=manager,
        process=Process.hierarchical,
    )

    return crew
