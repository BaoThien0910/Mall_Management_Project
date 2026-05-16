"""Reports service for generating management reports."""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from decimal import Decimal


# Mock data
MOCK_REVENUE_DATA = [
    {
        "month": "2025-09",
        "total_revenue": 850000000,
        "rent_revenue": 650000000,
        "service_revenue": 200000000,
    },
    {
        "month": "2025-10",
        "total_revenue": 920000000,
        "rent_revenue": 700000000,
        "service_revenue": 220000000,
    },
    {
        "month": "2025-11",
        "total_revenue": 950000000,
        "rent_revenue": 720000000,
        "service_revenue": 230000000,
    },
    {
        "month": "2025-12",
        "total_revenue": 1100000000,
        "rent_revenue": 800000000,
        "service_revenue": 300000000,
    },
]

MOCK_DEBT_DATA = [
    {
        "tenant": "Starbucks",
        "premise": "GF-01",
        "outstanding_amount": 38000000,
        "overdue_days": 15,
        "status": "overdue",
        "last_payment": "2025-10-15",
    },
    {
        "tenant": "Uniqlo",
        "premise": "L2-12",
        "outstanding_amount": 0,
        "overdue_days": 0,
        "status": "paid",
        "last_payment": "2025-11-05",
    },
    {
        "tenant": "Highlands Coffee",
        "premise": "GF-08",
        "outstanding_amount": 24000000,
        "overdue_days": 5,
        "status": "overdue",
        "last_payment": "2025-10-25",
    },
    {
        "tenant": "Watsons",
        "premise": "GF-12",
        "outstanding_amount": 45000000,
        "overdue_days": 45,
        "status": "overdue",
        "last_payment": "2025-09-20",
    },
]

MOCK_OCCUPANCY_DATA = {
    "total_premises": 120,
    "occupied": 95,
    "vacant": 25,
    "occupancy_rate": 79.17,
    "by_floor": [
        {"floor": "Ground", "total": 35, "occupied": 30, "occupancy_rate": 85.7},
        {"floor": "L1", "total": 30, "occupied": 25, "occupancy_rate": 83.3},
        {"floor": "L2", "total": 30, "occupied": 25, "occupancy_rate": 83.3},
        {"floor": "L3", "total": 25, "occupied": 15, "occupancy_rate": 60.0},
    ],
    "by_category": [
        {"category": "F&B", "count": 12, "occupancy_rate": 100},
        {"category": "Fashion", "count": 15, "occupancy_rate": 93.3},
        {"category": "Services", "count": 20, "occupancy_rate": 75.0},
        {"category": "Retail", "count": 28, "occupancy_rate": 71.4},
        {"category": "Others", "count": 20, "occupancy_rate": 65.0},
    ],
}


def get_revenue_report(
    start_month: Optional[str] = None, end_month: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get revenue report for specified period.
    
    Args:
        start_month: Start month in YYYY-MM format
        end_month: End month in YYYY-MM format
    
    Returns:
        Revenue data with trends and summary
    """
    filtered_data = MOCK_REVENUE_DATA.copy()

    if start_month:
        filtered_data = [d for d in filtered_data if d["month"] >= start_month]
    if end_month:
        filtered_data = [d for d in filtered_data if d["month"] <= end_month]

    if not filtered_data:
        filtered_data = MOCK_REVENUE_DATA[-3:]  # Last 3 months

    total_revenue = sum(d["total_revenue"] for d in filtered_data)
    total_rent = sum(d["rent_revenue"] for d in filtered_data)
    total_service = sum(d["service_revenue"] for d in filtered_data)

    return {
        "summary": {
            "total_revenue": total_revenue,
            "total_rent": total_rent,
            "total_service": total_service,
            "avg_monthly_revenue": total_revenue // len(filtered_data) if filtered_data else 0,
        },
        "data": filtered_data,
        "period": {"start": start_month or filtered_data[0]["month"], "end": end_month or filtered_data[-1]["month"]},
    }


def get_debt_report(
    status_filter: Optional[str] = None, overdue_only: bool = False
) -> Dict[str, Any]:
    """
    Get debt collection report.
    
    Args:
        status_filter: Filter by status (overdue, paid, pending)
        overdue_only: Only include overdue debts
    
    Returns:
        Debt collection data with summary
    """
    filtered_data = MOCK_DEBT_DATA.copy()

    if overdue_only:
        filtered_data = [d for d in filtered_data if d["overdue_days"] > 0]
    elif status_filter:
        filtered_data = [d for d in filtered_data if d["status"] == status_filter]

    total_outstanding = sum(d["outstanding_amount"] for d in filtered_data)
    total_overdue_items = len([d for d in filtered_data if d["overdue_days"] > 0])
    avg_overdue_days = (
        sum(d["overdue_days"] for d in filtered_data) // len(filtered_data)
        if filtered_data
        else 0
    )

    return {
        "summary": {
            "total_outstanding": total_outstanding,
            "total_overdue_items": total_overdue_items,
            "avg_overdue_days": avg_overdue_days,
            "items_count": len(filtered_data),
        },
        "data": filtered_data,
        "status": status_filter or "all",
    }


def get_occupancy_report() -> Dict[str, Any]:
    """
    Get occupancy report.
    
    Returns:
        Occupancy data with breakdowns by floor and category
    """
    return {
        "summary": {
            "total_premises": MOCK_OCCUPANCY_DATA["total_premises"],
            "occupied": MOCK_OCCUPANCY_DATA["occupied"],
            "vacant": MOCK_OCCUPANCY_DATA["vacant"],
            "occupancy_rate": MOCK_OCCUPANCY_DATA["occupancy_rate"],
        },
        "by_floor": MOCK_OCCUPANCY_DATA["by_floor"],
        "by_category": MOCK_OCCUPANCY_DATA["by_category"],
        "timestamp": datetime.now().isoformat(),
    }


def get_kpi_dashboard() -> Dict[str, Any]:
    """
    Get KPI dashboard combining multiple metrics.
    
    Returns:
        KPI dashboard data
    """
    revenue = get_revenue_report()
    debt = get_debt_report()
    occupancy = get_occupancy_report()

    return {
        "timestamp": datetime.now().isoformat(),
        "key_metrics": {
            "current_month_revenue": revenue["data"][-1]["total_revenue"] if revenue["data"] else 0,
            "total_outstanding_debt": debt["summary"]["total_outstanding"],
            "occupancy_rate": occupancy["summary"]["occupancy_rate"],
            "overdue_items": debt["summary"]["total_overdue_items"],
        },
        "revenue": revenue,
        "debt": debt,
        "occupancy": occupancy,
    }
