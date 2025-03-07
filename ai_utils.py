import cohere
from dotenv import load_dotenv
import os

load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")

conn=cohere.Client(COHERE_API_KEY)

MIN_WORDS=20
WORD_LIMIT=50

async def enhance_description(title:str, description:str)->str:
    if len(description.split())<MIN_WORDS:
        prompt =f"""
            Write a compelling and engaging real estate property description in a single paragraph (max {WORD_LIMIT} words).
            Use the title '{title}' for context. Expand on the key features while keeping it concise and professional.
            Avoid phrases like 'Sure, here is a description' or any introductory text.
            Only return the final property description, nothing else.\n\n
            Given description: {description}
        """  
        response=conn.generate(prompt=prompt)
        return response.generations[0].text.strip()
    return description

async def generate_keywords(title:str,description:str)->str:
    prompt = f"""
        Extract the most relevant keywords from the following real estate listing title and description.
        Return a comma separated list without any other details including introductory or conclusion texts.
        Avoid phrases like 'Sure, here are the keywords' or any introductory text.
        Only return the final required keywords, nothing else.\n\n
        Title: {title}\n
        Description: {description}
    """
    response=conn.generate(prompt=prompt)
    return response.generations[0].text.strip()

# print(generate_keywords("Luxury Apartment","A beautiful apartment in the heart of the city with stunning views of the skyline."))