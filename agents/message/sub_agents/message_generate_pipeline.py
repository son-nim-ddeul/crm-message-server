# parrell agent -> loop agent 기반 메시지 생성
import logging
from typing import Literal, Optional
from collections.abc import AsyncGenerator

from google.adk.agents import BaseAgent, LlmAgent, LoopAgent, ParallelAgent, SequentialAgent
from agents.config import config
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from pydantic import BaseModel, Field

from agents.message.sub_agents.strategic_message_prompt import (
    get_message_generator_config,
    get_enhanced_message_generator_config
)


class MessageOutput(BaseModel):
    """Output schema for marketing messages."""
    
    title: str = Field(
        description="Message title, maximum 40 characters in Korean"
    )
    content: str = Field(
        description="Message content, maximum 350 characters in Korean"
    )
    tone_rationale: str = Field(
        description="Brief explanation of how this message implements the specific emotional tone strategy"
    )
    
class EnhancedMessageOutput(BaseModel):
    """Model for providing evaluation feedback on marketing message quality."""

    title: str = Field(
        description="Message title, maximum 40 characters in Korean"
    )
    content: str = Field(
        description="Message content, maximum 350 characters in Korean"
    )
    tone_rationale: str = Field(
        description="Brief explanation of how this message implements the specific emotional tone strategy"
    )
    revision_notes: str = Field(
        default=None,
        description="[Optional] 어떤 부분을 어떻게 개선했는지 간단히 설명"
    )

def get_message_generator(message_type:str) -> LlmAgent:
    description, instruction = get_message_generator_config(message_type=message_type)
    return LlmAgent(
        name="message_generator",
        model=config.write_model,
        description=description,
        instruction=instruction,
        output_schema=MessageOutput,
        output_key=f"{message_type}_message"
    )

class Feedback(BaseModel):
    """Model for providing evaluation feedback on marketing message quality."""

    grade: Literal["pass", "fail"] = Field(
        description="Evaluation result. 'pass' if the message meets all criteria, 'fail' if it needs revision."
    )
    comment: str = Field(
        description="Detailed explanation of the evaluation, highlighting which criteria were met or failed, and specific suggestions for improvement."
    )
    improvement_suggestions: Optional[List[str]] = Field(
        default=None,
        description="Specific actionable suggestions for improving the message (only provided when grade is 'fail')."
    )

def get_message_evaluator(message_type:str) -> LlmAgent:
    return LlmAgent(
        model=config.critic_model,
        name="marketing_message_evaluator",
        description="Evaluates marketing messages against brand guidelines and quality criteria.",
        instruction="""
        You are a marketing quality assurance specialist evaluating the generated marketing message.

        **EVALUATION CRITERIA:**
        Assess the marketing message against the following requirements:

        1. **Title Length Compliance**: Title must be 40 characters or less (한글 기준 40자 이내)
        2. **Content Length Compliance**: Content must be 350 characters or less (한글 기준 350자 이내)
        3. **Brand Tone Alignment**: Message effectively incorporates and reflects the specified brand tone
        - Brand Tone: {brand_tone}
        4. **Purpose Fulfillment**: Message clearly serves the intended communication purpose
        - Message Purpose: {message_purpose}
        5. **Persona Understanding**: Message demonstrates deep understanding of the target persona's characteristics, needs, pain points, and preferences
        - Refer to the detailed persona information provided in the context
        - Ensure language, tone, and content resonate with this specific audience
        6. **Customer-Friendly Language**: Uses natural, conversational language that is easy to understand and relatable

        **TARGET PERSONA:**
        {persona}

        **GRADING GUIDELINES:**
        - Grade "pass" ONLY if ALL 6 criteria are met satisfactorily
        - Grade "fail" if ANY criterion is not met or if multiple criteria need improvement
        - For "fail" grades, provide specific, actionable feedback on what needs to be fixed
        - Be constructive but maintain high quality standards

        **RESPONSE FORMAT:**
        In your comment, address each criterion systematically:
        - State which criteria passed (✓) and which failed (✗)
        - For failed criteria, explain specifically what's wrong and why
        - Provide concrete examples or suggestions for improvement
        
        If grading "fail", include 3-5 specific improvement suggestions in the improvement_suggestions field.

        Your response must be a single, raw JSON object validating against the 'Feedback' schema.
        """,
        output_schema=Feedback,
        disallow_transfer_to_parent=True,
        disallow_transfer_to_peers=True,
        output_key=f"{message_type}_evaluation",
    )

