from pydantic import BaseModel, Field

class URLRetrievalResponse(BaseModel):

    answer: str = Field(..., description="Antwort auf die Frage.")
    url: str = Field(...,description="URL mit den relevantesten Inhalten zur gestellten Frage.")
    reason: str = Field(..., description="Begründung für die Antwort und URL.")

class URLSelectionResponse(BaseModel):
    answer: str = Field(..., description="Antwort auf die Frage.")
    chunk_nr: str = Field(...,description="Nummer des Chunks, der am relevantesten ist")
    reason: str = Field(..., description="Begründung für die Antwort und URL.")
    url: str = Field(...,description="URL mit den relevantesten Inhalten zur gestellten Frage.", exclude=True)
    chunk: str = Field(...,description="Chunk, der am relevantesten ist",exclude=True)