from services.prompt_builder import build_prompt


def test_build_prompt_contains_product_description():
    prompt, negative_prompt = build_prompt(
        product_description="Premium black wireless headphones",
        style="commercial e-commerce",
        background="clean studio background",
        lighting="soft diffused lighting",
        camera_angle="three-quarter product view",
        aspect_ratio="1:1",
        extra_details="realistic reflections",
    )

    assert "Premium black wireless headphones" in prompt
    assert isinstance(negative_prompt, str)
    assert len(negative_prompt) > 0


def test_build_prompt_contains_selected_settings():
    prompt, _ = build_prompt(
        product_description="Modern smartwatch",
        style="luxury advertising",
        background="dark studio background",
        lighting="cinematic lighting",
        camera_angle="close-up view",
        aspect_ratio="16:9",
        extra_details="highly detailed materials",
    )

    assert "luxury advertising" in prompt
    assert "dark studio background" in prompt
    assert "cinematic lighting" in prompt
    assert "close-up view" in prompt


def test_build_prompt_handles_empty_extra_details():
    prompt, negative_prompt = build_prompt(
        product_description="Minimalist ceramic coffee mug",
        style="lifestyle photography",
        background="kitchen background",
        lighting="natural window lighting",
        camera_angle="front view",
        aspect_ratio="1:1",
        extra_details="",
    )

    assert "Minimalist ceramic coffee mug" in prompt
    assert isinstance(prompt, str)
    assert isinstance(negative_prompt, str)
