from pydantic import BaseModel, Field, ConfigDict
from typing import Literal
from datetime import date

class AddUpdateTransactionForm(BaseModel):
    amount : int = Field(gt=0),
    mode : Literal['income','expense']
    notes : str = Field(default='')
    payment : Literal["bank", "card", "cash", "others", "upi"] 
    date : date
    category : int

    model_config = ConfigDict(json_schema_extra={
        "examples" : [{
            "amount": 2000,
            "date": "2026-10-28",
            "mode": "expense",
            "notes": "AWS EC2 Instance",
            "payment": "card",
            "category" : 3
        }]
    })

class DateFilterForm(BaseModel):
    start_date : date
    end_date : date

    model_config = ConfigDict(json_schema_extra={
        'examples':[{
            'start_date' : '2026-10-01',
            'end_date' : '2026-10-31'
        }]
    })