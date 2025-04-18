from __future__ import annotations

from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional

from pymongo import MongoClient
from django.conf import settings
from bson.objectid import ObjectId
from dateutil.relativedelta import relativedelta
import jdatetime

MONTH_NAMES_FA = [
    "فروردین", "اردیبهشت", "خرداد", "تیر",
    "مرداد", "شهریور", "مهر", "آبان",
    "آذر", "دی", "بهمن", "اسفند"
]

def to_jalali_str(g_date: date) -> str:
    """Gregorian → 'YYYY/MM/DD' (Jalali) با jdatetime (کندتر)"""
    jd = jdatetime.date.fromgregorian(date=g_date)
    return f"{jd.year}/{jd.month:02d}/{jd.day:02d}"




def get_date_range(mode: str, end_date: Optional[datetime] = None) -> datetime:
    """
    Calculate start date based on mode and end date.

    Args:
        mode: 'daily', 'weekly', or 'monthly'
        end_date: Reference end date (defaults to now if None)

    Returns:
        The calculated start date
    """
    if end_date is None:
        end_date = datetime.now()

    if mode == "daily":
        return end_date - timedelta(days=1000)
    elif mode == "weekly":
        return end_date - timedelta(weeks=40)
    elif mode == "monthly":
        return end_date - relativedelta(months=20)
    else:
        return end_date - timedelta(days=30)


def get_transaction_report(
    type_param: str,
    mode: str,
    merchant_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    بر اساس type_param ('count' یا 'amount') و mode ('daily'/'weekly'/'monthly')
    گزارش را از کالکشن transactions استخراج می‌کند.

    * اتصال به MongoDB همین‌جا داخل تابع ساخته و بسته می‌شود.
    * دیتابیس یا ایندکس دستکاری نمی‌شود.
    """
    client = MongoClient(settings.MONGODB_HOST, settings.MONGODB_PORT)
    db = client[settings.MONGODB_DB]

    end_date = datetime.now()
    start_date = get_date_range(mode, end_date)

    match_stage: Dict[str, Any] = {"createdAt": {"$gte": start_date, "$lte": end_date}}

    if merchant_id:
        try:
            match_stage["merchantId"] = ObjectId(merchant_id)
        except Exception:
            match_stage["merchantId"] = merchant_id

    if mode == "daily":
        group_id = {
            "y": {"$year": "$createdAt"},
            "m": {"$month": "$createdAt"},
            "d": {"$dayOfMonth": "$createdAt"},
        }
        sort_stage = {"_id.y": 1, "_id.m": 1, "_id.d": 1}

    elif mode == "weekly":
        group_id = {
            "y": {"$isoWeekYear": "$createdAt"},
            "w": {"$isoWeek": "$createdAt"},
        }
        sort_stage = {"_id.y": 1, "_id.w": 1}

    elif mode == "monthly":
        group_id = {
            "y": {"$year": "$createdAt"},
            "m": {"$month": "$createdAt"},
        }
        sort_stage = {"_id.y": 1, "_id.m": 1}

    if type_param == "amount":
        value_expr = "$numeric_amount"
        add_fields = [{
            "$addFields": {
                "numeric_amount": {"$toDouble": {"$ifNull": ["$amount", 0]}}
            }
        }]
    else:
        value_expr = 1
        add_fields = []

    pipeline = [
        {"$match": match_stage},
        *add_fields,
        {
            "$group": {
                "_id": group_id,
                "value": {"$sum": value_expr},
            }
        },
        {"$sort": sort_stage},
    ]

    cursor = db.transactions.aggregate(pipeline)

    formatted_results: List[Dict[str, Any]] = []

    for doc in cursor:
        _id = doc["_id"]
        val = float(doc["value"])

        if mode == "daily":
            g_date = date(_id["y"], _id["m"], _id["d"])
            key = to_jalali_str(g_date)

        elif mode == "weekly":
            g_date = datetime.strptime(f"{_id['y']}-{_id['w']}-1", "%G-%V-%u").date()
            j_year = to_jalali_str(g_date).split("/")[0]
            key = f"هفته {_id['w']} سال {j_year}"

        elif mode == "monthly":
            g_date = date(_id["y"], _id["m"], 1)
            j_year = int(to_jalali_str(g_date).split("/")[0])
            key = f"{MONTH_NAMES_FA[_id['m'] - 1]} {j_year}"

        formatted_results.append({"key": key, "value": val})

    client.close()

    return formatted_results
