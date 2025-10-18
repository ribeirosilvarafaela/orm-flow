from pydantic import BaseModel

class Settings(BaseModel):
    AUDIVERIS_JAR: str = "/app/audiveris.jar"
    OMR_DPI: int = 400
    MAX_PAGES: int = 30
    OUTPUT_DIR: str = "data/outputs"

settings = Settings()
