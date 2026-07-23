# AI Creative Studio

A portfolio project that demonstrates how Generative AI can automate product-image creation workflows through prompt engineering, REST APIs, and AI image generation.

## Highlights

- End-to-end AI image generation workflow
- Modular FastAPI architecture
- ComfyUI integration
- SQLite experiment tracking
- Interactive Streamlit interface
- Automated testing with pytest
- Dockerized deployment

## Project goal

Creative teams often repeat the same prompt-writing and image-generation steps. AI Creative Studio streamlines this process by combining a Streamlit interface, a FastAPI backend, reusable prompt engineering, ComfyUI integration, and SQLite-based generation history into an end-to-end workflow for creating and tracking AI-generated marketing assets.

1. Describe a product.
2. Select a visual style, background, lighting, and aspect ratio.
3. Generate a structured production-ready prompt.
4. Send the prompt to an image-generation backend.
5. Review and compare the results.


## Why this project matters

Through this project I explored:

- Designing end-to-end Generative AI applications
- Building reusable prompt engineering workflows
- Developing REST APIs with FastAPI
- Integrating external AI services through ComfyUI
- Designing modular Python applications
- Building interactive Streamlit interfaces
- Tracking experiments with SQLite
- Containerizing applications with Docker

## Tech Stack

### Frontend
- Streamlit

### Backend
- FastAPI
- Pydantic

### AI & Image Generation
- ComfyUI
- FLUX (via ComfyUI workflows)
- Prompt Engineering

### Data & Storage
- SQLite

### Development & DevOps
- Docker
- Git
- Python

## Architecture

```text
                 Streamlit
                     │
                     ▼
              FastAPI Backend
                     │
      ┌──────────────┼──────────────┐
      ▼              ▼              ▼
 Prompt Service  ComfyUI Client  SQLite Database
```

## Repository Structure

```text
api/            FastAPI backend
app/            Streamlit frontend
services/       Prompt building and generation services
tests/          Automated tests
generated/      Generated images
workflows/      ComfyUI workflow definitions
```

## Current Features

- Guided product-description workflow
- Structured prompt generation
- Negative prompt generation
- Configurable generation parameters (seed, steps, CFG, image size)
- Style, background, lighting, camera angle, and aspect-ratio presets
- ComfyUI image generation
- Mock backend for local development
- SQLite generation history
- Generation timing
- Download generated images
- Interactive Streamlit interface
- FastAPI REST API
- Automatic API documentation (Swagger/OpenAPI)
- Docker support
- Automated testing with pytest

## Future Improvements

- Regenerate from history
- Image-to-image generation
- Prompt template library
- Background removal
- Cloud deployment

## Run locally

### 1. Create an environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure the image backend

Create a `.env` file in the project root:

```text
IMAGE_BACKEND=comfyui
COMFYUI_URL=http://127.0.0.1:8188
```

Make sure ComfyUI is running before starting the API.

### 3. Start the API

```bash
uvicorn api.main:app --reload --port 8000
```

API documentation:

```text
http://localhost:8000/docs
```

### 4. Start Streamlit

Open a second terminal:

```bash
streamlit run app/main.py
```

## Run Tests

```bash

python -m pytest -v

```

Current test coverage includes:

- Prompt-building logic

- FastAPI health endpoint

- Mock image-generation workflow

- Request validation

## Run with Docker

```bash
docker compose up --build
```

Then open:

- Streamlit: http://localhost:8501
- FastAPI docs: http://localhost:8000/docs


## Screenshots

_Coming soon._

## Portfolio positioning

AI Creative Studio was built as a portfolio project to demonstrate how Generative AI workflows can be structured into modular, testable, and user-friendly applications using modern Python tools and frameworks.

## Author

Timothy Ajayi
