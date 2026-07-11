import pydantic


class AccountResponse(pydantic.BaseModel):
    id: str
    user_id: str
    balance: str
    currency: str


class MovementResponse(pydantic.BaseModel):
    id: str
    account_id: str
    user_id: str
    amount: str
    currency: str
    opening_balance: str
    closing_balance: str
    category: str
    description: str
    movement_type: str
    created_at: str


class MovementPageResponse(pydantic.BaseModel):
    items: list[MovementResponse]
    next_cursor: str | None


class CategoryStatResponse(pydantic.BaseModel):
    category: str
    total: str
    movement_type: str
    count: int


class MonthlyStatResponse(pydantic.BaseModel):
    year: int
    month: int
    income: str
    expense: str
    count: int


class DailyBalanceResponse(pydantic.BaseModel):
    date: str
    income: str
    expense: str
    count: int


class WeeklyStatResponse(pydantic.BaseModel):
    total_income: str
    total_expense: str
    movement_count: int
    by_category: list[CategoryStatResponse]
    daily_balance: list[DailyBalanceResponse]


class SummaryResponse(pydantic.BaseModel):
    current_balance: str
    currency: str
    total_income: str
    total_expense: str
    movement_count: int
