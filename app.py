from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, HumanMessage
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import START, StateGraph
from langgraph.checkpoint.memory import InMemorySaver


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


def build_agent(model, tools):
    """Build the same tool loop for the CLI and other callers."""
    model_with_tool = model.bind_tools(tools)

    def assistant(state: AgentState):
        return {"messages": [model_with_tool.invoke(state["messages"])]}

    builder = StateGraph(AgentState)

    builder.add_node("assistant", assistant)
    builder.add_node('tools',ToolNode(tools))

    builder.add_edge(START,'assistant')
    builder.add_conditional_edges(
        'assistant',
        tools_condition
    )
    builder.add_edge('tools','assistant')

    checkpointer = InMemorySaver()

    return builder.compile(checkpointer=checkpointer)


def main():
    # Importing the graph does not load the dataset or start an interactive CLI.
    from langchain_ollama import ChatOllama
    from tool import web_search_tool, get_weather_tool, hub_stats_tool
    from retriever import guest_info_tool_1

    model = ChatOllama(
        model="qwen2.5:1.5b",
        base_url="http://127.0.0.1:11434",
        num_predict=256,
    )
    tools = [get_weather_tool, web_search_tool, get_weather_tool,
             hub_stats_tool, guest_info_tool_1]
    alfred = build_agent(model, tools)
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


if __name__ == "__main__":
    main()
