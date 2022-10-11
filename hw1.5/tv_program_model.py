from pydantic import BaseModel, validator


class Country(BaseModel):
    name: str = ""

    @validator("name")
    def name_must_be_defined(cls, v: str) -> str:
        if v is None or v == "":
            raise ValueError("Name must be specified")
        return v.title()


class Network(BaseModel):
    name: str = ""
    country: Country

    @validator("name")
    def name_must_be_defined(cls, v: str) -> str:
        if v is None or v == "":
            raise ValueError("Name must be specified")
        return v

    @validator("country")
    def country_must_be_defined(cls, v: Country) -> Country:
        if v is None:
            raise ValueError("Country must be specified")
        return v


class TVProgram(BaseModel):
    name: str = ""
    network: Network
    summary: str = ""

    @validator("name")
    def name_must_be_defined(cls, v: str) -> str:
        if v is None or v == "":
            raise ValueError("Name must be specified")
        return v

    @validator("summary")
    def summary_must_be_defined(cls, v: str) -> str:
        if v is None or v == "":
            raise ValueError("")
        return v

    @validator("network")
    def network_must_be_defined(cls, v: Network) -> Network:
        if v is None:
            raise ValueError("Network must be specified")
        return v


def print_tv_program(program: TVProgram) -> None:
    print(f"Name: {program.name}")
    print(f"Network Name: {program.network.name}")
    print(f"Network Country Name: {program.network.country.name}")
    print(f"Summary: {program.summary}")
