from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, model_validator


TransactionPeriod = Literal[
    "today",
    "this_week",
    "this_month",
    "last_month",
    "last_30_days",
    "this_year",
    "all_time",
    "custom",
]


class AIChatRequest(BaseModel):

    question: str = Field(
        ...,
        min_length=1,
        max_length=2000
    )

    period: TransactionPeriod = "all_time"

    startdate: date | None = None
    enddate: date | None = None

    @model_validator(mode="after")
    def validate_date_range(self):

        if self.period == "custom":

            if self.startdate is None or self.enddate is None:
                raise ValueError(
                    "Both startdate and enddate are required for custom range"
                )

            if self.startdate > self.enddate:
                raise ValueError(
                    "Start date cannot be after end date"
                )

        elif self.startdate is not None or self.enddate is not None:

            raise ValueError(
                "Custom dates are only allowed when period is custom"
            )

        return self