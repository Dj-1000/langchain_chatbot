from langchain_core.pydantic_v1 import BaseModel, Field

class BotOuput(BaseModel):
    """Bot output structure"""
    is_match: bool = Field(..., description="Boolean, set to True if the highest intent score is more than 0.5, else False")
    message: str = Field(..., description="A message asking for more details if 'is_match' is False.")
    category: int = Field(..., description="The id of folder or file with the highest intent score.")
    intent_score : int = Field(..., description="Intent score of the user")
    file_name: str = Field(..., description="The name of the file with the highest intent score, or null if no match.")
    
class IntentScoreOutput(BaseModel):
    """description"""
    is_match: bool = Field(..., description="Boolean, set to True if the highest intent score is more than 0.5.")
    message: str = Field(..., description="A message asking for more details if 'is_match' is False.")
    category: int = Field(..., description="The id of the folder with the highest intent score.")
    intent_score : int = Field(..., description="The intent score of the folder with the highest intent score.")
    
class FileIntentScoreOutput(BaseModel):
    """dis"""
    is_match: bool = Field(..., description="Boolean, set to True if any file intent score is more than 0.7.")
    message: str = Field(..., description="A message asking for more details if 'is_match' is False or requesting confirmation if 'is_match' is True.")
    file_name: str = Field(..., description="The name of the file with the highest intent score, or null if no match.")
    file_id: int = Field(..., description="The ID of the file with the highest intent score, or null if no match")
    category : int = Field(..., description="The id of the parent folder of the file with the highest intent score, or null if no match")