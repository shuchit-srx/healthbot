from app.core.logging import get_logger
from app.graph.state import HealthBotState
from app.graph.workflow import healthbot_workflow
from app.utils.state_helpers import validate_state


logger = get_logger(__name__)


class HealthBotWorkflowService:
    """Service layer for executing the HealthBot workflow."""

    def __init__(self):
        self.workflow = healthbot_workflow

    def run(
        self,
        state: HealthBotState,
    ) -> HealthBotState:
        """Execute the complete HealthBot workflow."""

        if not validate_state(state):
            raise ValueError(
                "Invalid HealthBot workflow state."
            )

        try:
            logger.info(
                "Starting HealthBot workflow."
            )

            result = self.workflow.invoke(state)

            if not isinstance(result, dict):
                raise RuntimeError(
                    "Workflow returned an invalid state."
                )

            if not validate_state(result):
                raise RuntimeError(
                    "Workflow returned an invalid state structure."
                )

            logger.info(
                "HealthBot workflow completed."
            )

            return result

        except Exception as exc:
            logger.exception(
                "HealthBot workflow execution failed."
            )

            return {
                **state,
                "error": f"Workflow execution failed: {exc}",
            }


workflow_service = HealthBotWorkflowService()