import datetime
import motor.motor_asyncio


class Database:

    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.col1 = self.db.banned

    def new_user(self, id):
        return dict(
            id=id,
            join_date=datetime.date.today().isoformat(),
            ban_status=dict(
                is_banned=False,
                ban_duration=0,
                banned_on=datetime.date.max.isoformat(),
                ban_reason=''
            )
        )

    async def add_user(self, id):
        user = self.new_user(id)
        await self.col.insert_one(user)

    async def is_user_exist(self, id):
        user = await self.col.find_one({'id': int(id)})
        return True if user else False

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        all_users = self.col.find({})
        return all_users

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def ban_user(self, user_id):
        await self.col1.update_one(
            {"id": user_id},
            {"$set": {"ban_status.is_banned": True}}
        )

    async def check_user(self, user_id):
        user = await self.col1.find_one({"id": user_id})
        return user

    async def unban_user(self, user_id):
        await self.col1.update_one(
            {"id": user_id},
            {"$set": {"ban_status.is_banned": False}}
        )

    async def update_ban(self, id):
        user = self.new_user(id)
        await self.col1.insert_one(user)

    async def is_user_banned(self, id):
        user = await self.col1.find_one({'id': int(id)})
        return True if user else False