class EscalationChecker(BaseAgent):
    """Checks research evaluation and escalates to stop the loop if grade is 'pass'."""

    def __init__(self, name: str):
        super().__init__(name=name)

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        evaluation_result = ctx.session.state.get("message_evaluation")
        if evaluation_result and evaluation_result.get("grade") == "pass":
            logging.info(
                f"[{self.name}] Message evaluation passed. Escalating to stop loop."
            )
            yield Event(author=self.name, actions=EventActions(escalate=True))
        else:
            logging.info(
                f"[{self.name}] Message evaluation failed or not found. Loop will continue."
            )
            # Yielding an event without content or actions just lets the flow continue.
            yield Event(author=self.name)

def get_enhanced_message_generator(message_type:str) -> LlmAgent:
    """Creates an agent that improves messages based on evaluation feedback."""
    # TODO : message_type 기반 다른 프롬프트 조회
    description, instruction = get_enhanced_message_generator_config(message_type=message_type)
    return LlmAgent(
        model=config.writer_model,
        name="enhanced_message_generator",
        description=description,
        instruction=instruction,
        output_schema=EnhancedMessageOutput,
        output_key=f"{message_type}_message",  # 동일한 key로 덮어쓰기
    )

aspirational_dreamer_message = SequentialAgent(
    name="aspirational_dreamer_message",
    description="generate marketing message like aspirational dreamer",
    sub_agents=[
        get_message_generator(message_type="aspirational_dreamer"),
        LoopAgent(
            name="aspirational_dreamer_evaluate",
            description="",
            max_iterations=config.max_search_iterations,
            sub_agents=[
                get_message_evaluator(message_type="aspirational_dreamer"),
                EscalationChecker(name="escalation_checker"),
                get_enhanced_message_generator(message_type="aspirational_dreamer"),
            ],
        )
    ]
)

empathetic_supporter_message = SequentialAgent(
    name="empathetic_supporter_message",
    description="generate marketing message like empathetic supporter",
    sub_agents=[
        get_message_generator(message_type="empathetic_supporter"),
        LoopAgent(
            name="empathetic_supporter_evaluate",
            description="",
            max_iterations=config.max_search_iterations,
            sub_agents=[
                get_message_evaluator(message_type="empathetic_supporter"),
                EscalationChecker(name="escalation_checker"),
                get_enhanced_message_generator(message_type="empathetic_supporter"),
            ],
        )
    ]
)

playful_entertainer_message = SequentialAgent(
    name="playful_entertainer_message",
    description="generate marketing message like playful entertainer",
    sub_agents=[
        get_message_generator(message_type="playful_entertainer"),
        LoopAgent(
            name="playful_entertainer_evaluate",
            description="",
            max_iterations=config.max_search_iterations,
            sub_agents=[
                get_message_evaluator(message_type="playful_entertainer"),
                EscalationChecker(name="escalation_checker"),
                get_enhanced_message_generator(message_type="playful_entertainer"),
            ],
        )
    ]
)

rational_advisor_message = SequentialAgent(
    name="rational_advisor_message",
    description="generate marketing message like rational advisor",
    sub_agents=[
        get_message_generator(message_type="rational_advisor"),
        LoopAgent(
            name="rational_advisor_evaluate",
            description="",
            max_iterations=config.max_search_iterations,
            sub_agents=[
                get_message_evaluator(message_type="rational_advisor"),
                EscalationChecker(name="escalation_checker"),
                get_enhanced_message_generator(message_type="rational_advisor"),
            ],
        )
    ]
)

message_generate_pipeline = ParallelAgent(
    name="message_generate_pipeline",
    description="",
    sub_agents=[
        aspirational_dreamer_message,
        empathetic_supporter_message,
        playful_entertainer_message,
        rational_advisor_message
    ]
)