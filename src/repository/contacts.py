from typing import List, Any
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import or_, func

from src.database.models import Contact
from src.schemas.contacts import ContactBase, ContactUpdate


class ContactsRepository:

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_all(
        self,
        birthdays_within_days: int | None = None,
        search: str | None = None,
        skip: int | None = None,
        limit: int | None = None,
    ):
        stmt = select(Contact)

        if search is not None:
            stmt = stmt.filter(
                or_(
                    Contact.first_name.ilike(f"%{search}%"),
                    Contact.last_name.ilike(f"%{search}%"),
                    Contact.email.ilike(f"%{search}%"),
                )
            )

        if birthdays_within_days is not None:
            today = datetime.now().date()
            week = today + timedelta(days=birthdays_within_days)

            today_mmdd = today.strftime("%m-%d")
            week_mmdd = week.strftime("%m-%d")

            if today_mmdd <= week_mmdd:
                stmt = stmt.filter(
                    func.to_char(Contact.birthday, "MM-DD").between(
                        today_mmdd, week_mmdd
                    )
                )
            else:
                stmt = stmt.filter(
                    or_(
                        func.to_char(Contact.birthday, "MM-DD") >= today_mmdd,
                        func.to_char(Contact.birthday, "MM-DD") <= week_mmdd,
                    )
                )

        if skip is not None:
            stmt = stmt.offset(skip)
        if limit is not None:
            stmt = stmt.limit(limit)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_one_or_none(
        self,
        filters: List[Any] | None = None,
        order_by: Any = "id",
    ):
        return (
            await self.db.execute(select(Contact).filter(*filters).order_by(order_by))
        ).scalar_one_or_none()

    async def create(self, body: ContactBase):
        contact = Contact(**body.model_dump())
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update(self, contact_id: int, body: ContactUpdate):
        contact = await self.get_one_or_none(filters=[Contact.id == contact_id])

        if contact is None:
            return None

        for key, value in body.model_dump(exclude_unset=True).items():
            setattr(contact, key, value)

        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def delete(self, contact: Contact):
        await self.db.delete(contact)
        await self.db.commit()
        return contact
