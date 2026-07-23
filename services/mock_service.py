import hashlib


def generate_mock(
    prompt: str,
    seed: int,
    count: int,
) -> dict:
    digest = hashlib.sha256(f"{prompt}:{seed}".encode()).hexdigest()[:10]

    return {
        "status": "mock_generation_complete",
        "backend": f"mock:{digest}",
        "images": [],
        "count": count,
    }
