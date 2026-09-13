from datetime import date

from sqlalchemy import Column, Date, Integer, MetaData, String, Table, create_engine, select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from ventes_lab.domain import Sale, summarize

metadata = MetaData()
sales_table = Table(
    "sales", metadata,
    Column("day", Date, primary_key=True),
    Column("shop", String(20), primary_key=True),
    Column("sale_id", String(64), primary_key=True),
    Column("quantity", Integer, nullable=False),
    Column("unit_price_cents", Integer, nullable=False),
)


class Storage:
    def __init__(self, url: str):
        kwargs = {"check_same_thread": False} if url.startswith("sqlite:") else {"connect_timeout": 3}
        self.engine = create_engine(url, connect_args=kwargs, pool_pre_ping=True)

    def initialize(self):
        metadata.create_all(self.engine)

    def ready(self):
        with self.engine.connect() as connection:
            connection.execute(text("SELECT 1"))

    def save(self, sales: list[Sale]) -> int:
        insert = sqlite_insert if self.engine.dialect.name == "sqlite" else pg_insert
        inserted = 0
        with self.engine.begin() as connection:
            for sale in sales:
                statement = insert(sales_table).values(**sale.model_dump())
                statement = statement.on_conflict_do_nothing(index_elements=["day", "shop", "sale_id"])
                inserted += connection.execute(statement).rowcount
        return inserted

    def summary(self, day: date) -> dict:
        with self.engine.connect() as connection:
            rows = connection.execute(select(sales_table).where(sales_table.c.day == day)).mappings().all()
        return {"day": day.isoformat(), **summarize([Sale.model_validate(dict(row)) for row in rows])}

    def close(self):
        self.engine.dispose()

