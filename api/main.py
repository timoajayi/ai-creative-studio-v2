import os
import time
from typing import Literal

import requests

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from services.comfyui_service import (
    ComfyUIError,
    queue_generation,
    wait_for_images,
)
from services.history_service import (
    init_db,
    list_generations,
    save_generation,
)
from services.mock_service import generate_mock
from services.prompt_builder import build_prompt

load_dotenv()
app = FastAPI(
    title="AI Creative Studio API",
    version="0.2.0",
)


@app.on_event("startup")
def startup() -> None:
    init_db()


class GenerationRequest(BaseModel):
    product_description: str = Field(
        min_length=3,
        max_length=500,
    )

    model: Literal["Z Image Turbo",] = "Z Image Turbo"

    lora: Literal[
        "None",
        "Realistic Snapshot",
        "35mm Photo",
        "Aesthetic",
    ] = "None"

    lora_strength: float = Field(
        default=0.8,
        ge=0.0,
        le=1.2,
    )

    style: str = "Commercial e-commerce"
    background: str = "Clean white studio background"
    lighting: str = "Soft diffused studio lighting"
    camera_angle: str = "Three-quarter product view"
    aspect_ratio: str = "1:1"
    extra_details: str = ""

    seed: int = Field(
        default=42,
        ge=0,
    )

    steps: int = Field(
        default=8,
        ge=1,
        le=100,
    )

    cfg: float = Field(
        default=1.0,
        ge=1.0,
        le=20.0,
    )

    width: int = Field(
        default=1024,
        ge=256,
        le=2048,
    )

    height: int = Field(
        default=1024,
        ge=256,
        le=2048,
    )

    image_count: int = Field(
        default=1,
        ge=1,
        le=4,
    )

    custom_prompt: str | None = Field(
        default=None,
        max_length=2000,
    )


@app.get("/health")
def health() -> dict:
    return {
        "status": "healthy",
        "backend": os.getenv("IMAGE_BACKEND", "mock"),
    }


@app.get("/history")
def history(limit: int = 30):
    limit = min(max(limit, 1), 100)
    return list_generations(limit)


@app.post("/enhance-prompt")
def enhance_prompt(r: GenerationRequest):
    try:
        prompt, negative = build_prompt(
            r.product_description,
            r.style,
            r.background,
            r.lighting,
            r.camera_angle,
            r.aspect_ratio,
            r.extra_details,
        )

        return {
            "product_description": r.product_description,
            "enhanced_prompt": prompt,
            "negative_prompt": negative,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Prompt enhancement failed: {error}",
        ) from error


@app.post("/generate")
def generate(r: GenerationRequest):
    start_time = time.perf_counter()

    try:
        built_prompt, negative = build_prompt(
            r.product_description,
            r.style,
            r.background,
            r.lighting,
            r.camera_angle,
            r.aspect_ratio,
            r.extra_details,
        )

        prompt = (
            r.custom_prompt.strip()
            if r.custom_prompt and r.custom_prompt.strip()
            else built_prompt
        )

        image_backend = os.getenv(
            "IMAGE_BACKEND",
            "mock",
        ).lower()

        if image_backend == "comfyui":
            prompt_id = queue_generation(
                prompt=prompt,
                negative_prompt=negative,
                seed=r.seed,
                steps=r.steps,
                cfg=r.cfg,
                width=r.width,
                height=r.height,
                batch_size=r.image_count,
                model=r.model,
                lora=r.lora,
                lora_strength=r.lora_strength,
            )

            images = wait_for_images(prompt_id)
            status = "generation_complete"
            backend = "comfyui"

        elif image_backend == "mock":
            result = generate_mock(
                prompt,
                r.seed,
                r.image_count,
            )

            images = result["images"]
            status = result["status"]
            backend = result["backend"]

        else:
            raise ValueError(
                f"Unsupported IMAGE_BACKEND: {image_backend}. "
                f"Supported backends are: comfyui, mock."
            )

        generation_time = time.perf_counter() - start_time

        record = {
            "product_description": r.product_description,
            "model": r.model,
            "lora": r.lora,
            "lora_strength": r.lora_strength,
            "style": r.style,
            "background": r.background,
            "lighting": r.lighting,
            "camera_angle": r.camera_angle,
            "aspect_ratio": r.aspect_ratio,
            "extra_details": r.extra_details,
            "prompt": prompt,
            "negative_prompt": negative,
            "seed": r.seed,
            "steps": r.steps,
            "cfg": r.cfg,
            "width": r.width,
            "height": r.height,
            "image_count": r.image_count,
            "generation_time": round(generation_time, 3),
            "backend": backend,
            "status": status,
            "images": images,
        }

        generation_id = save_generation(record)

        return {
            **record,
            "id": generation_id,
        }

    except (ComfyUIError, OSError, ValueError) as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error

    except requests.RequestException as error:
        raise HTTPException(
            status_code=502,
            detail=f"Image backend request failed: {error}",
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected server error: {error}",
        ) from error
