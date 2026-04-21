# AI Deployment Learning Project

> 从零开始学习 AI 模型部署与 RAG 应用的个人项目，目标岗位：AI 应用工程师 / 推理优化工程师。

## 📁 项目结构
ai-deployment-project/
├── README.md # 项目说明
├── .gitignore # Git 忽略文件
├── A_W1D1.ipynb # 路径A：PyTorch MNIST 训练
├── A_W1D2.ipynb # 路径A：推理 + 可视化
├── A_W1D3.ipynb # 路径A：手写数字测试 + ONNX 导出
├── A_W1D4.ipynb # 路径A：ONNX Runtime 推理 + 速度对比
├── B_W1D1.ipynb # 路径B：RAG 概念 + 最简 Demo
├── B_W1D2.ipynb # 路径B：LangChain + Chroma + 检索
├── B_W1D3.ipynb # 路径B：完整 RAG（检索 + LLM 生成）
├── B_W1D4.ipynb # 路径B：Agent 入门 + Tool 调用
├── B_W1D5.ipynb # 路径B：Agent with Memory
├── mnist_model.pth # PyTorch 训练好的模型（已忽略）
├── mnist_model.onnx # ONNX 导出模型
├── data/ # MNIST 数据集（已忽略）
└── images/ # 图片文件


## 🚀 项目亮点

### 路径A：模型推理与部署优化
- ✅ 使用 PyTorch 训练 MNIST 手写数字识别模型，准确率 **97.8%**
- ✅ 实现单张图片推理与可视化
- ✅ 导出 ONNX 格式，使用 ONNX Runtime 推理
- ✅ 速度对比：ONNX Runtime GPU vs CPU，加速比 **1.56x**
- ✅ TensorRT FP16 量化（Google Colab），模型大小减少 **51%**

### 路径B：RAG 与 Agent
- ✅ 理解 RAG（检索增强生成）核心流程
- ✅ 使用 LangChain + Chroma + HuggingFace Embeddings 构建 RAG Demo
- ✅ 实验检索参数 `k` 对召回结果的影响
- ✅ 接入 DeepSeek API 完成完整 RAG 问答
- ✅ 理解 Agent 概念，实现 Tool Calling（加法、乘法、搜索）
- ✅ 实现带 Memory 的多轮对话 Agent

## 📊 关键结果

| 测试项 | 结果 |
|--------|------|
| PyTorch 推理速度（GPU） | 0.560 ms/张 |
| ONNX Runtime 推理速度（GPU） | 0.360 ms/张 |
| 加速比 | **1.56x** |
| ONNX → TensorRT FP16 模型大小 | 4.6MB → 2.4MB（**-51%**） |
| RAG 检索准确率 | 3个chunk独立检索 |
| Agent Memory | 支持多轮对话 |

## 🛠️ 环境要求

```bash
Python 3.8+
PyTorch 2.5.1
ONNX Runtime 1.20+
LangChain 1.0+

# 克隆仓库
git clone https://github.com/justin-zhong/ai-deployment-project.git
cd ai-deployment-project

# 安装依赖
pip install torch torchvision onnxruntime langchain langchain-openai

# 运行 Jupyter
jupyter lab

推理优化心得
小模型（如 MNIST）GPU 加速比不高，因为 GPU 启动开销占比大

大模型（如 ResNet50）GPU 加速比可达 10-50x

FP16 量化能有效减少模型大小和显存占用

RAG 调优心得
k 值太小会漏掉答案，太大会引入噪声

问题表述对检索质量影响巨大

需要在 prompt 中限制 LLM 只使用知识库内容

🔗 相关资源
PyTorch 官方教程

ONNX Runtime 文档

LangChain 文档

DeepSeek API

📧 联系我
GitHub: justin-zhong

Email: zhongchongyuan1999@gmail.com

持续更新中...