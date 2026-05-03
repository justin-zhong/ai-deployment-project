from tools.bif_generator import generate_bif
from tools.rag_tool import rag_search
from tools.device_comparator import compare_devices
from tools.command_validator import validate_command

from mcp.server.fastmcp import FastMCP
import json

mcp = FastMCP("AMD文档助手")

@mcp.tool()
def mcp_rag(query: str) -> str:
    return rag_search.invoke(query)

@mcp.tool()
def mcp_gen_bif(device: str, components: list) -> str:
        return generate_bif.invoke({
            "device": device,
            "components": components
        })

@mcp.tool()
def mcp_comp_devices(device1: str, device2: str) -> str:
    return compare_devices.invoke({
        "device1": device1, 
        "device2": device2
    })

@mcp.tool()
def mcp_val_cmd(commands: str) -> str:
    return validate_command.invoke(commands)

if __name__ == "__main__":
    mcp.run()