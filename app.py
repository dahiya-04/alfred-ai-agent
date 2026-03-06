from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
from langgraph.prebuilt import ToolNode
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition
from langgraph.checkpoint.memory import InMemorySaver  
from langchain_ollama import ChatOllama
from tool import DuckDuckGoSearchRun,web_search_tool,latest_news_tool, get_weather_tool as weather_info_tool, hub_stats_tool
from retriever import guest_info_tool_1




model = ChatOllama(
        model="qwen2.5:1.5b",  # Or try other Ollama-supported models
        base_url="http://127.0.0.1:11434",  # Default Ollama local server
            num_predict=256
        )

tools=[weather_info_tool,web_search_tool,weather_info_tool,hub_stats_tool,guest_info_tool_1]
model_with_tool = model.bind_tools(tools)

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage],add_messages]


def assistant(state: AgentState):
    return {
        "messages": [model_with_tool.invoke(state["messages"])],
    }

builder = StateGraph(AgentState)

builder.add_node("assistant",assistant)
builder.add_node('tools',ToolNode(tools))

builder.add_edge(START,'assistant')
builder.add_conditional_edges(
    'assistant',
    tools_condition
)
builder.add_edge('tools','assistant')

checkpointer = InMemorySaver()

alfred = builder.compile(checkpointer=checkpointer)
thread_config = {"configurable": {"thread_id": "1"}}

print("🎩 Alfred: Hello, I am Alfred. How can I assist you today?")
print("Type 'exit' or 'quit' to stop.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit"]:
        print("Alfred: Goodbye.")
        break

    response = alfred.invoke(
        {"messages": [HumanMessage(content=user_input)]},
        thread_config
    )

    ai_reply = response["messages"][-1].content

    print("\n🎩 Alfred:", ai_reply)
    print("-" * 40)