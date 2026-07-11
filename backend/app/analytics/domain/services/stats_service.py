import datetime
import decimal
import time
from collections import defaultdict

from app.commons import logs, base_types, standard_types
from app.commons.adapters import unit_of_work
from app.analytics.domain.model import dtos, entities

_LOGGER = logs.get_logger()

_EPOCH = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)


def _get_account_balance(
    uow: unit_of_work.AbstractUnitOfWork,
    user_id: str,
    account_id: str | None = None,
) -> base_types.Money:
    repo = uow.get_repo(entity_type=entities.Account)
    find: dict = {"user_id": user_id}
    if account_id:
        find["id"] = account_id
    account = next(repo.find_by(find=find), None)
    if not account:
        return base_types.Money(amount=decimal.Decimal("0"))
    return account.balance


def _ts_from_str(s: str | None) -> standard_types.Timestamp | None:
    if s is None:
        return None
    return standard_types.Timestamp.from_string(s)


def by_category(
    uow: unit_of_work.AbstractUnitOfWork,
    user_id: str,
    account_id: str | None = None,
    category: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
) -> list[dtos.CategoryStatResponse]:
    _LOGGER.info("Getting stats by category for user [%s]", user_id)
    repo = uow.get_repo(entity_type=entities.Movement)

    filters: dict = {"user_id": user_id}
    if account_id:
        filters["account_id"] = account_id

    from_ts = _ts_from_str(from_date)
    to_ts = _ts_from_str(to_date)
    if from_ts:
        filters["created_at.value"] = {"$gte": from_ts.value}
    if to_ts:
        filters["created_at.value"] = filters.get("created_at.value", {})
        filters["created_at.value"]["$lte"] = to_ts.value

    movements = repo.find_by(find=filters)

    groups: dict[tuple[str, str], dict] = {}
    for m in movements:
        if category and m.category != category:
            continue
        key = (m.category, m.movement_type)
        if key not in groups:
            groups[key] = {"total": decimal.Decimal("0"), "count": 0}
        groups[key]["total"] += decimal.Decimal(str(m.money.amount))
        groups[key]["count"] += 1

    return [
        dtos.CategoryStatResponse(
            category=cat,
            total=str(data["total"]),
            movement_type=mtype,
            count=data["count"],
        )
        for (cat, mtype), data in sorted(groups.items(), key=lambda x: -float(x[1]["total"]))
    ]


def monthly(
    uow: unit_of_work.AbstractUnitOfWork,
    user_id: str,
    account_id: str | None = None,
    months: int = 6,
) -> list[dtos.MonthlyStatResponse]:
    _LOGGER.info("Getting monthly stats for user [%s] for [%d] months", user_id, months)

    since = standard_types.Timestamp.now()
    since.value -= months * 31 * 86400

    repo = uow.get_repo(entity_type=entities.Movement)

    filters: dict = {"user_id": user_id, "created_at.value": {"$gte": since.value}}
    if account_id:
        filters["account_id"] = account_id

    movements = repo.find_by(find=filters)

    groups: dict[tuple[int, int], dict] = {}
    for m in movements:
        dt = datetime.datetime.fromtimestamp(m.created_at.value, tz=datetime.timezone.utc)
        key = (dt.year, dt.month)
        if key not in groups:
            groups[key] = {"income": decimal.Decimal("0"), "expense": decimal.Decimal("0"), "count": 0}
        entry = groups[key]
        amount = decimal.Decimal(str(m.money.amount))
        if m.movement_type == "INCOME":
            entry["income"] += amount
        else:
            entry["expense"] += amount
        entry["count"] += 1

    return [
        dtos.MonthlyStatResponse(
            year=y,
            month=m,
            income=str(data["income"]),
            expense=str(data["expense"]),
            count=data["count"],
        )
        for (y, m), data in sorted(groups.items(), reverse=True)
    ]


