import os, threading, json, re
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from ibm_watsonx_ai import Credentials, APIClient
from ibm_watsonx_ai.foundation_models.inference import ModelInference

load_dotenv()

_WATSONX_URL = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
_WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")
_WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
_DEFAULT_MODEL_ID = os.getenv("WATSONX_MODEL_ID", "ibm/granite-13b-instruct")

_lock = threading.Lock()
_client: Optional[APIClient] = None
_infers: Dict[str, ModelInference] = {}
_JSON_BLOCK = re.compile(r"\{.*\}", re.DOTALL)

def _require_env():
    if not _WATSONX_API_KEY:
        raise RuntimeError("Missing WATSONX_API_KEY in environment/.env")
    if not _WATSONX_PROJECT_ID:
        raise RuntimeError("Missing WATSONX_PROJECT_ID in environment/.env")

def _get_client() -> APIClient:
    """Singleton APIClient with project set."""
    global _client
    _require_env()
    if _client is None:
        with _lock:
            if _client is None:
                creds = Credentials(url=_WATSONX_URL, api_key=_WATSONX_API_KEY)
                c = APIClient(creds)
                c.set.default_project(_WATSONX_PROJECT_ID)
                _client = c
    return _client

def get_infer(model_id: Optional[str] = None, **params) -> ModelInference:
    """Return a cached ModelInference bound to the shared client."""
    mid = model_id or _DEFAULT_MODEL_ID
    # sensible defaults
    params = dict(params)
    params.setdefault("max_new_tokens", 200)
    params.setdefault("decoding_method", "greedy")

    key = f"{mid}:{json.dumps(params, sort_keys=True)}"
    infer = _infers.get(key)
    if infer is None:
        with _lock:
            infer = _infers.get(key)
            if infer is None:
                infer = ModelInference(model_id=mid, params=params, client=_get_client())
                _infers[key] = infer
    return infer

def generate_text(prompt: str, **params) -> str:
    """Simple helper for text generations."""
    return get_infer(**params).generate_text(prompt)

def generate_json(prompt: str, **params) -> Dict[str, Any]:
    """Try to coerce model output to JSON by extracting the first {...} block."""
    raw = generate_text(prompt, **params).strip()
    try:
        return json.loads(raw)
    except Exception:
        m = _JSON_BLOCK.search(raw)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
    return {"error": "json_parse_failed", "raw": raw[:240]}

def health_check() -> bool:
    """Lightweight check that auth & project are good and a model can be built."""
    try:
        _ = get_infer()
        return True
    except Exception:
        return False