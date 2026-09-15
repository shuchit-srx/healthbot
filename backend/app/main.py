from app.graph.workflow import healthbot_app
from app.utils.state_helpers import reset_state


def run_healthbot():
    """Run the HealthBot application."""

    initial_state = reset_state()

    return healthbot_app.invoke(initial_state)


if __name__ == "__main__":
    run_healthbot()