def weekly(
    uow: unit_of_work.AbstractUnitOfWork,
    user_id: str,
    account_id: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
) -> dtos.WeeklyStatResponse:
    _LOGGER.info("Getting weekly stats for user [%s]", user_id)

    now_ts = standard_types.Timestamp.now()

    from_ts = _ts_from_str(from_date)
    to_ts = _ts_from_str(to_date)

    if not from_ts:
        today = datetime.datetime.fromtimestamp(now_ts.value, tz=datetime.timezone.utc)
        week_start = today - datetime.timedelta(days=today.weekday())
        from_ts = standard_types.Timestamp(value=week_start.timestamp())
    if not to_ts:
        to_ts = now_ts

    repo = uow.get_repo(entity_type=entities.Movement)

    filters: dict = {
        "user_id": user_id,
        "created_at.value": {"$gte": from_ts.value, "$lte": to_ts.value},
    }
    if account_id:
        filters["account_id"] = account_id

    movements = list(repo.find_by(find=filters))

    by_category: dict[tuple[str, str], dict] = {}
    by_day: dict[str, dict] = {}
    totals: dict[str, dict] = {}

    for m in movements:
        amount = decimal.Decimal(str(m.money.amount))

        cat_key = (m.category, m.movement_type)
        if cat_key not in by_category:
            by_category[cat_key] = {"total": decimal.Decimal("0"), "count": 0}
        by_category[cat_key]["total"] += amount
        by_category[cat_key]["count"] += 1

        if m.movement_type not in totals:
            totals[m.movement_type] = {"total": decimal.Decimal("0"), "count": 0}
        totals[m.movement_type]["total"] += amount
        totals[m.movement_type]["count"] += 1

        day = m.created_at.format("%Y-%m-%d")
        if day not in by_day:
            by_day[day] = {"income": decimal.Decimal("0"), "expense": decimal.Decimal("0"), "count": 0}
        day_entry = by_day[day]
        if m.movement_type == "INCOME":
            day_entry["income"] += amount
        else:
            day_entry["expense"] += amount
        day_entry["count"] += 1

    total_income = str(totals.get("INCOME", {}).get("total", decimal.Decimal("0")))
    total_expense = str(totals.get("EXPENSE", {}).get("total", decimal.Decimal("0")))
    movement_count = sum(t.get("count", 0) for t in totals.values())

    return dtos.WeeklyStatResponse(
        total_income=total_income,
        total_expense=total_expense,
        movement_count=movement_count,
        by_category=[
            dtos.CategoryStatResponse(
                category=cat,
                total=str(data["total"]),
                movement_type=mtype,
                count=data["count"],
            )
            for (cat, mtype), data in by_category.items()
        ],
        daily_balance=[
            dtos.DailyBalanceResponse(
                date=date,
                income=str(data["income"]),
                expense=str(data["expense"]),
                count=data["count"],
            )
            for date, data in sorted(by_day.items())
        ],
    )


def summary(
    uow: unit_of_work.AbstractUnitOfWork,
    user_id: str,
    account_id: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
) -> dtos.SummaryResponse:
    _LOGGER.info("Getting summary for user [%s]", user_id)

    balance = _get_account_balance(uow=uow, user_id=user_id, account_id=account_id)

    repo = uow.get_repo(entity_type=entities.Movement)

    filters: dict = {"user_id": user_id}
    if account_id:
        filters["account_id"] = account_id

    from_ts = _ts_from_str(from_date)
    to_ts = _ts_from_str(to_date)
    if from_ts:
        filters["created_at.value"] = {"$gte": from_ts.value}
    if to_ts:
        filters["created_at.value"] = filters.get("created_at.value", {})
        filters["created_at.value"]["$lte"] = to_ts.value

    movements = repo.find_by(find=filters)

    total_income = decimal.Decimal("0")
    total_expense = decimal.Decimal("0")
    movement_count = 0

    for m in movements:
        amount = decimal.Decimal(str(m.money.amount))
        movement_count += 1
        if m.movement_type == "INCOME":
            total_income += amount
        else:
            total_expense += amount

    return dtos.SummaryResponse(
        current_balance=str(balance.amount),
        currency=balance.currency,
        total_income=str(total_income),
        total_expense=str(total_expense),
        movement_count=movement_count,
    )
