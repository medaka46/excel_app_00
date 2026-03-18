# uvicorn main:app --reload --port 8010
PORT="${PORT:-8010}"
cd "$(dirname "$0")/api"
exec uvicorn main:app --host 0.0.0.0 --port "$PORT"
