from psi_environment.environment import Environment

def hello_world():
    print("Hello, World!")
    env = Environment()
    while(env.is_running()):
        env.step(1)

if __name__ == "__main__":
    hello_world()