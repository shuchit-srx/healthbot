from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "HealthBot"
    app_version: str = "1.0.0"
    debug: bool = True

    gemini_api_key_1: str = ""
    gemini_api_key_2: str = ""
    gemini_api_key_3: str = ""
    gemini_api_key_4: str = ""
    gemini_api_key_5: str = ""

    tavily_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file="config.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def gemini_api_keys(self) -> list[str]:
        return [
            key
            for key in [
                self.gemini_api_key_1,
                self.gemini_api_key_2,
                self.gemini_api_key_3,
                self.gemini_api_key_4,
                self.gemini_api_key_5,
            ]
            if key
        ]


settings = Settings()