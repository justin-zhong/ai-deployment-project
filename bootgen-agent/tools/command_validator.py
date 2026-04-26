from langchain.tools import tool

commands_to_check = ["-arch", "-image", "-o"]

@tool
def validate_command(commands: str) -> str:
    """
    当询问检查bootgen指令的语法时，使用这个工具来检查语法。
    """
    command_list = commands.split()
    command_list = command_list[1:]

    for item in commands_to_check:
        if item not in command_list:
            return f"错误：缺少{item}参数。\n"
        
    for command, val in zip(command_list[::2], command_list[1::2]):
        match command:
            case "-arch":
                if val not in ["zynqmp", "versal"]:
                    return f"错误：{command}参数值为{val}，不是合法值。\n"
            case "-image":
                if val.endswith(".bif") == False:
                    return f"错误：{command}参数值为{val}，不是合法值。\n"
            case "-o":
                if val.endswith(".bin") == False and val.endswith(".pdi") == False:
                    return f"错误：{command}参数值为{val}，不是合法值。\n"
    return "命令合法\n"
    