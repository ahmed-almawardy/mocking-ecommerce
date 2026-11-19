"""Explicit CLI for promoting an existing, already-registered account to admin.

Usage: python -m app.admin_cli promote admin@example.com
Never expose this as a public API endpoint.
"""
import argparse
import asyncio

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models import User


async def promote(email: str) -> None:
    async with AsyncSessionLocal() as db:
        user = await db.scalar(select(User).where(User.email == email.strip().lower()))
        if not user:
            raise SystemExit(f"No account found for {email!r}. Register this account first.")
        user.role = "admin"
        await db.commit()
        print(f"Promoted {user.email} to administrator.")


async def main() -> None:
    parser = argparse.ArgumentParser(description="NOVA HOME administrator account management")
    sub = parser.add_subparsers(dest="command", required=True)
    promote_parser = sub.add_parser("promote", help="Promote an existing account to admin")
    promote_parser.add_argument("email")
    args = parser.parse_args()
    if args.command == "promote":
        await promote(args.email)


if __name__ == "__main__":
    asyncio.run(main())
