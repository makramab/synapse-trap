import os
import requests
from langchain.agents
from pydantic import BaseModel, Field, model_validator
from langchain.tools import tool
from langchain_google_genai import GoogleGenerativeAI, HarmCategory, HarmBlockThreshold
import re

# Set up OpenCVE credentials from environment variables
OPENCVE_USERNAME = os.getenv("OPENCVE_USERNAME")
OPENCVE_PASSWORD = os.getenv("OPENCVE_PASSWORD")

# Define the LLM
llm = GoogleGenerativeAI(
    model="gemini-1.5-pro-latest",
    temperature=0,
    safety_settings={
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    },
)


# Define OpenCVE API tools
class CVE_ID(BaseModel):
    cve_id: str = Field(description="Should be a CVE ID such as CVE-2022-1234")

    @model_validator(mode="before")
    def is_valid_cve_id(cls, values: dict[str, any]) -> dict[str, any]:
        cve_pattern = re.compile(r"^CVE-\d{4}-\d{4,}$")
        if cve_pattern.match(values.get("cve_id")):
            return values
        raise ValueError("Malformed CVE ID")


@tool("cve_by_id", args_schema=CVE_ID, return_direct=False)
def cve_by_id(cve_id):
    """Lookup CVE given its ID"""
    url = f"https://app.opencve.io/api/cve/{cve_id}"
    response = requests.get(url, auth=(OPENCVE_USERNAME, OPENCVE_PASSWORD))
    if response.status_code == 200:
        return response.json()


class CWE_ID(BaseModel):
    cwe_id: str = Field(description="Should be a CWE ID such as CWE-123")

    @model_validator(mode="before")
    def is_valid_cwe_id(cls, values: dict[str, any]) -> dict[str, any]:
        cwe_pattern = re.compile(r"^CWE-\d{1,}$")
        if cwe_pattern.match(values.get("cwe_id")):
            return values
        raise ValueError("Malformed CWE ID")


@tool("cwe_by_id", args_schema=CWE_ID, return_direct=False)
def cwe_by_id(cwe_id):
    """Lookup weaknesses and CWE given its ID"""
    url = f"https://app.opencve.io/api/weaknesses/{cwe_id}"
    response = requests.get(url, auth=(OPENCVE_USERNAME, OPENCVE_PASSWORD))
    if response.status_code == 200:
        return response.json()


# Integrate the tools with the LLM
tools = [cve_by_id, cwe_by_id]
