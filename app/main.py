import os
import random
import time

import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="AI Creative Studio",
    page_icon="🎨",
    layout="wide",
)


@st.cache_data(ttl=300, show_spinner=False)
def download_image(image_url: str) -> bytes:

    response = requests.get(
        image_url,
        timeout=60,
    )

    response.raise_for_status()
    return response.content


st.title("AI Creative Studio")
st.caption("Build, generate, compare, and track reusable product-image workflows.")


with st.sidebar:
    st.header("Generation Settings")

    model = st.selectbox(
        "Model",
        [
            "Z Image Turbo",
            # "FLUX Schnell",
        ],
    )

    lora = st.selectbox(
        "LoRA",
        [
            "None",
            "Realistic Snapshot",
            "35mm Photo",
            "Aesthetic",
        ],
    )

    lora_strength = st.slider(
        "LoRA Strength",
        min_value=0.0,
        max_value=1.2,
        value=0.8,
        step=0.05,
    )

    st.divider()

    style = st.selectbox(
        "Visual style",
        [
            "Commercial e-commerce",
            "Premium fashion campaign",
            "Minimal editorial",
            "Lifestyle advertising",
            "Cinematic product photography",
        ],
    )

    background = st.selectbox(
        "Background",
        [
            "Clean white studio background",
            "Soft neutral gradient background",
            "Modern architectural setting",
            "Urban lifestyle environment",
            "Minimal pastel backdrop",
        ],
    )

    lighting = st.selectbox(
        "Lighting",
        [
            "Soft diffused studio lighting",
            "Dramatic directional lighting",
            "Natural window lighting",
            "High-key commercial lighting",
            "Warm golden-hour lighting",
        ],
    )

    angle = st.selectbox(
        "Camera angle",
        [
            "Three-quarter product view",
            "Front-facing product view",
            "Low-angle hero shot",
            "Top-down flat lay",
            "Close-up detail shot",
        ],
    )

    ratio = st.selectbox(
        "Aspect ratio",
        [
            "1:1",
            "4:5",
            "16:9",
            "9:16",
        ],
    )

    seed_mode = st.radio(
        "Seed",
        ["Fixed", "Random"],
        horizontal=True,
    )

    seed = st.number_input(
        "Seed value",
        min_value=0,
        value=42,
        step=1,
    )

    steps = st.slider(
        "Steps",
        min_value=1,
        max_value=50,
        value=8,
    )

    cfg = st.slider(
        "CFG scale",
        min_value=1.0,
        max_value=15.0,
        value=1.0,
        step=0.5,
    )

    count = st.slider(
        "Images to compare",
        min_value=1,
        max_value=4,
        value=1,
    )

    sizes = {
        "Square 512": (512, 512),
        "Square 768": (768, 768),
        "Square 1024": (1024, 1024),
        "Portrait 768 × 960": (768, 960),
        "Landscape 960 × 640": (960, 640),
    }

    selected_size = st.selectbox(
        "Image size",
        list(sizes.keys()),
    )

    width, height = sizes[selected_size]


