class HealthBotError(Exception):
    """Base exception for HealthBot."""


class ConfigurationError(HealthBotError):
    """Raised when application configuration is invalid."""


class ValidationError(HealthBotError):
    """Raised when user input fails validation."""


class ExternalServiceError(HealthBotError):
    """Raised when an external service fails."""


class WorkflowError(HealthBotError):
    """Raised when the HealthBot workflow fails."""