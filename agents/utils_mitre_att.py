# This script downloads the real-time Mitre ATT&CK information on a variety of
# attack groups, formats them in Markdown files, then loads them into a vector
# database (ChromaDB).  This is subsequently used in a RAG chain to handle
# queries through an LLM
from attackcti import attack_client
import os
import re
import copy
import glob
from jinja2 import Template
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import UnstructuredMarkdownLoader

current_directory = f"{os.path.dirname(__file__)}/mitre_rag_data/"
documents_directory = os.path.join(current_directory, "documents")
if not os.path.exists(documents_directory):
    os.makedirs(documents_directory)

lift = attack_client()
techniques_used_by_groups = lift.get_techniques_used_by_all_groups()
techniques_used_by_groups[0]

# Create Group docs
all_groups = dict()
for technique in techniques_used_by_groups:
    if technique["id"] not in all_groups:
        group = dict()
        group["group_name"] = technique["name"]
        group["group_id"] = technique["external_references"][0]["external_id"]
        group["created"] = technique["created"]
        group["modified"] = technique["modified"]
        group["description"] = technique["description"]
        group["aliases"] = technique["aliases"]
        if "x_mitre_contributors" in technique:
            group["contributors"] = technique["x_mitre_contributors"]
        group["techniques"] = []
        all_groups[technique["id"]] = group
    technique_used = dict()
    technique_used["matrix"] = technique["technique_matrix"]
    technique_used["domain"] = technique["x_mitre_domains"]
    technique_used["platform"] = technique["platform"]
    technique_used["tactics"] = technique["tactic"]
    technique_used["technique_id"] = technique["technique_id"]
    technique_used["technique_name"] = technique["technique"]
    technique_used["use"] = technique["relationship_description"]
    if "data_sources" in technique:
        technique_used["data_sources"] = technique["data_sources"]
    all_groups[technique["id"]]["techniques"].append(technique_used)

print("[+] Creating markdown files for each group..")
group_template = os.path.join(current_directory, "group_template.md")
markdown_template = Template(open(group_template).read())
for key in list(all_groups.keys()):
    group = all_groups[key]
    print("  [>>] Creating markdown file for {}..".format(group["group_name"]))
    group_for_render = copy.deepcopy(group)
    markdown = markdown_template.render(
        metadata=group_for_render,
        group_name=group["group_name"],
        group_id=group["group_id"],
    )
    file_name = (group["group_name"]).replace(" ", "_")
    open(f"{documents_directory}/{file_name}.md", encoding="utf-8", mode="w").write(
        markdown
    )


# Load data do DB
current_directory = f"{os.path.dirname(__file__)}/mitre_rag_data/"
documents_directory = os.path.join(current_directory, "documents")

group_files = glob.glob(os.path.join(documents_directory, "*.md"))

# Loading Markdown files
md_docs = []
print("[+] Loading Group markdown files..")
for group in group_files:
    print(f" [*] Loading {os.path.basename(group)}")
    loader = UnstructuredMarkdownLoader(group)
    md_docs.extend(loader.load_and_split())

print(f"[+] Number of .md documents processed: {len(md_docs)}")

# Define the embedding function
embedding_function = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001", task_type="retrieval_query"
)

# Load documents into Chroma and save it to disk
vectorstore = Chroma.from_documents(
    md_docs,
    embedding_function,
    collection_name="groups_collection",
    persist_directory=f"{current_directory}/.chromadb",
)
retriever = vectorstore.as_retriever()

print("RAG database initialized.")
