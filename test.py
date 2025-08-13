import uiautomator2 as u2
from fastmcp import FastMCP
from fastmcp.utilities.types import Image
import xml.etree.ElementTree as ET
import json
import io
import subprocess
import re

mcp = FastMCP("Android Mobile MCP Server")
device = u2.connect()
