import base64
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
load_dotenv()

def generate_answer_gemini(query, context_chunks, gemini_model_name="gemini-2.0-flash-thinking-exp-01-21"):
    """
    Generates an answer using the Gemini API, given a query and context chunks.

    Args:
        query (str): The user query.
        context_chunks (list): A list of dictionaries, where each dictionary represents a retrieved chunk
                               and contains 'content' and 'source' keys.
        gemini_model_name (str, optional): The Gemini model to use.
                                           Defaults to "gemini-2.0-flash-thinking-exp-01-21".

    Returns:
        str: The generated answer from the Gemini API.
    """
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = gemini_model_name
    context_text = "\n\n".join([chunk["content"] for chunk in context_chunks])

    prompt = f"""Answer the question based on the context below.
    Context:
    {context_text}

    Question: {query}

    Answer:
    """

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=0.7,
        top_p=0.95,
        top_k=64,
        max_output_tokens=65536,
        response_mime_type="text/plain",
        system_instruction=open("system_instructions.md", "r").read(),  # Load system instruction from file
    )

    generated_text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        generated_text += chunk.text

    return generated_text.strip()
