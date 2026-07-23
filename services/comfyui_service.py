from __future__ import annotations
import copy, json, os, time, uuid
from pathlib import Path
from typing import Any
import requests

from dotenv import load_dotenv

load_dotenv()

COMFYUI_URL = os.getenv("COMFYUI_URL", "http://127.0.0.1:8188")
WORKFLOW_PATH = Path(
    os.getenv("COMFYUI_WORKFLOW_PATH", "workflows/marketing_image_workflow_api.json")
)

LORA_NODE_ID = "72"
LORA_MAP = {
    "Realistic Snapshot": "RealisticSnapshotKrea2.safetensors",
    "35mm Photo": "Z-TURBO_Photography_35mmPhoto_1536.safetensors",
    "Aesthetic": "aesthetic_exp1.safetensors",
}


class ComfyUIError(RuntimeError):
    pass


def _load_workflow() -> dict[str, Any]:
    if not WORKFLOW_PATH.exists():
        raise ComfyUIError(f"Workflow not found at {WORKFLOW_PATH}.")
    return json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))


def _replace(v: Any, r: dict[str, Any]) -> Any:
    if isinstance(v, dict):
        return {k: _replace(x, r) for k, x in v.items()}
    if isinstance(v, list):
        return [_replace(x, r) for x in v]
    if isinstance(v, str) and v in r:
        return r[v]
    return v


def queue_generation(
    prompt: str,
    negative_prompt: str,
    seed: int,
    steps: int,
    cfg: float,
    width: int,
    height: int,
    batch_size: int,
    model: str = "Z Image Turbo",
    lora: str = "None",
    lora_strength: float = 0.8,
) -> str:
    wf = copy.deepcopy(_load_workflow())

    if lora == "None":
        wf[LORA_NODE_ID]["inputs"]["strength_model"] = 0.0
        wf[LORA_NODE_ID]["inputs"]["strength_clip"] = 0.0
    else:
        if lora not in LORA_MAP:
            raise ComfyUIError(f"Unsupported LoRA: {lora}")
        wf[LORA_NODE_ID]["inputs"]["lora_name"] = LORA_MAP[lora]
        wf[LORA_NODE_ID]["inputs"]["strength_model"] = lora_strength
        wf[LORA_NODE_ID]["inputs"]["strength_clip"] = lora_strength

    # Update the exact nodes from your exported ComfyUI workflow.
    wf["67"]["inputs"]["text"] = prompt
    wf["71"]["inputs"]["text"] = negative_prompt

    wf["70"]["inputs"]["seed"] = seed
    wf["70"]["inputs"]["steps"] = steps
    wf["70"]["inputs"]["cfg"] = cfg

    wf["68"]["inputs"]["width"] = width
    wf["68"]["inputs"]["height"] = height
    wf["68"]["inputs"]["batch_size"] = batch_size

    payload = {
        "prompt": wf,
        "client_id": str(uuid.uuid4()),
    }

    res = requests.post(
        f"{COMFYUI_URL}/prompt",
        json=payload,
        timeout=30,
    )

    if not res.ok:
        raise ComfyUIError(
            f"ComfyUI rejected the workflow: {res.status_code} {res.text}"
        )
    # if not res.ok:
    #     raise ComfyUIError(
    #         f"ComfyUI rejected the workflow: "
    #         f"{res.status_code} {res.text}"
    #     )

    prompt_id = res.json().get("prompt_id")

    if not prompt_id:
        raise ComfyUIError(f"ComfyUI did not return a prompt_id. Response: {res.text}")

    return prompt_id


def wait_for_images(prompt_id: str, timeout_seconds: int = 2200) -> list[str]:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        res = requests.get(f"{COMFYUI_URL}/history/{prompt_id}", timeout=30)
        if not res.ok:
            raise ComfyUIError(
                f"Could not retrieve ComfyUI history: {res.status_code} {res.text}"
            )

        hist = res.json()
        if prompt_id in hist:
            urls = []
            for output in hist[prompt_id].get("outputs", {}).values():
                for image in output.get("images", []):
                    urls.append(
                        f"{COMFYUI_URL}/view?filename={image['filename']}&subfolder={image.get('subfolder', '')}&type={image.get('type', 'output')}"
                    )
            if urls:
                return urls
        time.sleep(2)
    raise ComfyUIError("Timed out while waiting for ComfyUI generation.")
