from langchain.tools import tool

DEVICE_INFO = {
    "zynqmp": {
        "arch": "zynqmp",
        "bootloader": "FSBL",
        "output_format": ".bin",
        "components": ["fsbl", "pmu", "application", "bitstream"],
    },
    "versal": {
        "arch": "versal",
        "bootloader": "PLM",
        "output_format": [".bin", ".pdi"],
        "components": ["plm", "psmfw", "pmc"],
    }
}

@tool
def compare_devices(device1: str, device2: str) -> str:
    """
    当询问关于两个器件的区别或配置差异时使用这个工具。
    """
    result = ""

    if device1 not in DEVICE_INFO or device2 not in DEVICE_INFO:
        return "错误！没有找到器件。\n"
    result += f"{device1}:\n"
    for key, value in DEVICE_INFO[device1].items():
        result += f"{key}是{value}。\n"
    result += f"{device2}:\n"
    for key, value in DEVICE_INFO[device2].items():
        result += f"{key}是{value}。\n"
    return result