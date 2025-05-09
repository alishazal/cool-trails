from openai import OpenAI
import json
import os

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI()

PACKING_REC_SCHEMA = {
        "type": "json_schema",
        "json_schema": {
            "name": "packing_recommendation_response",
            "schema": {
                "type": "object",
                "properties": {
                    "packing_recommendations": {
                        "type": "array",
                        "description": "A list of packing recommendations.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "The name of the item to pack.",
                                },
                                "quantity": {
                                    "type": "string",
                                    "description": "The quantity of the item to pack.",
                                },
                                "explanation": {
                                    "type": "string",
                                    "description": "An explanation on why you should pack the item.",
                                },
                            },
                            "required": ["name", "quantity", "explanation"],
                            "additionalProperties": False,
                        },
                    }
                },
                "required": ["packing_recommendations"],
                "additionalProperties": False
            },
            "strict": True
        }
    }

def get_completion(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano-2025-04-14",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format=PACKING_REC_SCHEMA,
        )
        return response
    except Exception as e:
        print(f"Error generating completion for: {prompt[:50]}... - {str(e)}")
        raise e

def get_response_json(completion):
    return json.loads(completion.choices[0].message.content)

def get_completion_json(llm_input):
    completion = get_completion(llm_input)
    json = get_response_json(completion)
    return json

