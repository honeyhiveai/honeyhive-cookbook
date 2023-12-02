!pip install honeyhive -q
import honeyhive
from honeyhive.sdk.utils import fill_template
from transformers import AutoTokenizer # & appropriate model imports
import time

honeyhive.api_key = "HONEYHIVE_API_KEY"

hf_model_path = "dummy/model"

tokenizer = AutoTokenizer.from_pretrained(hf_model_path)
# using the huggingface model import
# model = 

USER_TEMPLATE = f"{HUMAN_PROMPT} Write me an email on {{topic}} in a {{tone}} tone.{AI_PROMPT}"
user_inputs = {
    "topic": "AI Services",
    "tone": "Friendly"
}
#"Write an email on AI Services in a Friendly tone."
user_message = fill_template(USER_TEMPLATE, user_inputs)

start = time.perf_counter()

# tokenize the inputs
# model_inputs = tokenizer(user_message)

# generate model completion
# generated_ids = model.generate(**model_inputs)

# decode the tokens
# decoded_output = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

end = time.perf_counter()

request_latency = (end - start)*1000
generation = decoded_output
token_usage = {
    "completion_tokens": len(generated_ids),
    "prompt_tokens": len(model_inputs),
    "total_tokens": len(generated_ids) + len(model_inputs)
}

gpu_cost_per_ms = 0.0000006
response = honeyhive.generations.log(
    project="Sandbox - Email Writer",
    source="staging",
    model=model_path,
    hyperparameters={
        # any additional arguments used when generating model completion
    },
    prompt_template=USER_TEMPLATE,
    inputs=user_inputs,
    generation=generation,
    metadata={
        "session_id": session_id  # Optionally specify a session id to track related completions
    },
    usage=token_usage,
    latency=request_latency,
    cost=request_latency * gpu_cost_per_ms,
    user_properties={
        "user_device": "Macbook Pro",
        "user_Id": "92739527492",
        "user_country": "United States",
        "user_subscriptiontier": "Enterprise",
        "user_tenantID": "Acme Inc."
    }
)
from honeyhive.sdk.feedback import generation_feedback
generation_feedback(
    project="Sandbox - Email Writer",
    generation_id=response.generation_id,
    ground_truth="INSERT_GROUND_TRUTH_LABEL",
    feedback_json={
        "provided": True,
        "accepted": False,
        "edited": True
    }
)
import honeyhive

honeyhive.api_key = "HONEYHIVE_API_KEY"
honeyhive.openai_api_key = "OPENAI_API_KEY"

response = honeyhive.generations.generate(
    project="Sandbox - Email Writer",
    source="staging",
    input={
        "topic": "Model evaluation for companies using GPT-4",
        "tone": "friendly"
    },
)
