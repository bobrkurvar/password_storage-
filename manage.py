import subprocess
import sys


PROD_PROJECT = "password-storage"
PROD_COMPOSE = "docker-compose.yml"
TEST_PROJECT = "tests"
TEST_COMPOSE = "docker-compose.test.yml"
IS_TEST = False


def run(cmd: list[str]) -> int:
    print(">", " ".join(cmd))
    return subprocess.call(cmd)

def run_or_exit(cmd):
    code = run(cmd)
    return code if code == 0 else sys.exit(code)

def compose_run(*args):
    return ["docker", "compose", "-p", TEST_PROJECT if IS_TEST else PROD_PROJECT, "-f", TEST_COMPOSE if IS_TEST else PROD_COMPOSE, *args]


def migrates_run():
    run_or_exit(compose_run("build", "migrate"))
    return run(compose_run("run", "--rm", "migrate"))

def scripts_run():
    run_or_exit(compose_run("build", "runner"))
    return run(compose_run("run", "--rm", "runner"))


def prod() -> int:
    migrates = input("run the migrates (y/n): ")
    if migrates.strip().lower() == "y":
        migrates_run()
    scripts = input("run the init scripts (y/n): ")
    if scripts.strip().lower() == "y":
        scripts_run()

    return run(compose_run("up", "--build"))

def down() -> int:
    return run(compose_run("down", "--remove-orphans"))

def down_with_volumes() -> int:
    return run(compose_run("down", "-v", "--remove-orphans"))


def logs():
    services = ["app", "bot"]
    outs = "|".join(services)
    out = input(f"[{outs}]: ")
    if out in services:
        return run(compose_run("logs", "-f", out))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python manage.py [prod|down|down_with_volumes|logs]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "prod":
        code = prod()
    elif cmd == "down":
        code = down()
    elif cmd == "down_with_volumes":
        code = down_with_volumes()
    elif cmd == "logs":
        code = logs()
    else:
        print(f"Unknown command: {cmd}")
        code = 1

    sys.exit(code)