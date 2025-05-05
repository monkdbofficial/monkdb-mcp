# from .mcp_server import mcp
from mcp_monkdb.mcp_server import mcp


def main():
    mcp.run()


if __name__ == "__main__":
    main()
