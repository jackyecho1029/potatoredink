from typing import List, Optional, Literal, Union, Dict, Any
from pydantic import BaseModel, Field, field_validator

class PosterSection(BaseModel):
    """Section of a poster - matches LLM output format from poster_prompt.txt"""
    icon: Optional[str] = Field(None, description="Icon keyword for the section")
    heading: str = Field(..., description="Section heading/title")
    content: str = Field(..., description="Section content text")
    style: Optional[str] = Field("neutral", description="Visual style: positive/negative/neutral")

class PosterData(BaseModel):
    """Poster data structure - matches LLM output format from poster_prompt.txt"""
    title: str = Field(..., description="Main title of the poster")
    subtitle: Optional[str] = Field(None, description="Subtitle or one-line summary")
    quote: Optional[str] = Field(None, description="Key quote or golden sentence")
    sections: List[PosterSection] = Field(default_factory=list, description="List of content sections")
    summary: Optional[str] = Field(None, description="Bottom summary text")

class OutlineRequest(BaseModel):
    topic: str = Field(..., min_length=1, description="The topic to generate content for")
    mode: Literal["outline", "poster"] = Field("outline", description="Generation mode")
    images: Optional[List[str]] = Field(None, description="List of base64 encoded images")

    @field_validator('topic')
    def topic_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Topic cannot be empty or whitespace only')
        return v

class OutlineResponse(BaseModel):
    success: bool
    mode: Literal["outline", "poster"]
    outline: Optional[str] = None
    pages: Optional[List[Dict[str, Any]]] = None
    poster_data: Optional[PosterData] = None
    has_images: bool = False
    error: Optional[str] = None
