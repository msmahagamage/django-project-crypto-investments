from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Investment
from .forms import InvestmentForm
from django.db.models import Sum
from .crypto import to_cg_id, get_prices_usd_by_ids
from collections import defaultdict
from django.core.serializers.json import DjangoJSONEncoder
import json


def list_investments(request):
    qs = Investment.objects.all().order_by("-timestamp")

    # Build the set of CG ids from whatever is in .coin (name or symbol)
    cg_ids = []
    for s in Investment.objects.values_list("coin", flat=True).distinct():
        cid = to_cg_id(s)
        if cid:
            cg_ids.append(cid)

    prices = get_prices_usd_by_ids(cg_ids, ttl=60)  # {cg_id: {price, change_24h}}

    rows = []
    total_value = 0.0
    for inv in qs:
        cg_id = to_cg_id(inv.coin)
        payload = prices.get(cg_id, {})
        price = payload.get("price")
        change = payload.get("change_24h")
        value = (
            price * float(inv.quantity)
            if (price is not None and inv.quantity is not None)
            else None
        )
        if value is not None:
            total_value += value
        rows.append(
            {
                "id": inv.id,
                "coin": inv.coin,
                "quantity": inv.quantity,
                "timestamp": inv.timestamp,
                "price_usd": price,
                "value_usd": value,
                "change_24h": change,
            }
        )

    stats = {
        "count": qs.count(),
        "total_quantity": qs.aggregate(total=Sum("quantity"))["total"],
        "portfolio_value_usd": total_value if total_value else None,
    }

    # --- Aggregate by coin ---
    value_by_coin = defaultdict(float)
    qty_by_coin = defaultdict(float)

    for r in rows:
        coin = r["coin"] or "Unknown"
        if r["value_usd"] is not None:
            value_by_coin[coin] += float(r["value_usd"])
        if r["quantity"] is not None:
            qty_by_coin[coin] += float(r["quantity"])

    # Build chart payloads (skip empties)
    value_labels = list(value_by_coin.keys())
    value_series = [round(value_by_coin[c], 2) for c in value_labels]

    qty_labels = list(qty_by_coin.keys())
    qty_series = [round(qty_by_coin[c], 6) for c in qty_labels]

    chart_portfolio = {"labels": value_labels, "values": value_series}
    chart_quantity = {"labels": qty_labels, "values": qty_series}

    return render(
        request,
        "list.html",
        {
            "investments": rows,
            "stats": stats,
            # JSON for Chart.js (use json_script in template)
            "chart_portfolio": json.dumps(chart_portfolio, cls=DjangoJSONEncoder),
            "chart_quantity": json.dumps(chart_quantity, cls=DjangoJSONEncoder),
        },
    )
def create_investment(request):
    if request.method == "POST":
        form = InvestmentForm(request.POST)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f"Investment #{obj.pk} created.")
            return redirect("dashboard:detail", pk=obj.pk)
        messages.error(request, "Please fix the errors below.")
    else:
        form = InvestmentForm()
    return render(request, "create.html", {"form": form})


def investment_detail(request, pk):
    investment = get_object_or_404(Investment, pk=pk)
    return render(request, "detail.html", {"investment": investment})


def edit_investment(request, pk):
    investment = get_object_or_404(Investment, pk=pk)
    if request.method == "POST":
        form = InvestmentForm(request.POST, instance=investment)
        if form.is_valid():
            form.save()
            messages.success(request, f"Investment #{pk} updated.")
            return redirect("dashboard:detail", pk=pk)
        messages.error(request, "Please fix the errors below.")
    else:
        form = InvestmentForm(instance=investment)
    return render(request, "edit.html", {"form": form, "investment": investment})


def delete_investment(request, pk):
    investment = get_object_or_404(Investment, pk=pk)
    if request.method == "POST":
        investment.delete()
        messages.success(request, f"Investment #{pk} deleted.")
        return redirect("dashboard:list")
    # GET shows confirmation page
    return render(request, "delete_confirm.html", {"investment": investment})
