import argparse
import asyncio
import random
from datetime import date, time, timedelta

from sqlalchemy import select

from app.database import Base, async_session, engine
from app.models.activity import Activity
from app.models.earning import Earning
from app.models.expense import Expense
from app.models.user import User
from app.utils.auth import hash_password


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def create_user(email: str, password: str, name: str, is_admin: bool = False):
    await create_tables()
    async with async_session() as session:
        existing = await session.execute(select(User).where(User.email == email))
        if existing.scalar_one_or_none():
            print(f"User with email {email} already exists.")
            return
        user = User(
            email=email,
            hashed_password=hash_password(password),
            name=name,
            is_admin=is_admin,
        )
        session.add(user)
        await session.commit()
        print(f"User '{name}' ({email}) created successfully. Admin: {is_admin}")


async def seed_data(email: str, days: int = 60):
    """Generate realistic sample data for the given user."""
    await create_tables()
    async with async_session() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            print(f"User {email} not found. Create the user first.")
            return

        if not user.tax_percent:
            user.tax_percent = 23.0
            user.vehicle_name = "Toyota Corolla Hybrid"
            session.add(user)

        platforms = ["Uber", "Bolt", "Private", "FreeNow"]
        platform_weights = [0.45, 0.35, 0.12, 0.08]
        stations = ["Galp", "Repsol", "BP", "Cepsa", "Prio"]
        fuel_types = ["diesel", "gasoline"]
        maint_items = [
            "Oil change", "Tire rotation", "Brake pads", "Air filter",
            "Wiper blades", "Battery check", "Spark plugs",
        ]
        improvement_items = [
            "Phone mount", "Dashcam", "Seat covers", "Floor mats",
            "USB charger", "Air freshener set",
        ]
        operational_items = [
            "Car wash", "Interior cleaning", "Parking", "Tolls",
            "Cleaning supplies", "Water bottles",
        ]

        today = date.today()
        start_date = today - timedelta(days=days)
        current_km = 45000.0

        activities = []
        earnings = []
        expenses = []

        d = start_date
        while d <= today:
            if d.weekday() == 6:
                d += timedelta(days=1)
                continue

            is_short_day = random.random() < 0.2
            start_hour = random.randint(7, 10)
            work_hours = random.randint(4, 7) if is_short_day else random.randint(8, 12)
            end_hour = min(start_hour + work_hours, 23)

            daily_km = round(random.uniform(80, 200) if not is_short_day else random.uniform(40, 100), 1)
            end_km = current_km + daily_km

            activities.append(Activity(
                user_id=user.id,
                date=d,
                start_km=round(current_km, 1),
                end_km=round(end_km, 1),
                start_time=time(start_hour, random.choice([0, 15, 30, 45])),
                end_time=time(end_hour, random.choice([0, 15, 30, 45])),
            ))
            current_km = end_km

            num_platforms = random.choices([1, 2], weights=[0.4, 0.6])[0]
            chosen = random.choices(platforms, weights=platform_weights, k=num_platforms)
            chosen = list(set(chosen))
            for platform in chosen:
                base_earning = daily_km * random.uniform(0.5, 0.9) / len(chosen)
                tip = round(random.uniform(0, 5), 2) if random.random() < 0.3 else 0.0

                earnings.append(Earning(
                    user_id=user.id,
                    date=d,
                    platform=platform,
                    total_earnings=round(base_earning, 2),
                    tips=tip,
                    is_taxable=platform != "Private",
                ))

            if random.random() < 0.25:
                station = random.choice(stations)
                fuel = random.choice(fuel_types)
                ppu = round(random.uniform(1.45, 1.85), 3) if fuel != "electric" else round(random.uniform(0.20, 0.35), 3)
                qty = round(random.uniform(20, 50), 2)
                expenses.append(Expense(
                    user_id=user.id,
                    date=d,
                    category="fuel_charging",
                    amount=round(ppu * qty, 2),
                    station_name=station,
                    fuel_type=fuel,
                    price_per_unit=ppu,
                    quantity=qty,
                ))

            if random.random() < 0.04:
                item = random.choice(maint_items)
                expenses.append(Expense(
                    user_id=user.id,
                    date=d,
                    category="maintenance",
                    subcategory=item,
                    description=item,
                    amount=round(random.uniform(30, 250), 2),
                ))

            if random.random() < 0.02:
                item = random.choice(improvement_items)
                expenses.append(Expense(
                    user_id=user.id,
                    date=d,
                    category="improvements",
                    subcategory=item,
                    description=item,
                    amount=round(random.uniform(10, 80), 2),
                ))

            if random.random() < 0.15:
                item = random.choice(operational_items)
                expenses.append(Expense(
                    user_id=user.id,
                    date=d,
                    category="operational",
                    subcategory=item,
                    description=item,
                    amount=round(random.uniform(3, 25), 2),
                ))

            d += timedelta(days=1)

        session.add_all(activities + earnings + expenses)
        await session.commit()
        print(f"Seeded {len(activities)} activities, {len(earnings)} earnings, {len(expenses)} expenses for {email}")


def main():
    parser = argparse.ArgumentParser(description="TVDE Earnings Tracker CLI")
    sub = parser.add_subparsers(dest="command")

    create_cmd = sub.add_parser("create-user", help="Create a new user account")
    create_cmd.add_argument("--email", required=True)
    create_cmd.add_argument("--password", required=True)
    create_cmd.add_argument("--name", required=True)
    create_cmd.add_argument("--admin", action="store_true")

    sub.add_parser("init-db", help="Initialize the database tables")

    seed_cmd = sub.add_parser("seed", help="Generate sample data for a user")
    seed_cmd.add_argument("--email", required=True, help="User email to seed data for")
    seed_cmd.add_argument("--days", type=int, default=60, help="Number of days of data to generate")

    args = parser.parse_args()

    if args.command == "create-user":
        asyncio.run(create_user(args.email, args.password, args.name, args.admin))
    elif args.command == "init-db":
        asyncio.run(create_tables())
        print("Database tables created.")
    elif args.command == "seed":
        asyncio.run(seed_data(args.email, args.days))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
