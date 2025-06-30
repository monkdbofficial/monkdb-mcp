from mcp_monkdb.mcp_server import mcp
from mcp_monkdb.otel_setup import configure_otel


def main():
    configure_otel(mcp.app)
    mcp.run()


if __name__ == "__main__":
    main()
