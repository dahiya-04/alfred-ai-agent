import datasets
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver  
from langchain_community.tools import DuckDuckGoSearchRun

from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage , SystemMessage
from langgraph.prebuilt import ToolNode
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition
from langchain_ollama import ChatOllama



# Load the dataset
guest_dataset = datasets.load_dataset("agents-course/unit3-invitees", split="train")

# Convert dataset entries into Document objects
docs = [
    Document(
        page_content="\n".join([
            f"Name: {guest['name']}",
            f"Relation: {guest['relation']}",
            f"Description: {guest['description']}",
            f"Email: {guest['email']}"
        ]),
        metadata={"name": guest["name"]}
    )
    for guest in guest_dataset
]

bm25_retriever = BM25Retriever.from_documents(docs)

checkpointer = InMemorySaver()
@tool
def guest_info_tool_1(query: str) -> str:
    """Retrieves detailed information about gala guests based on their name or relation."""
    results = bm25_retriever.invoke(query)
    if results:
        ans =  "\n\n".join([doc.page_content for doc in results[:1]])
        prompt = f"""
            Based on the following guest information, suggest 3 conversation starters.

            Guest info:
            {ans}

            Format:
            Guest Information
            Conversation Starters
            """
        response = model.invoke(ans)
        return response.content
    else:
        return "No matching guest information found."
    

# search = DuckDuckGoSearchRun()

# @tool
# def web_search_tool(query: str) -> str:
#     """Search the web for information about unfamiliar guests."""
#     return search.run(query)


model = ChatOllama(
        model="qwen2.5:1.5b",  # Or try other Ollama-supported models
        base_url="http://127.0.0.1:11434",  # Default Ollama local server
            num_predict=256
        )

# tools=[guest_info_tool_1,web_search_tool]
# model = model.bind_tools(tools)

# # create Graph for better use
# class AgentState(TypedDict):
#     messages : Annotated[list[AnyMessage],add_messages]

# def assistant(state:AgentState):

#     system_prompt = SystemMessage(
#         content=(
#             "You are Alfred, Bruce Wayne's intelligent assistant managing a gala guest list.\n"
#             "You have access to two tools:\n"
#             "1. guest_info_tool_1 → use this when the guest might be in the gala dataset.\n"
#             "2. web_search_tool → use this when the guest is not found in the dataset or you need latest information.\n\n"
#             "Always prefer using tools instead of guessing."
#         )
#     )

#     messages = [system_prompt] + state["messages"]

#     response = model.invoke(messages)
#     return {
#         'messages':[response]
#     }

# builder = StateGraph(AgentState)

# builder.add_node("assistant", assistant)
# builder.add_node("tools", ToolNode(tools))

# # Define edges: these determine how the control flow moves
# builder.add_edge(START, "assistant")
# builder.add_conditional_edges(
#     "assistant",
#     # If the latest message requires a tool, route to tools
#     # Otherwise, provide a direct response
#     tools_condition,
# )
# builder.add_edge("tools", "assistant")

# alfred = builder.compile(checkpointer=checkpointer)


# messages = [HumanMessage(content="Tell me about our guest named 'Lady Ada Lovelace' ?")]
# response = alfred.invoke(
#     {"messages": messages},
#      {"configurable": {"thread_id": "1"}},
#      )

# print("🎩 Alfred's Response:")
# # print(response['messages'][-1].content)


# for msg in response["messages"]:
#     print(type(msg).__name__, ":", msg.content)