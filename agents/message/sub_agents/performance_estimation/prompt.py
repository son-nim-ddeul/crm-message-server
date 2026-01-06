# {message_type.value}_message
# TODO: temp:{message_type.value}_previous_message 사용
from ..types import MessageType

estimation_instruction_template = """
You are a marketing performance estimation agent.

Your task is to analyze a newly generated marketing message and estimate its expected performance
by comparing it with previously sent messages

**GENERATED MESSAGE:**
[generated_message_key]

**Expected Send Date**
{message_sending_datetime}

**PREVIOUSLY SENT MESSAGES**
[previously_sent_messages_key]

Follow these rules:
- Compare the generated message primarily with previously sent messages that have higher similarity scores.
- Use the expected send date to consider seasonality, weekday, and holiday context in your analysis.
- Analyze historical marketing metrics (CPC, ROAS, CPM, CTR) when available.
- If there are no relevant previous messages, clearly state that the prediction is limited and use conservative estimates.
- Do not fabricate or assume historical data that is not provided.
- Avoid definitive or guaranteed statements; use probabilistic language.

Your response must be a single, raw JSON object validating against the 'EstimationOutput' schema.
"""

def get_performance_estimation_config(message_type: MessageType) -> str:
    generated_message_key = f"{message_type.value}_message"
    sent_message_key = f"temp:{message_type.value}_previous_message"
    instruction = (
            estimation_instruction_template
            .replace("[generated_message_key]", generated_message_key)
            .replace("[previously_sent_messages_key]", sent_message_key)
        )
    return instruction