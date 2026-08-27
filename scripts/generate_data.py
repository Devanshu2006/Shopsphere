"""
ShopSphere data generator.

Generates realistic e-commerce data for the raw PostgreSQL database.

Usage:
    python generate_data.py --seed
    python generate_data.py --live --minutes 5
"""

import argparse
import random
import time
from datetime import datetime, timedelta

import psycopg2
from faker import Faker


fake = Faker()

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5432,
    "dbname": "shopsphere",
    "user": "shopsphere",
    "password": "shopsphere",
}

CATEGORIES = [
    "electronics",
    "home",
    "apparel",
    "beauty",
    "sports",
    "books",
]

SEGMENTS = [
    "regular",
    "vip",
    "churn_risk",
]

EVENT_TYPES = [
    "page_view",
    "add_to_cart",
    "checkout",
]


def get_conn():
    return psycopg2.connect(**DB_CONFIG)


def seed_products(cur, n=50):
    product_ids = []

    for _ in range(n):
        cur.execute(
            """
            INSERT INTO raw.products
                (sku, product_name, category, price)
            VALUES
                (%s, %s, %s, %s)
            RETURNING product_id
            """,
            (
                fake.unique.bothify(text="SKU-####??"),
                fake.catch_phrase(),
                random.choice(CATEGORIES),
                round(random.uniform(5, 500), 2),
            ),
        )

        product_ids.append(cur.fetchone()[0])

    return product_ids


def seed_customers(cur, n=200):
    customer_ids = []

    for _ in range(n):
        cur.execute(
            """
            INSERT INTO raw.customers
                (email, full_name, segment, signup_date)
            VALUES
                (%s, %s, %s, %s)
            RETURNING customer_id
            """,
            (
                fake.unique.email(),
                fake.name(),
                random.choices(
                    SEGMENTS,
                    weights=[0.7, 0.15, 0.15]
                )[0],
                fake.date_between(
                    start_date="-2y",
                    end_date="-30d"
                ),
            ),
        )

        customer_ids.append(cur.fetchone()[0])

    # Create a few duplicate-like customers
    for _ in range(int(n * 0.03)):
        base = fake.name()

        cur.execute(
            """
            INSERT INTO raw.customers
                (email, full_name, segment, signup_date)
            VALUES
                (%s, %s, %s, %s)
            RETURNING customer_id
            """,
            (
                fake.unique.email(),
                base,
                "regular",
                fake.date_between(
                    start_date="-1y",
                    end_date="-1d"
                ),
            ),
        )

        customer_ids.append(cur.fetchone()[0])

    return customer_ids


def seed_orders(cur, customer_ids, product_ids, n=1000):

    for _ in range(n):

        customer_id = random.choice(customer_ids)

        order_date = fake.date_time_between(
            start_date="-1y",
            end_date="now"
        )

        status = random.choices(
            ["completed", "cancelled", "refunded"],
            weights=[0.85, 0.10, 0.05]
        )[0]

        cur.execute(
            """
            INSERT INTO raw.orders
                (customer_id, order_date, status)
            VALUES
                (%s, %s, %s)
            RETURNING order_id
            """,
            (
                customer_id,
                order_date,
                status,
            ),
        )

        order_id = cur.fetchone()[0]

        for _ in range(random.randint(1, 4)):

            product_id = random.choice(product_ids)

            cur.execute(
                """
                INSERT INTO raw.order_items
                    (order_id, product_id, quantity, unit_price)
                SELECT
                    %s,
                    %s,
                    %s,
                    price
                FROM raw.products
                WHERE product_id = %s
                """,
                (
                    order_id,
                    product_id,
                    random.randint(1, 3),
                    product_id,
                ),
            )


