from google.adk.plugins.base_plugin import BasePlugin
from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from typing import Optional, Any
from google.genai import types
from ..sub_agents.types import MessageType


_ui_status_cache = {
    "main_message_generator": {
        "type": False,
        "before": "Initiating message generation and marketing performance prediction process",
        "after": "Completing message generation and marketing performance prediction process"
    },
    "message_generate_pipeline": {
        "type": False,
        "before": "Launching parallel message generation pipeline",
        "after": "Finalizing parallel message generation pipeline"
    },
    "aspirational_dreamer_message": {
        "type": False,
        "before": "Initiating aspirational dreamer message generation process",
        "after": "Completing aspirational dreamer message generation process"
    },
    "empathetic_supporter_message": {
        "type": False,
        "before": "Initiating empathetic supporter message message generation process",
        "after": "Completing empathetic supporter message message generation process"
    },
    "playful_entertainer_message": {
        "type": False,
        "before": "Initiating playful entertainer message message generation process",
        "after": "Completing playful entertainer message message generation process"
    },
    "rational_advisor_message": {
        "type": False,
        "before": "Initiating rational advisor message message generation process",
        "after": "Completing rational advisor message message generation process"
    },
    "message_generator": {
        "type": True,
        "before": "Generating initial message draft",
        "after": "Message draft generation complete"
    },
    "marketing_message_evaluator": {
        "type": True,
        "before": "Commencing generated message evaluation",
        "after": "Generated message evaluation complete"
    },
    "escalation_checker": {
        "type": True,
        "before": "Reviewing evaluation findings",
        "after": "Evaluation review complete"
    },
    "enhanced_message_generator": {
        "type": True,
        "before": "Enhancing message content",
        "after": "Message enhancement complete"
    },
    "performance_estimation_agent": {
        "type": False,
        "before": "Estimating marketing performance across strategies",
        "after": "Marketing performance estimation complete"
    },
    "aspirational_dreamer_estimation_agent": {
        "type": False,
        "before": "(Strategy : aspirational dreamer) Predicting marketing performance based on historical data",
        "after": "(Strategy : aspirational dreamer) Performance prediction complete"
    },
    "empathetic_supporter_estimation_agent": {
        "type": False,
        "before": "(Strategy : empathetic supporter) Predicting marketing performance based on historical data",
        "after": "(Strategy : empathetic supporter) Performance prediction complete"
    },
    "playful_entertainer_estimation_agent": {
        "type": False,
        "before": "(Strategy : playful entertainer) Predicting marketing performance based on historical data",
        "after": "(Strategy : playful entertainer) Performance prediction complete"
    },
    "rational_advisor_estimation_agent": {
        "type": False,
        "before": "(Strategy : rational advisor) Predicting marketing performance based on historical data",
        "after": "(Strategy : rational advisor) Performance prediction complete"
    },
    "report_agent": {
        "type": False,
        "before": "write report about marketing performance estimation",
        "after": "write report complete"
    }
}

def __format_strategy_prefix(branch: str) -> Optional[str]:
    for message_type in MessageType:
        if message_type.value in branch:
            strategy_name = message_type.value.replace('_', ' ').title()
            return f"(Strategy: {strategy_name})"
    return None

def __get_ui_status(
    agent_name: str,
    execution_point: str,
    branch: Optional[str]
) -> Optional[str]:
    ui_status : dict[str, Any] = _ui_status_cache.get(agent_name)
    if not ui_status:
        return None
    
    if ui_status.get("type") == False:
        return ui_status.get(execution_point)
    
    if not branch:
        return None
    
    prefix = __format_strategy_prefix(branch=branch)
    if not prefix:
        return None
    
    ui_status = ui_status.get(execution_point)
    return f"{prefix} {ui_status}"

class StautsLoggingPlugin(BasePlugin):
        
  def __init__(self, name: str = "status_logging_plugin"):
    super().__init__(name)
    
  async def before_agent_callback(
      self, *, agent: BaseAgent, callback_context: CallbackContext
  ) -> Optional[types.Content]:
      ui_status = __get_ui_status(
          agent_name=agent.name,
          execution_point="before",
          branch=callback_context._invocation_context.branch
      )
      if not ui_status:
          return None
      callback_context.state['ui_status'] = ui_status
      return None
  
  async def after_agent_callback(
      self, *, agent: BaseAgent, callback_context: CallbackContext
  ) -> Optional[types.Content]:
    ui_status = __get_ui_status(
        agent_name=agent.name,
        execution_point="after",
        branch=callback_context._invocation_context.branch
    )
    if not ui_status:
          return None
    callback_context.state['ui_status'] = ui_status
    return None