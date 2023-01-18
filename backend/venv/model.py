from fastapi.encoders import jsonable_encoder

# Pydantic, and Python's built-in typing are used to define a schema
# that defines the structure and types of the different objects stored
# in the recipes collection, and managed by this API.
from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import datetime
from objectid import PydanticObjectId

import bson

# Nume și prenume
# Adresă de email
# Parola
# Vârsta
# Gen
# (opțional) 3 filme preferate
# (opțional) 3 genuri de filme preferate
# Register date

class User(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    first_name: str
    last_name: str
    email_address: str
    password: str
    age: str
    gender: str
    films: List[str]
    film_types: List[str]
    register_date: Optional[datetime]

    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data 

# jti
# created_at

class RevokeToken(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    jti: str
    created_at: Optional[datetime]

    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data

class Film(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    budget: str
    genres: str
    homepage: str
    keywords: str
    original_language: str
    original_title: str
    overview: str
    popularity: str
    production_companies: str
    production_countries: str
    release_date: str
    revenue: str
    runtime: str
    status: str
    tagline: str
    title: str
    vote_average: str
    vote_count: str
    movie_id: str
    register_date: Optional[datetime]

    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data  