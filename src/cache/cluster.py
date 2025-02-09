from rediscluster import RedisCluster

cluster = RedisCluster(
    startup_nodes=[
        {"host": "redis-node1", "port": 7000},
        {"host": "redis-node2", "port": 7001}
    ],
    decode_responses=False,
    password="SECRET"
) 