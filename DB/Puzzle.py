from typing import List, Union
from pydantic import BaseModel
from DetaDB import DetaBase

class PuzzleDB:
    def __init__(self):
        return DetaBase().Base("puzzles")