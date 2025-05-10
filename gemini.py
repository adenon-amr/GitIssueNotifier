from google import genai
from pydantic import BaseModel
from config import GEMINI_API_KEY

class GeminiResponse(BaseModel):
    difficulty_level: str
    difficulty_number: int
    estimated_hours: int
    explanation: str
    resources: list[str]

def analyze_github_issue(issue):
    title = issue["title"]
    description = issue["body"] or "No description provided."
    
    prompt = f"""
    Please analyze the following GitHub issue and provide the following details to help the user understand how to approach and solve it:

    1. Difficulty Level: Provide a difficulty rating from 1 to 10, followed by a brief description of why you assigned that rating.
    2. Estimated Time to Code: Estimate the number of hours required to complete the issue.
    3. Explanation: Provide a brief explanation of how to approach solving the issue in no more than two short paragraphs.
    4. Learning Resources: Suggest 3-5 links to tutorials, documentation, or courses to help the user learn the necessary skills to solve this issue.

    GitHub Issue:
    - Title: {title}
    - Description: {description}
    """

    client = genai.Client(api_key=GEMINI_API_KEY)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt],
        config={
            "response_mime_type": "application/json",
            "response_schema": GeminiResponse,
        }
    )

    response_data = response.parsed
    return response_data.dict()
