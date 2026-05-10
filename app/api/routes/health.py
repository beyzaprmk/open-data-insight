def health_check() -> dict:
    # Basic liveness probe response.
    return {"status": "ok"}
