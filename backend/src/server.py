from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import logging
from src.content_generator import ContentGenerator
from models.content_generation_models import ContentGeneration
from src.scraping import FalabellaScraper

# Configurar logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI-Powered Text Generation with LLMs",
    description="""Create high-quality text content using advanced Large Language Models (LLMs).  
                  Generate textual descriptions, narratives, and insights from images and text inputs.  
                  Access the Streamlit interface at port 8501 for an interactive experience.""",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    """Endpoint to check the health of the API"""
    return {"status": "ok"}


@app.post("/content_generator")
def generate_content(request: ContentGeneration):
    """Generate content based on metadata scraped from the given URL"""
    try:
        logger.info(f"Scraping metadata from URL: {request.url}")

        # Extraer metadata con MercadoLibreScraper
        metadata = FalabellaScraper(str(request.url)).scrape()

        # Verificar si metadata contiene datos válidos
        if not metadata or not isinstance(metadata, dict):
            raise ValueError("No se pudo extraer metadata válida del producto.")

        logger.info(f"Metadata scraped: {metadata}")

        # Generar contenido con el modelo LLM
        content = ContentGenerator().generate_content(
            metadata, request.new_target_audience, request.new_tone, request.language
        )

        logger.info("Content generated successfully")
        return {"generated_content": content}

    except ValueError as ve:
        logger.error(f"ValueError: {ve}")
        raise HTTPException(
            status_code=400, detail={"error": "Datos inválidos", "message": str(ve)}
        )

    except Exception as e:
        logger.error(f"Error interno: {e}")
        raise HTTPException(
            status_code=500, detail={"error": "Error interno", "message": str(e)}
        )
