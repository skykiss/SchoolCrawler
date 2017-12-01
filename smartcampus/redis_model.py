import redis


class RedisModel:

    host = "115.159.182.201"
    port = "6379"
    pool = redis.ConnectionPool(host=host, port=port, decode_responses=True)
    r = redis.Redis(connection_pool=pool)

    @classmethod
    def add_record(cls, stu_id, jsessionid):
        cls.r.set(stu_id, jsessionid)
        cls.r.expire(stu_id, 900)

    @classmethod
    def get_record(cls, stu_id):
        jsessionid = cls.r.get(stu_id)
        cls.r.expire(stu_id, 3600)
        return jsessionid



