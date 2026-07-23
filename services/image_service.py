from __future__ import annotations

import hashlib


def generate_mock_result(prompt: str, aspect_ratio: str) -> dict[str, str | None]:
    """
    Return a deterministic mock response.

    This keeps the MVP fully runnable without a GPU or paid API.
    Replace this service with a ComfyUI client in the next phase.
    """
    prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:10]

    return {
        "status": "mock_generation_complete",
        "image_url": None,
        "backend": f"mock:{aspect_ratio}:{prompt_hash}",
    }
