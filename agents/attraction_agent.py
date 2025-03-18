import os
from langchain_community.vectorstores import Chroma
import chromadb
from langgraph.graph import Graph, END, START
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    HarmCategory,
    HarmBlockThreshold,
    GoogleGenerativeAIEmbeddings,
)

llm = ChatGoogleGenerativeAI(
    model=os.getenv("GOOGLE_MODEL"),
    safety_settings={
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
    },
)

# Define embedding function
embedding_function = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001", task_type="retrieval_query"
)

# Open vector database
current_directory = f"{os.path.dirname(__file__)}/mitre_rag_data"
chroma_db = os.path.join(current_directory, f"{current_directory}/.chromadb")

persistent_client = chromadb.PersistentClient(path=chroma_db)
db = Chroma(
    client=persistent_client,
    collection_name="groups_collection",
    embedding_function=embedding_function,
)
db.get()
retriever = db.as_retriever(search_kwargs={"k": 10})


# Create nodes
def linux_command_node(user_input):
    context = retriever.invoke(user_input)
    response = llm.invoke(
        f"""
        Context: {context}
        Given the user's prompt, you are to generate a Linux command to answer it. Provide no other formatting, just the command. \n\n  User prompt: {user_input}
        """
    )
    return response.content if hasattr(response, "content") else response


def user_check(linux_command):
    print(f"Linux command is: {linux_command}")
    user_ack = input("Should I execute this command? ")
    response = llm.invoke(
        f"""The following is the response the user gave to 'Should I execute this command?': {user_ack} \n\n  If the answer given is a negative one, return NO else return YES"""
    )
    response_text = response.content if hasattr(response, "content") else response
    if "YES" in response_text:
        return "linux_node"
    else:
        return END


def linux_node(linux_command):
    result = os.system(linux_command)
    return END


# Define graph
workflow = Graph()
workflow.add_node("linux_command_node", linux_command_node)
workflow.add_node("linux_node", linux_node)

workflow.add_edge(START, "linux_command_node")
workflow.add_conditional_edges("linux_command_node", user_check)
workflow.add_edge("linux_node", END)

app = workflow.compile()

print(
    "This is a human-in-the-loop Linux command-line tool.  Ask me to do perform a task and I will generate and execute it in the shell.  A blank line exits."
)
while True:
    line = input(">> ")
    try:
        if line:
            result = app.invoke(line)
            print(result)
        else:
            break
    except Exception as e:
        print(e)
