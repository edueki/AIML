from server import mcp
import rag_tool
import registration_tools
import payments_tool
import enrollment_tool
import email_tool
import discounts_tool
import courses_tool
import authentication_tool

import logging

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
