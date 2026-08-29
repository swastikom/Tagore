import os
import re
import time
import warnings
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

warnings.filterwarnings("ignore", category=UserWarning)
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# --- LangSmith / LangGraph tracing (optional) ---
os.environ.setdefault("LANGCHAIN_PROJECT", os.getenv("LANGCHAIN_PROJECT", "novel-gen-pipeline"))
_tracing_enabled = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
if _tracing_enabled:
    print(f"🔍 LangSmith tracing ENABLED — project: '{os.environ['LANGCHAIN_PROJECT']}'")
else:
    print("🔍 LangSmith tracing disabled (set LANGCHAIN_TRACING_V2=true in .env to enable)")

GEMINI_HEAVY_MODEL = "gemini-3.5-flash"       # Prose drafting (Adjust to 2.5/3.5 depending on your API access)
GEMINI_LIGHT_MODEL = "gemini-3.5-flash-lite"    # Logic & Validation
LLM_MAX_RETRIES = 6
MAX_RETRIES = 3

def get_llm(heavy: bool = False):
    model_name = GEMINI_HEAVY_MODEL if heavy else GEMINI_LIGHT_MODEL
    temp = 0.85 if heavy else 0.2
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=GOOGLE_API_KEY,
        max_retries=LLM_MAX_RETRIES,
        temperature=temp
    )

def safe_invoke(llm, prompt, max_attempts=5):
    for attempt in range(max_attempts):
        try:
            return llm.invoke(prompt)
        except Exception as e:
            err_str = str(e)
            is_rate_limit = "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "RateLimit" in type(e).__name__
            is_server_busy = "503" in err_str or "UNAVAILABLE" in err_str or "high demand" in err_str
            # NEW: catch transient connection-level failures (e.g. "Server
            # disconnected without sending a response") — these are just as
            # retryable as 429/503, but previously fell straight into the
            # `raise e` branch below and got zero retry attempts.
            is_connection_error = (
                "Server disconnected" in err_str
                or "Connection reset" in err_str
                or "ConnectionError" in type(e).__name__
                or "RemoteProtocolError" in type(e).__name__
            )

            if is_rate_limit or is_server_busy or is_connection_error:
                match = re.search(r"retry in (\d+(\.\d+)?)s", err_str, re.IGNORECASE)
                if match:
                    wait_time = int(float(match.group(1))) + 2
                elif is_connection_error:
                    wait_time = 5 * (attempt + 1)  # shorter backoff — network blips usually clear fast
                else:
                    wait_time = 15 * (attempt + 1)

                if is_server_busy:
                    reason = "Google Server Overload (503)"
                elif is_rate_limit:
                    reason = "Rate Limit (429)"
                else:
                    reason = "Connection Dropped"
                print(f"\n⚠️ {reason} hit. Pausing... retrying in {wait_time}s (Attempt {attempt+1}/{max_attempts})...")
                time.sleep(wait_time)
            else:
                raise e
    return llm.invoke(prompt)