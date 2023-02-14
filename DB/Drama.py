from typing import List, Union
from pydantic import BaseModel
from DetaDB import DetaBase

class DramaDB:
    def __init__(self):
        return DetaBase().Base("dramas")