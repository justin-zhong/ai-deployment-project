from langchain.tools import tool

@tool
def generate_bif(device: str, components: list) -> str:
    """
    当询问关于BIF的问题时，使用这个工具来生成BIF。device的合法值为：versal, zynqmp。components可以为：fsbl, pmu, application, bitstream, plm, psmfw, pmc。
    """
    bif = ""
    is_zynqmp = False
    is_versal = False
    if device == "zynqmp":
        is_zynqmp = True
        bif += "the_ROM_image:\n{\n"
    elif device == "versal":
        is_versal = True
        bif += "all:\n{\n"
    else:
        raise ValueError("Invalid input provided")
    for component in components:
        match component:
            case s if "fsbl" in s:
                bif += "[bootloader, destination_cpu=a53-0] fsbl_a53.elf\n"
            case s if "pmu" in s:
                bif += "[pmufw_image] pmu_fw.elf\n"
            case s if "application" in s:
                bif += "[destination_cpu=a53-1] app_a53.elf\n"
            case s if "plm" in s:
                bif += "{type=bootloader, file=PLM.elf}\n"
            case s if "pmc" in s:
                bif += "{type=pmcdata, file=pmc_cdo.bin}\n"
            case _:
                raise ValueError("Invalid component")
    bif += "}\n"
    
    return bif