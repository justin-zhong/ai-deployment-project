#!/usr/bin/env python
# coding: utf-8

# In[1]:


import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
import torchvision.transforms as transforms
import time
import numpy as np
from typing import List, Tuple, Dict
import matplotlib.pyplot as plt


# In[2]:


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.dropout1 = nn.Dropout(0.25)
        self.dropout2 = nn.Dropout(0.5)
        self.fc1 = nn.Linear(9216, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.conv1(x)
        x = F.relu(x)
        x = self.conv2(x)
        x = F.relu(x)
        x = F.max_pool2d(x, 2)
        x = self.dropout1(x)
        x = torch.flatten(x, 1)
        x = self.fc1(x)
        x = F.relu(x)
        x = self.dropout2(x)
        x = self.fc2(x)
        return F.log_softmax(x, dim=1)


# In[96]:


class ImagePreprocessor:
    def __init__(self):
        self.mean = 0.1307
        self.std = 0.3081

    def preprocess(self, image_path: str) -> torch.Tensor:
        """
        预处理单张图片

        步骤：
        1. 打开图片，转灰度
        2. 缩放到 28x28
        3. 转 Tensor
        4. 归一化
        5. 添加 batch 维度

        Returns:
            torch.Tensor: shape (1, 1, 28, 28)
        """
        # TODO: 自己实现预处理逻辑
        # 1. 打开图片，转灰度
        # print(image_path)
        img = Image.open(image_path)
        grayscale_img = img.convert('L')

        # 2. 缩放到 28x28
        resized_img = grayscale_img.resize((28, 28))
        # img.show(resized_img)

        # 3. 转 Tensor
        transform = transforms.ToTensor()
        tensor_img = transform(resized_img)
        # print(tensor_img)

        # 4. 归一化
        norm_tensor_img = (tensor_img - self.mean) / self.std

        # 5. 添加 batch 维度
        add_dim_tensor_img = torch.unsqueeze(norm_tensor_img, 0)

        return add_dim_tensor_img

    def preprocess_batch(self, image_paths: List[str]) -> torch.Tensor:
        """
        批量预处理多张图片

        Returns:
            torch.Tensor: shape (N, 1, 28, 28)
        """
        # TODO: 自己实现批量预处理
        tensors = [self.preprocess(path) for path in image_paths]
        return torch.cat(tensors, dim=0)


# In[97]:


# 临时测试代码（放在文件末尾）
preprocessor = ImagePreprocessor()
tensor = preprocessor.preprocess("my_digit.png")
# print(tensor)
print(f"预处理后 shape: {tensor.shape}")  # 应该是 (1, 1, 28, 28)


# In[115]:


# ============ 推理引擎 ============
class InferenceEngine:
    """推理引擎类"""

    def __init__(self, model_path: str, device: str = "cuda"):
        """
        初始化推理引擎

        Args:
            model_path: 模型文件路径 (.pth)
            device: 运行设备 ("cuda" 或 "cpu")
        """
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.preprocessor = ImagePreprocessor()

        # TODO: 加载模型
        # 1. 创建模型实例
        self.model = Net()

        # 2. 加载权重
        state_dict = torch.load(model_path, weights_only=True)
        self.model.load_state_dict(state_dict)

        # 3. 移动到设备
        self.model.to(self.device)

        # 4. 设置为评估模式
        self.model.eval()

    def predict(self, image_path: str) -> int:
        """
        单张图片推理

        Args:
            image_path: 图片路径

        Returns:
            预测的数字 (0-9)
        """
        # TODO: 自己实现单张推理
        preprocessor = self.preprocessor
        tensor = preprocessor.preprocess(image_path)
        with torch.no_grad():
            tensor = tensor.to(self.device)
            output = self.model(tensor)
        #print(torch.argmax(output, dim=1)[0])
        return torch.argmax(output, dim=1)[0]

    def predict_batch(self, image_paths: List[str], batch_size: int = 32) -> List[int]:
        """
        批量推理

        Args:
            image_paths: 图片路径列表
            batch_size: 批次大小

        Returns:
            预测结果列表
        """
        # TODO: 自己实现批量推理
        # 提示：分批处理，避免内存溢出
        results = []
        for i in range(0, len(image_paths), batch_size):
            batch_paths = image_paths[i:i+batch_size]
            # 批量预处理
            batch_tensors = self.preprocessor.preprocess_batch(batch_paths)
            batch_tensors = batch_tensors.to(self.device)
            # 批量推理
            with torch.inference_mode():
                outputs = self.model(batch_tensors)
                batch_results = torch.argmax(outputs, dim=1).cpu().tolist()
            results.extend(batch_results)
        return results

    def benchmark(self, image_path: str, num_runs: int = 100) -> Dict[str, float]:
        """
        性能测试

        Args:
            image_path: 测试图片
            num_runs: 运行次数

        Returns:
            包含 p50, p95, p99, mean 延迟的字典
        """
        # TODO: 自己实现性能测试
        # 提示：
        # 1. 预热 10 次
        tensor = self.preprocessor.preprocess(image_path).to(self.device)
        for i in range(10):
            with torch.inference_mode():
                self.model(tensor)
        # 2. 记录 num_runs 次推理时间
        times = []

        for i in range(num_runs):
            start_time = time.perf_counter()
            # print(image_path)
            with torch.inference_mode():
                result = self.model(tensor)
            end_time = time.perf_counter()
            times.append((end_time - start_time) * 1000)
        # 3. 计算 P50, P95, P99, mean
        p50 = np.percentile(times, 50)
        p95 = np.percentile(times, 95)
        p99 = np.percentile(times, 99)
        mean = np.mean(times)

        print(f"Min: {min(times):.3f} ms, Max: {max(times):.3f} ms")

        return {
        'mean': mean,
        'p50': p50,
        'p95': p95,
        'p99': p99,
    }


# In[116]:


# 临时测试代码
engine = InferenceEngine("mnist_model.pth")
result = engine.predict("my_digit.png")
print(f"预测结果: {result}")


# In[117]:


# ============ 测试代码 ============
if __name__ == "__main__":
    print("=" * 50)
    print("推理引擎测试")
    print("=" * 50)

    # 1. 初始化引擎
    print("\n1. 初始化推理引擎...")
    engine = InferenceEngine("mnist_model.pth")
    print(f"   设备: {engine.device}")

    # 2. 单张推理
    print("\n2. 单张图片推理...")
    result = engine.predict("my_digit.png")
    print(f"   预测结果: {result}")

    # 3. 批量推理
    print("\n3. 批量推理（10张，同一张图）...")
    test_images = ["my_digit.png"] * 10
    results = engine.predict_batch(test_images, batch_size=4)
    print(f"   批量结果: {results}")

    # 4. 性能测试
    print("\n4. 性能测试（100次）...")
    stats = engine.benchmark("my_digit.png", num_runs=100)
    print(f"   平均延迟: {stats['mean']:.3f} ms")
    print(f"   P50: {stats['p50']:.3f} ms")
    print(f"   P95: {stats['p95']:.3f} ms")
    print(f"   P99: {stats['p99']:.3f} ms")

    print("\n✅ 测试完成！")

