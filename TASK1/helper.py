import redis, os


def sent_in_redis(branch_name, data, db):
    try:
        r = redis.StrictRedis(host=os.getenv("REDIS_HOST"), port=6379, db=db)
        r.mset({branch_name: str(data)})
        r.expire(branch_name, 604800)
        r.close()
    except redis.RedisError as e:
        print(e)


def get_in_redis(branch_name,db):
    try:
        r=redis.StrictRedis(host=os.getenv("REDIS_HOST"), port=6379, db=db)
        branch = r.get(branch_name)
        r.close()
        return branch
    except redis.RedisError as e:
        print(e)
