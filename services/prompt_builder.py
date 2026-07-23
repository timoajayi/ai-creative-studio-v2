from __future__ import annotations


def build_prompt(
    product_description: str,
    style: str,
    background: str,
    lighting: str,
    camera_angle: str,
    aspect_ratio: str,
    extra_details: str = "",
) -> tuple[str, str]:
    """Create a structured production prompt and negative prompt."""

    product = product_description.strip()
    if not product:
        raise ValueError("Product description cannot be empty.")

    components = [
        f"Professional {style} image of {product}",
        camera_angle,
        background,
        lighting,
        "high detail",
        "realistic materials and textures",
        "clear product focus",
        "commercial-quality composition",
        f"aspect ratio {aspect_ratio}",
    ]

    if extra_details.strip():
        components.append(extra_details.strip())

    prompt = ", ".join(components) + "."

    negative_prompt = (
        "low resolution, blurry, distorted product, incorrect proportions, "
        "duplicate objects, extra parts, text, watermark, logo artifacts, "
        "poor lighting, cluttered composition, oversaturated colors"
    )

    return prompt, negative_prompt
