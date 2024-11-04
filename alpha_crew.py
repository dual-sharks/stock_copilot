from textwrap import dedent
from crewai import Agent, Task, Crew
import os
from langchain_openai import ChatOpenAI
os.environ["OPENAI_API_KEY"] = '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'
llm = OpenAIGPT4 = ChatOpenAI(model_name="gpt-4", temperature=0.7)
fingus = Agent(
            role="Define agent 1 role here",
            backstory=dedent(f"""Agent 1 is always trying to tell the best riddle"""),
            goal=dedent(f"""Answer the question in the form of a riddle no matter what"""),
            expected_output="string",
            # tools=[tool_1, tool_2],
            allow_delegation=False,
            verbose=True,
            llm=llm,
        )

lask = Task(
            description=dedent(
                f"""
            Do something as part of task 1
            
    
       tell me something mysterious
        """
            ),
            agent=fingus,
            expected_output="string"
        )


crew = Crew(
            agents=[fingus],
            tasks=[lask],
            verbose=True,
        )
def first_chatbot():
    crew = Crew(
            agents=[fingus],
            tasks=[lask],
            verbose=True,
        )
    result = crew.kickoff()
    return result