def seed_events(cur, customer_ids, product_ids, n=3000):

    for _ in range(n):

        event_ts = fake.date_time_between(
            start_date="-30d",
            end_date="now"
        )

        cur.execute(
            """
            INSERT INTO raw.events
                (customer_id, event_type, product_id, event_ts)
            VALUES
                (%s, %s, %s, %s)
            """,
            (
                random.choice(customer_ids),
                random.choices(
                    EVENT_TYPES,
                    weights=[0.7, 0.2, 0.1]
                )[0],
                random.choice(product_ids),
                event_ts,
            ),
        )


def simulate_live_traffic(
    cur,
    customer_ids,
    product_ids,
    minutes
):

    end_time = datetime.now() + timedelta(
        minutes=minutes
    )

    print(
        f"Simulating live traffic until {end_time}..."
    )

    while datetime.now() < end_time:

        # Generate a new event
        cur.execute(
            """
            INSERT INTO raw.events
                (customer_id, event_type, product_id, event_ts)
            VALUES
                (%s, %s, %s, now())
            """,
            (
                random.choice(customer_ids),
                random.choices(
                    EVENT_TYPES,
                    weights=[0.7, 0.2, 0.1]
                )[0],
                random.choice(product_ids),
            ),
        )

        # Occasionally create an order
        if random.random() < 0.3:

            customer_id = random.choice(
                customer_ids
            )

            cur.execute(
                """
                INSERT INTO raw.orders
                    (customer_id, order_date, status)
                VALUES
                    (%s, now(), 'completed')
                RETURNING order_id
                """,
                (customer_id,),
            )

            order_id = cur.fetchone()[0]

            product_id = random.choice(
                product_ids
            )

            cur.execute(
                """
                INSERT INTO raw.order_items
                    (order_id, product_id, quantity, unit_price)
                SELECT
                    %s,
                    %s,
                    %s,
                    price
                FROM raw.products
                WHERE product_id = %s
                """,
                (
                    order_id,
                    product_id,
                    random.randint(1, 2),
                    product_id,
                ),
            )

        # Occasionally change customer segment
        if random.random() < 0.05:

            customer_id = random.choice(
                customer_ids
            )

            new_segment = random.choice(
                SEGMENTS
            )

            cur.execute(
                """
                UPDATE raw.customers
                SET
                    segment = %s,
                    updated_at = now()
                WHERE customer_id = %s
                """,
                (
                    new_segment,
                    customer_id,
                ),
            )

            print(
                f"Customer {customer_id} "
                f"-> segment changed to {new_segment}"
            )

        time.sleep(1)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--seed",
        action="store_true",
        help="Run initial seed"
    )

    parser.add_argument(
        "--live",
        action="store_true",
        help="Simulate live traffic"
    )

    parser.add_argument(
        "--minutes",
        type=int,
        default=5,
        help="Minutes to simulate"
    )

    args = parser.parse_args()

    conn = get_conn()

    conn.autocommit = True

    cur = conn.cursor()

    if args.seed or not args.live:

        print("Seeding products...")

        product_ids = seed_products(cur)

        print("Seeding customers...")

        customer_ids = seed_customers(cur)

        print("Seeding orders...")

        seed_orders(
            cur,
            customer_ids,
            product_ids
        )

        print("Seeding events...")

        seed_events(
            cur,
            customer_ids,
            product_ids
        )

        print("Seed complete.")

    else:

        cur.execute(
            "SELECT customer_id FROM raw.customers"
        )

        customer_ids = [
            row[0]
            for row in cur.fetchall()
        ]

        cur.execute(
            "SELECT product_id FROM raw.products"
        )

        product_ids = [
            row[0]
            for row in cur.fetchall()
        ]

    if args.live:

        cur.execute(
            "SELECT customer_id FROM raw.customers"
        )

        customer_ids = [
            row[0]
            for row in cur.fetchall()
        ]

        cur.execute(
            "SELECT product_id FROM raw.products"
        )

        product_ids = [
            row[0]
            for row in cur.fetchall()
        ]

        simulate_live_traffic(
            cur,
            customer_ids,
            product_ids,
            args.minutes
        )

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()