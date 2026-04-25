# evaluator.py
from src.chain import ask

TEST_CASES = [
    {
        "question": "什么是 Bootgen 工具？",
        "answer": "Bootgen 是用于生成引导镜像（boot image）的工具，支持 AMD 的 Zynq、Zynq UltraScale+ 和 Versal 设备。",
        "keywords": ["引导镜像生成工具", "Boot image", "AMD", "Versal", "Zynq"],
    },
    {
        "question": "Bootgen 生成的输出文件是什么？",
        "answer": "Bootgen 生成的输出文件是引导镜像，例如 BOOT.BIN 或 Versal 设备使用的 PDI 文件。",
        "keywords": ["BOOT.BIN", "PDI", "引导镜像"],
    },
    {
        "question": "BIF 文件的主要作用是什么？",
        "answer": "BIF 文件用于描述引导镜像的内容和结构，包括分区及其顺序，是 Bootgen 的输入文件之一。",
        "keywords": ["Boot Image Format", "镜像描述", "分区定义"],
    },
    {
        "question": "Bootgen 支持哪些输入文件类型？",
        "answer": "Bootgen 支持多种输入文件类型，包括 ELF 文件、bitstream 文件、二进制文件以及其他数据文件。",
        "keywords": ["ELF", "bitstream", "binary", "data files"],
    },
    {
        "question": "如何在 BIF 文件中定义分区？",
        "answer": "在 BIF 文件中通过添加分区条目（partition entries）按顺序列出各个文件来定义分区。",
        "keywords": ["partition", "分区", "条目", "顺序"],
    },
    {
        "question": "Bootgen 如何处理加密和认证？",
        "answer": "Bootgen 支持对引导镜像进行加密和认证，通过在 BIF 文件中指定相关属性并使用密钥实现安全启动。",
        "keywords": ["encryption", "authentication", "密钥", "安全启动"],
    },
    {
        "question": "Bootgen 命令行的基本用法是什么？",
        "answer": "Bootgen 通常通过命令行使用，例如指定 -image 输入 BIF 文件、-arch 指定架构以及 -o 指定输出文件。",
        "keywords": ["bootgen", "-image", "-arch", "-o"],
    },
    {
        "question": "如何在 BIF 文件中指定启动设备？",
        "answer": "可以在 BIF 文件中通过相关配置项指定启动设备，以控制引导镜像的加载方式。",
        "keywords": ["boot device", "启动设备", "配置"],
    },
    {
        "question": "Bootgen 支持哪些架构？",
        "answer": "Bootgen 支持 Zynq、Zynq UltraScale+ 和 Versal 等架构。",
        "keywords": ["Zynq", "Zynq UltraScale+", "Versal"],
    },
    {
        "question": "BIF 文件中 attributes 的作用是什么？",
        "answer": "attributes 用于指定分区属性，例如加载地址、执行方式以及安全相关设置。",
        "keywords": ["attributes", "属性", "load", "execution"],
    }
]


def evaluate(chain) -> dict:
    """
    运行所有测试用例，返回评估报告
    """
    scores = {}
    for case in TEST_CASES:
        result = ask(chain, case["question"])
        found = len([word for word in case["keywords"] if word in result])
        num_keywords = len(case["keywords"])
        if __debug__:
            print(found, num_keywords) #for debug
        percentage = float(found)/num_keywords
        if __debug__:
            print(percentage) #for debug
        scores[case["question"]] = [result[:101], percentage]
    if __debug__:
        print(scores)
    return scores

def print_report(results: dict):
    """
    打印每道题的得分和整体准确率
    """
    total_score = 0.0
    for key,value in results.items():
        total_score += value[1]
        print(f"问题：{key};\n回答（仅显示前100字）：{value[0]};\n正确率：{value[1]}\n")
    print(f"平均正确率：{total_score/len(results)}\n")