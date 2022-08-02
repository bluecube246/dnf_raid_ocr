from django.db import models


class Feature:
    name: str
    id: int


class Character:
    name: str
    job: str
    id: int
    character_id: str
    server: str
    guild: str
    adventureName: str
    ms: int
