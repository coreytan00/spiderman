import os
from spacetime import Node
from utils.pcc_models import Register

def init(df, user_agent, fresh):
    reg = df.read_one(Register, user_agent)
    if not reg:
        reg = Register(user_agent, fresh)
        df.add_one(Register, reg)
        df.commit()
        df.push_await()
    while not reg.load_balancer:
        df.pull_await()
        if reg.invalid:
            raise RuntimeError("User agent string is not acceptable.")
        if reg.load_balancer:
            df.delete_one(Register, reg)
            df.commit()
            df.push()
    return reg.load_balancer

def get_cache_server(config, restart):
    print("get cache server runs")
    init_node = Node(
        init, Types=[Register], dataframe=(config.host, config.port))
    print("node created")
    print("restart: ", restart)
    print("config user agent: ", config.user_agent)
    print("config.save_file: ", config.save_file)
    print("os.path.exists: ", os.path.exists(config.save_file))
    print("restart or not os.path.exists(config.save_file):", restart or not os.path.exists(config.save_file))
    print("return value: ", init_node.start(config.user_agent, restart or not os.path.exists(config.save_file)))
    return init_node.start(
        config.user_agent, restart or not os.path.exists(config.save_file))