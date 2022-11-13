from typing import Optional

from pydantic import BaseModel, validator

DEFAULT_IMAGE_URL = (
    "https://upload.wikimedia.org/wikipedia/"
    "commons/1/14/No_Image_Available.jpg?20200913095930"
)
DEFAULT_IMAGE_DICT = {"medium": DEFAULT_IMAGE_URL}

DEFAULT_COUNTRY_NAME = "Undefined Country"
DEFAULT_COUNTRY_DICT = {"name": DEFAULT_COUNTRY_NAME}
DEFAULT_NETWORK_NAME = "Undefined network"
DEFAULT_NETWORK_DICT = {
    "name": DEFAULT_NETWORK_NAME,
    "country": DEFAULT_COUNTRY_DICT,
}


class Country(BaseModel):
    name: str

    @validator("name", pre=True, always=True)
    def name_is_none(cls, v: Optional[str]) -> str:
        if not v:
            v = DEFAULT_COUNTRY_NAME
        return v


class Network(BaseModel):
    name: str
    country: Country

    @validator("name", pre=True, always=True)
    def name_is_none(cls, v: Optional[str]) -> str:
        if not v:
            v = DEFAULT_NETWORK_NAME
        return v

    @validator("country", pre=True, always=True)
    def country_is_none(cls, v: Optional[Country]) -> Country:
        if not v:
            v = Country(**DEFAULT_COUNTRY_DICT)
        return v


class Image(BaseModel):
    medium: str

    @validator("medium", pre=True, always=True)
    def medium_is_none(cls, v: Optional[str]) -> str:
        if not v:
            v = DEFAULT_IMAGE_URL
        return v


class TVProgram(BaseModel):
    name: str = ""
    network: Network
    summary: str
    image: Image

    @validator("summary", pre=True, always=True)
    def summary_is_none(cls, v: Optional[str]) -> str:
        if not v:
            v = "Summary is missing("
        return v

    @validator("network", pre=True, always=True)
    def network_is_none(cls, v: Optional[Network]) -> Network:
        if not v:
            v = Network(**DEFAULT_NETWORK_DICT)
        return v

    @validator("image", pre=True, always=True)
    def image_is_none(cls, v: Optional[Image]) -> Image:
        if not v:
            v = Image(**DEFAULT_IMAGE_DICT)
        return v

    @validator("name")
    def name_must_be_defined(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            raise ValueError("Name must be specified")
        return v
