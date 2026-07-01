from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "MomentumLens"
    debug: bool = False

    database_url: str = "sqlite:///./momentumlens.db"

    ibm_watsonx_url: str = ""
    ibm_watsonx_apikey: str = ""
    ibm_watsonx_project_id: str = ""
    granite_model_id: str = "ibm/granite-13b-chat-v2"

    momentum_window: int = 5
    turning_point_threshold: float = 0.3

    class Config:
        env_file = ".env"


settings = Settings()
