import locust_base

class ApiUser(locust_base.IrohaLocust):
    host = locust_base.random.choice(["s1.tst.iroha.tech:50051","s2.tst.iroha.tech:50051","s3.tst.iroha.tech:50051","s4.tst.iroha.tech:50051"])
    min_wait = 1600
    max_wait = 2400
    task_set = locust_base.LivingNextDoorToMultiAlice