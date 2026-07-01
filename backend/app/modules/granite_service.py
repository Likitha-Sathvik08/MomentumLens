from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from app.core.config import settings


class GraniteUnavailableError(Exception):
    """Raised when IBM Granite / WatsonX is not configured or reachable."""
    pass


def _check_credentials():
    """Validate that WatsonX credentials are configured."""
    if not settings.ibm_watsonx_url or not settings.ibm_watsonx_apikey or not settings.ibm_watsonx_project_id:
        raise GraniteUnavailableError(
            "IBM WatsonX credentials are not configured. "
            "Please set IBM_WATSONX_URL, IBM_WATSONX_APIKEY, and IBM_WATSONX_PROJECT_ID in your .env file."
        )


def _get_model() -> ModelInference:
    _check_credentials()
    try:
        credentials = Credentials(
            url=settings.ibm_watsonx_url,
            api_key=settings.ibm_watsonx_apikey,
        )
        client = APIClient(credentials)
        return ModelInference(
            model_id=settings.granite_model_id,
            api_client=client,
            project_id=settings.ibm_watsonx_project_id,
            params={
                GenParams.MAX_NEW_TOKENS: 512,
                GenParams.TEMPERATURE: 0.7,
                GenParams.TOP_P: 0.9,
            },
        )
    except Exception as e:
        raise GraniteUnavailableError(f"Failed to connect to IBM WatsonX: {str(e)}")


EXPLANATION_SYSTEM = (
    "You are a soccer tactical analyst. Given match context and turning point data, "
    "write a clear, engaging 2-3 paragraph explanation of why momentum shifted. "
    "Be specific about events and tactical reasons. Avoid jargon overload."
)

CHAT_SYSTEM = (
    "You are MomentumLens, an AI soccer analyst. Answer follow-up questions about "
    "match momentum and tactics based on the provided match context. Be concise and insightful."
)


def generate_explanation(context: str) -> str:
    model = _get_model()
    prompt = f"{EXPLANATION_SYSTEM}\n\nContext:\n{context}\n\nExplanation:"
    result = model.generate_text(prompt=prompt)
    return result.strip()


def chat(message: str, match_context: str, history: list[dict]) -> str:
    model = _get_model()
    history_text = ""
    for turn in history[-6:]:  # keep last 3 exchanges
        role = turn.get("role", "user")
        content = turn.get("content", "")
        history_text += f"{role.capitalize()}: {content}\n"

    prompt = (
        f"{CHAT_SYSTEM}\n\nMatch Context:\n{match_context}\n\n"
        f"{history_text}User: {message}\nAssistant:"
    )
    result = model.generate_text(prompt=prompt)
    return result.strip()
