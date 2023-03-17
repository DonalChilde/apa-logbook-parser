from pathlib import Path

from pydantic import BaseModel


class HashedFile(BaseModel):
    file_path: Path
    file_hash: str
    hash_method: str


class ParsedMetadata(BaseModel):
    original_source: HashedFile
    source: HashedFile | None
    data_model_name: str
    data_model_version: str
