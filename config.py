from dotenv import load_dotenv

load_dotenv()

MAX_DOC_LEN = 5000
CHUNK_SIZE = 2000
CHUNK_OVERLAP = 400
TOKEN_LIMIT = 4000
USE_TOOL_ENGINE = True

OPENAI_API_KEY="key"
QDRANT_URL="https://xxx.europe-west3-0.gcp.cloud.qdrant.io:6333/"
QDRANT_API_KEY=""
