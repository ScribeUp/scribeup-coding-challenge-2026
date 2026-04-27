"""Seed the database with realistic transaction data.

Generates ~5,000 transactions across ~50 users with a mix of:
- Real recurring subscriptions (monthly, yearly, weekly).
- Subscriptions with quirks: price changes, free trials, cancellations,
  amount variability, merchant name variations.
- Near-recurring noise (same merchant, irregular cadence).
- One-off retail/food purchases.

Deterministic — seed is fixed so all candidates see the same data.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from django.core.management.base import BaseCommand

from subscriptions.models import Transaction


SEED = 42
NUM_USERS = 50
WINDOW_DAYS = 400  # ~13 months of history


@dataclass
class SubscriptionPlan:
    merchant: str
    amount: float
    cadence_days: int
    amount_jitter: float = 0.0       # +/- absolute dollars of noise
    name_variants: tuple = ()        # alternate merchant strings
    price_change: tuple = None       # (after_n_charges, new_amount)
    cancel_after: int = None         # cancel after N charges
    free_trial: bool = False         # first charge is $0
    one_off: bool = False            # not actually recurring


MONTHLY_SUBS = [
    SubscriptionPlan("Netflix", 15.99, 30, name_variants=("NETFLIX.COM", "Netflix Inc")),
    SubscriptionPlan("Spotify", 11.99, 30),
    SubscriptionPlan("Hulu", 17.99, 30, price_change=(4, 18.99)),
    SubscriptionPlan("Disney+", 13.99, 30),
    SubscriptionPlan("HBO Max", 15.99, 30, name_variants=("Max", "HBO MAX")),
    SubscriptionPlan("Apple iCloud", 2.99, 30),
    SubscriptionPlan("Google One", 9.99, 30),
    SubscriptionPlan("Equinox", 250.00, 30),
    SubscriptionPlan("Planet Fitness", 24.99, 30),
    SubscriptionPlan("ChatGPT Plus", 20.00, 30),
    SubscriptionPlan("Claude Pro", 20.00, 30),
    SubscriptionPlan("AWS", 87.50, 30, amount_jitter=35.0),  # variable usage
    SubscriptionPlan("DoorDash DashPass", 9.99, 30, free_trial=True),
    SubscriptionPlan("Uber One", 9.99, 30),
    SubscriptionPlan("NYT Cooking", 5.00, 30, cancel_after=5),
    SubscriptionPlan("Patreon", 8.00, 30),
    SubscriptionPlan("Audible", 14.95, 30),
    SubscriptionPlan("Peloton", 44.00, 30),
    SubscriptionPlan("LinkedIn Premium", 39.99, 30),
    SubscriptionPlan("1Password", 4.99, 30),
]

WEEKLY_SUBS = [
    SubscriptionPlan("Blue Apron", 89.00, 7, amount_jitter=10.0),
    SubscriptionPlan("HelloFresh", 75.00, 7, cancel_after=8),
    SubscriptionPlan("NYT Subscription", 4.00, 7),
]

YEARLY_SUBS = [
    SubscriptionPlan("Amazon Prime", 139.00, 365),
    SubscriptionPlan("GitHub Copilot", 100.00, 365),
    SubscriptionPlan("Namecheap", 12.99, 365),
    SubscriptionPlan("Costco Membership", 60.00, 365),
]

ONE_OFF_MERCHANTS = [
    ("Amazon", 8, 200),
    ("Whole Foods", 30, 150),
    ("Trader Joe's", 20, 90),
    ("Starbucks", 4, 25),
    ("Chipotle", 10, 35),
    ("Target", 15, 250),
    ("Walgreens", 5, 60),
    ("Uber", 8, 60),
    ("Lyft", 8, 60),
    ("Shell", 30, 90),
    ("Delta", 200, 800),
    ("Airbnb", 150, 1200),
    ("Apple Store", 50, 1500),
    ("Best Buy", 30, 800),
    ("REI", 40, 400),
    ("Home Depot", 20, 500),
    ("CVS", 8, 80),
    ("Sweetgreen", 14, 22),
    ("Nike", 60, 250),
    ("Etsy", 15, 120),
]

# Merchants that look subscription-ish but aren't — same merchant, irregular dates.
NEAR_RECURRING_MERCHANTS = [
    ("Spotify", 11.99),    # gift cards, irregular reloads
    ("Apple Store", 9.99),  # in-app purchases
    ("Steam", 19.99),
]


class Command(BaseCommand):
    help = "Seed the database with realistic transaction data."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Delete existing transactions first")

    def handle(self, *args, **options):
        rng = random.Random(SEED)

        if options["reset"]:
            count = Transaction.objects.count()
            Transaction.objects.all().delete()
            self.stdout.write(f"Deleted {count} existing transactions.")

        if Transaction.objects.exists():
            self.stdout.write(self.style.WARNING(
                "Transactions already exist. Use --reset to start fresh."
            ))
            return

        end = datetime.now(timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0)
        start = end - timedelta(days=WINDOW_DAYS)

        all_txns: list[Transaction] = []

        for user_id in range(1, NUM_USERS + 1):
            user_txns = self._build_user(user_id, rng, start, end)
            all_txns.extend(user_txns)

        rng.shuffle(all_txns)
        Transaction.objects.bulk_create(all_txns, batch_size=1000)

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(all_txns)} transactions across {NUM_USERS} users."
        ))

    def _build_user(self, user_id, rng, start, end):
        txns: list[Transaction] = []

        # Pick subscription mix.
        n_monthly = rng.randint(1, 5)
        n_weekly = rng.choices([0, 1, 2], weights=[6, 3, 1])[0]
        n_yearly = rng.choices([0, 1, 2], weights=[5, 4, 1])[0]

        chosen_monthly = rng.sample(MONTHLY_SUBS, k=min(n_monthly, len(MONTHLY_SUBS)))
        chosen_weekly = rng.sample(WEEKLY_SUBS, k=min(n_weekly, len(WEEKLY_SUBS)))
        chosen_yearly = rng.sample(YEARLY_SUBS, k=min(n_yearly, len(YEARLY_SUBS)))

        for plan in chosen_monthly + chosen_weekly + chosen_yearly:
            txns.extend(self._emit_subscription(user_id, plan, rng, start, end))

        # Near-recurring noise (one merchant per user, occasionally).
        if rng.random() < 0.4:
            merchant, base_amount = rng.choice(NEAR_RECURRING_MERCHANTS)
            n = rng.randint(2, 5)
            for _ in range(n):
                offset = rng.randint(0, (end - start).days)
                charged_at = start + timedelta(days=offset, hours=rng.randint(0, 23))
                amount = round(base_amount * rng.uniform(0.5, 1.8), 2)
                txns.append(self._make_txn(user_id, merchant, amount, charged_at, rng))

        # One-off purchases.
        n_oneoff = rng.randint(20, 80)
        for _ in range(n_oneoff):
            merchant, low, high = rng.choice(ONE_OFF_MERCHANTS)
            amount = round(rng.uniform(low, high), 2)
            offset = rng.randint(0, (end - start).days)
            charged_at = start + timedelta(days=offset, hours=rng.randint(0, 23))
            txns.append(self._make_txn(user_id, merchant, amount, charged_at, rng))

        return txns

    def _emit_subscription(self, user_id, plan, rng, start, end):
        txns = []
        # Random offset into the cadence so subs don't all start on the same day.
        first = start + timedelta(days=rng.randint(0, plan.cadence_days))
        current = first
        i = 0

        while current <= end:
            if plan.cancel_after is not None and i >= plan.cancel_after:
                break

            amount = plan.amount
            if plan.price_change and i >= plan.price_change[0]:
                amount = plan.price_change[1]
            if plan.amount_jitter:
                amount = max(0.5, amount + rng.uniform(-plan.amount_jitter, plan.amount_jitter))
            if plan.free_trial and i == 0:
                amount = 0.0

            merchant = plan.merchant
            if plan.name_variants and rng.random() < 0.25:
                merchant = rng.choice(plan.name_variants)

            # Slight day-of jitter (some merchants charge 1-2 days early/late).
            jitter = timedelta(days=rng.randint(-2, 2)) if plan.cadence_days >= 28 else timedelta(0)
            charged_at = current + jitter

            txns.append(self._make_txn(
                user_id,
                merchant,
                round(amount, 2),
                charged_at,
                rng,
            ))

            current += timedelta(days=plan.cadence_days)
            i += 1

        return txns

    def _make_txn(self, user_id, merchant, amount, charged_at, rng):
        # Realistic-ish metadata a bank feed might include. Intentionally does
        # NOT label transactions as subscription/one-off/etc — that's the
        # candidate's job to figure out.
        payload = {
            "tx_ref": f"TX-{rng.randint(100000, 999999):06d}",
            "mcc": rng.choice(["5814", "5411", "5311", "5812", "5912", "5499", "4900", "7372"]),
            "channel": rng.choice(["card_present", "card_not_present", "ach"]),
            "memo": f"{merchant.upper()} #{rng.randint(1000, 9999)}",
        }
        return Transaction(
            user_id=user_id,
            merchant_name=merchant,
            amount=Decimal(str(amount)),
            charged_at=charged_at,
            raw_payload=payload,
        )