t1, t2, t3 = st.tabs(
    [
        "Generate & compare",
        "Generation history",
        "About",
    ]
)
with t1:
    product = st.text_area(
        "Product description",
        placeholder="Premium black running sneakers with reflective details",
        height=110,
    )

    extra = st.text_input(
        "Additional creative direction",
        placeholder="Subtle shadow, premium campaign, no visible branding",
    )

    if "enhanced_prompt" not in st.session_state:
        st.session_state.enhanced_prompt = ""

    payload = {
        "product_description": product,
        "model": model,
        "lora": lora,
        "lora_strength": lora_strength,
        "style": style,
        "background": background,
        "lighting": lighting,
        "camera_angle": angle,
        "aspect_ratio": ratio,
        "extra_details": extra,
        "seed": (random.randint(0, 2**31 - 1) if seed_mode == "Random" else int(seed)),
        "steps": steps,
        "cfg": cfg,
        "width": width,
        "height": height,
        "image_count": count,
    }

    enhance_col, generate_col = st.columns(2)

    with enhance_col:
        enhance_clicked = st.button(
            "Enhance Prompt",
            use_container_width=True,
        )

    with generate_col:
        generate_clicked = st.button(
            "Generate Images",
            type="primary",
            use_container_width=True,
        )

    if enhance_clicked:
        if not product.strip():
            st.warning("Please enter a product description.")
        else:
            try:
                with st.spinner("Enhancing prompt..."):
                    enhance_response = requests.post(
                        f"{API_URL}/enhance-prompt",
                        json=payload,
                        timeout=60,
                    )

                    enhance_response.raise_for_status()
                    enhanced_result = enhance_response.json()

                st.session_state.enhanced_prompt = enhanced_result["enhanced_prompt"]

                st.success("Prompt enhanced successfully.")

            except requests.RequestException as error:
                try:
                    detail = (
                        error.response.json().get("detail", "")
                        if error.response is not None
                        else ""
                    )
                except Exception:
                    detail = ""

                st.error(detail or str(error))

    st.text_area(
        "Enhanced prompt",
        key="enhanced_prompt",
        height=180,
        placeholder=(
            "Click “Enhance Prompt” to create a detailed prompt, "
            "then edit it before generating."
        ),
    )

    if generate_clicked:
        if not product.strip():
            st.warning("Please enter a product description.")
            st.stop()

        payload["custom_prompt"] = (
            st.session_state.enhanced_prompt.strip()
            if st.session_state.enhanced_prompt.strip()
            else None
        )

        start_time = time.perf_counter()

        try:
            with st.spinner("Running creative workflow..."):
                res = requests.post(
                    f"{API_URL}/generate",
                    json=payload,
                    timeout=900,
                )

                res.raise_for_status()
                result = res.json()

            elapsed_time = time.perf_counter() - start_time

            st.success(f"Generation #{result['id']} completed in {elapsed_time:.1f} s.")

            with st.expander("Prompt and parameters"):
                st.code(result["prompt"], language=None)
                st.code(result["negative_prompt"], language=None)

                st.json(
                    {
                        "lora": result["lora"],
                        "lora_strength": result["lora_strength"],
                        "seed": result["seed"],
                        "steps": result["steps"],
                        "cfg": result["cfg"],
                        "size": (f"{result['width']} × {result['height']}"),
                        "backend": result["backend"],
                    }
                )

            images = result.get("images", [])

            if images:
                cols = st.columns(min(len(images), 2))

                for i, url in enumerate(images):
                    with cols[i % len(cols)]:
                        try:
                            image_bytes = download_image(url)

                            st.image(
                                image_bytes,
                                caption=f"Option {i + 1}",
                                use_container_width=True,
                            )

                            st.download_button(
                                label=f"Download option {i + 1}",
                                data=image_bytes,
                                file_name=(
                                    f"ai_creative_studio_"
                                    f"generation_{result['id']}_"
                                    f"option_{i + 1}.png"
                                ),
                                mime="image/png",
                                key=(f"download_generated_{result['id']}_{i + 1}"),
                                use_container_width=True,
                            )

                        except requests.RequestException as image_error:
                            st.error(f"Could not load image {i + 1}: {image_error}")
                            st.write("Image URL:", url)

            elif result.get("backend") == "mock":
                st.info(
                    "Mock mode is active. Set "
                    "IMAGE_BACKEND=comfyui and restart FastAPI."
                )

            else:
                st.warning("The backend completed the request but returned no images.")

        except requests.RequestException as error:
            try:
                detail = (
                    error.response.json().get("detail", "")
                    if error.response is not None
                    else ""
                )
            except Exception:
                detail = ""

            st.error(detail or str(error))

with t2:
    st.subheader("Generation history")

    if st.button("Load generation history"):
        try:
            response = requests.get(
                f"{API_URL}/history",
                timeout=20,
            )
            response.raise_for_status()

            records = response.json()

            if not records:
                st.info("No generations saved yet.")

            for record in records:
                generation_id = record["id"]
                created_at = record["created_at"][:19]

                with st.expander(f"Generation #{generation_id} · {created_at}"):
                    st.write(record["prompt"])

                    st.json(
                        {
                            "seed": record["seed"],
                            "steps": record["steps"],
                            "cfg": record["cfg"],
                            "size": (f"{record['width']} × {record['height']}"),
                            "backend": record["backend"],
                        }
                    )

                    images = record.get("images", [])

                    if images:
                        columns = st.columns(min(len(images), 2))

                        for index, image_url in enumerate(images):
                            with columns[index % len(columns)]:
                                try:
                                    image_bytes = download_image(image_url)

                                    st.image(
                                        image_bytes,
                                        caption=f"Option {index + 1}",
                                        use_container_width=True,
                                    )

                                except requests.RequestException as image_error:
                                    st.error(
                                        f"Could not load image "
                                        f"{index + 1}: {image_error}"
                                    )

        except requests.RequestException as error:
            st.warning(f"History unavailable: {error}")


with t3:
    st.subheader("ℹ️ Info")

    st.markdown(
        """
        **AI Creative Studio** is an end-to-end AI application for generating,
        comparing, and tracking product images using reusable prompt workflows.

        **Architecture**

        `Streamlit → FastAPI → Prompt Builder → ComfyUI → SQLite`
        """
    )
