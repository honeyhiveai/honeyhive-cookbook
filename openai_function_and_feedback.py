import honeyhive
import json
from honeyhive.sdk.tracer import HoneyHiveTracer
from openai import OpenAI

open_key = "OPENAI_API_KEY"
hhai_key = "HONEYHIVE_API_KEY"
honeyhive.api_key = hhai_key

project_name = "New Project"

client = OpenAI(
    api_key=open_key
)

# Instatiate your HoneyHiveTracer
honeyhive_tracer = HoneyHiveTracer(
    project=project_name,
    name="Weather Bot",
    source="testing"
)

# Calling a dummy function
def get_current_weather(location, format):
    return "It's 40 degrees " + format + " and rainy in " + location + "."

# A function to add function response to messages
def execute_function_call(message, honeyhive_tracer):
    function_call_args = json.loads(message["tool_calls"][0]["function"]["arguments"])
    if message["tool_calls"][0]["function"]["name"] == "get_current_weather":
        with honeyhive_tracer.tool(
            event_name="get_current_weather"
        ):
            results = get_current_weather(function_call_args["location"], function_call_args["format"])
    else:
        results = f"Error: function {message['tool_calls'][0]['function']['name']} does not exist"
    return results

# Tools, required for OpenAI API
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this from the users location.",
                    },
                },
                "required": ["location", "format"],
            },
        }
    }
]

# construct system message, neatly
sys_msg = "Don't make assumptions about what values to plug into functions."
sys_msg += " Ask for clarification if a user request is ambiguous."

#basic messages list
messages = []
messages.append({"role": "system", "content": sys_msg})
messages.append({"role": "user", "content": "What's the weather like today in {{location}}"})

function_output_field = "choices.0.message.tool_calls.0.function"
model_output_field = "choices.0.message.content"

input_dict = {"location": "NYC"}

# weather_function_call step in pipeline 
with honeyhive_tracer.model(
    event_name="weather_function_call",
    input=input_dict,
    chat_template=messages,
    output_field=function_output_field
) as weather_function_call:
    openai_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=honeyhive.utils.fill_chat_template(messages, input_dict),
        tools=tools
    ).json()

# making sure messages persists the location info
messages = honeyhive.utils.fill_chat_template(messages, input_dict)

assistant_message = json.loads(openai_response)["choices"][0]["message"]

# drop the function_call field
del assistant_message["function_call"]
messages.append(assistant_message)

results = execute_function_call(assistant_message, honeyhive_tracer)
messages.append({"role": "tool", 
                 "tool_call_id": assistant_message["tool_calls"][0]['id'], 
                 "name": assistant_message["tool_calls"][0]["function"]["name"], 
                 "content": results})

# Second step in pipeline, passing in function response
with honeyhive_tracer.model(
    event_name="weather_chat",
    input={ "function_response": results },
    output_field=model_output_field
) as weather_function_call:
    openai_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages 
    ).json()

# log feedback for the session
session_id = honeyhive_tracer.session_id
honeyhive.sdk.feedback(
    session_id=session_id,
    feedback={
        "provided": True,
        "accepted": False,
        "edited": True
    }
)
