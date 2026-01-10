from google.adk.agents import LoopAgent, SequentialAgent

from agents.config import config

from ..types import MessageType

from .sub_agents.generator.agent import get_message_generator, get_enhanced_message_generator
from .sub_agents.evaluator.agent import get_message_evaluator
from .sub_agents.checker.agent import EscalationChecker


def create_tone_pipeline(message_type: MessageType, description: str) -> SequentialAgent:
    """Creates a sequential pipeline for a specific message tone."""
    return SequentialAgent(
        name=f"{message_type.value}_message",
        description=description,
        sub_agents=[
            get_message_generator(message_type=message_type),
            LoopAgent(
                name=f"{message_type.value}_evaluate",
                description=description,
                max_iterations=config.max_search_iterations,
                sub_agents=[
                    get_message_evaluator(message_type=message_type),
                    EscalationChecker(name="escalation_checker", message_type=message_type),
                    get_enhanced_message_generator(message_type=message_type),
                ],
            )
        ]
    )

aspirational_dreamer_message = create_tone_pipeline(
    message_type=MessageType.ASPIRATIONAL_DREAMER,
    description="generate marketing message like aspirational dreamer"
)

empathetic_supporter_message = create_tone_pipeline(
    message_type=MessageType.EMPATHETIC_SUPPORTER,
    description="generate marketing message like empathetic supporter"
)

playful_entertainer_message = create_tone_pipeline(
    message_type=MessageType.PLAYFUL_ENTERTAINER,
    description="generate marketing message like playful entertainer"
)

rational_advisor_message = create_tone_pipeline(
    message_type=MessageType.RATIONAL_ADVISOR,
    description="generate marketing message like rational advisor"
)
