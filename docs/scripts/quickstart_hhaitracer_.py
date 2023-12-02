!pip install -U honeyhive
import os
from honeyhive.utils.tracer import HoneyHiveTracer

os.environ["HONEYHIVE_API_KEY"] = "YOUR_HONEYHIVE_API_KEY"

tracer = HoneyHiveTracer(
    project="Sandbox - Email Writer",  # necessary field: specify which project within HoneyHive
    name="Paul Graham Q&A",            # optional field: name of the chain/agent you are running
    source="testing",                  # optional field: source (to separate production & testing in monitoring)
    user_properties={                  # optional field: specify user properties for whom this was ran
        "user_id": "1234",
        "user_country": "US"
    }
)
with tracer.model(
    event_name="Email Writer",
    description="Generate an email response based on context provided",
    config={
        "model": "gpt-3.5-turbo",
        "chat_template": YOUR_TEMPLATE_HERE
    }
) as model_call:
    openai_response = openai.ChatCompletion.create(...)
with tracer.tool(
    event_name="Context Provider",
    description="Get context for the email response",
    config={
        "index": "quickstart",
        "provider": "pinecone",
        "chunk_size": 512
    }
) as pinecone_call:
    pinecone_response = pinecone.query(...)
honeyhive.sessions.feedback(
    session_id = tracer.session_id,
    feedback = {
       "accepted": True,
       "edited": False
    }
)
honeyhive.sessions.feedback(
    session_id = tracer.session_id,
    event_id = model_call.event_id,
    ground_truth = "INSERT_GROUND_TRUTH_LABEL",
    feedback = {
       "accepted": False
    }
)
tracer.end_session()
