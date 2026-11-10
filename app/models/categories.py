from pydantic import BaseModel,Field,ConfigDict
from typing import Literal

class AddCategoriesForm(BaseModel):
    category : str = Field(min_length=3)
    description : str = Field(min_length=10)
    expense_type : Literal['income','expense']
    expense_classification : str | None = None

    model_config = ConfigDict({
        'json_schema_extra' : {
            'examples' : [
                {
                    "category": "Rent",
                    "description": "House rent or accommodation expenses",
                    "expense_type": "expense",
                    "expense_classification": "essential",
                }
            ]
        }
    })