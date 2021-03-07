"""


async def init_connection(db_uri):
    """ connect to db with async GinoORM """
    await db.set_bind(db_uri)
    return db

import asyncpg
async def drop_and_recreate_all_tables():
    """ use this function if you want re-init the table"""
    db = await init_connection("postgresql://local:local@localhost:5432/kkr_metadata")
    models = [Languages, Users,]
    # drop&create tables
    for model_id in models:
        sql_query = f"DROP TABLE {model_id.__tablename__} CASCADE"
        try:
            await db.status(db.text(sql_query))
        except asyncpg.exceptions.UndefinedTableError:
            # if table not exist just ignore it
            pass

async def main():
    db = await init_connection("postgresql://local:local@localhost:5432/kkr_metadata")
    
    await db.gino.create_all()
    await Users.create(name='Ia')
    print((await Users.get(1)).to_dict())
    await Users.create(name='Hi')
    print((await Users.get()).to_dict())
    
import asyncio
loop = asyncio.get_event_loop()
loop.run_until_complete(main())


"""