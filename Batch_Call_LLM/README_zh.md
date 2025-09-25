# 大模型批量调用脚本

## 功能简介

该项目提供两种批量调用大模型API的方法：使用智谱AI SDK和使用OpenAI兼容接口。两种方法都具有以下特点：

- 支持并发调用（多线程/异步），提高处理效率
- 自动重试失败的请求
- 支持断点续传，可中断后继续处理
- 定期保存检查点，避免数据丢失
- 提供进度显示和统计信息

### 智谱AI方式特点

- 使用智谱AI官方SDK
- 多线程并发处理
- 自动提取模型输出中的思考过程（`<think>...</think>`标签之间的内容）和最终答案

### OpenAI SDK方式特点

- 使用标准OpenAI SDK
- 异步并发处理
- 适用于兼容OpenAI接口的API服务

## 安装依赖

### 方法一：使用环境文件

```bash
# 使用conda创建环境
conda create -n llm_batch python=3.10 -y
conda activate llm_batch

# 安装依赖包
pip install -r requirements.txt
```

### 方法二：手动安装依赖

根据您使用的脚本安装相应依赖：

```bash
# 智谱AI方式依赖
pip install zhipuai pandas pyyaml tqdm colorlog 

# OpenAI SDK方式依赖
pip install openai pandas pyyaml tqdm colorlog aiofiles
```

## 准备输入数据

两种方法使用相同的输入数据格式，为CSV文件，**必须包含`id`和`question`两列**：

```csv
id,question
1,"什么是人工智能？"
2,"如何学习Python编程？"
...
```

## 配置参数

### 智谱AI方式配置

编辑`zhipuai_config.yaml`文件：

```yaml
# 智谱AI模型配置
model:
  # 智谱AI API密钥（必需）
  api_key: "您的智谱AI API密钥"
  # 智谱AI模型名称（必需）
  model_name: "glm-z1-airx"
  # 系统提示词（可选）
  system_prompt: "你是人工智能助手"
  # 温度参数，控制生成文本的随机性（可选）
  temperature: 0.7
  # Top-p采样参数（可选）
  top_p: 0.9
  # 最大生成token数（可选）
  max_tokens: 4096

# 运行时配置
runtime:
  # 最大并发线程数（必需）
  max_concurrent: 5
  # 失败重试次数（必需）
  retry_times: 3
  # 重试间隔(秒)
  retry_delay: 1
  # 检查点保存间隔(处理多少条数据后保存一次)
  save_interval: 10
  # 日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL
  log_level: "INFO"

# 输入输出配置
io:
  # 输入CSV文件，必须包含id和question两列（必需）
  input_file: "./data/questions.csv"
  # 输出CSV文件路径（必需）
  output_file: "./data/results.csv"
  # 检查点目录（必需）
  checkpoint_dir: "./checkpoints/"
```

### OpenAI SDK方式配置

编辑`openai_config.yaml`文件（以前称为`doubao_infer.yaml`）：

```yaml
# OpenAI API配置
model:
  api_key: "YOUR_API_KEY"  # 在这里替换为你的API密钥
  base_url: "https://api.example.com/v1"  # API基础URL，根据实际服务提供商修改
  model_name: "model-name"  # 模型名称
  system_prompt: "你是一个人工智能助手..."  # 可选
  temperature: 0.3  # 可选
  top_p: 1.0  # 可选
  top_k: 50  # 可选，部分API可能不支持

# 运行时配置
runtime:
  max_concurrent: 5      # 最大并发数
  retry_times: 3         # 失败重试次数
  retry_delay: 1         # 重试间隔(秒)
  save_interval: 10      # 每处理多少条保存一次
  log_level: "INFO"      # 日志级别

# 输入输出配置
io:
  input_file: "./data/questions.csv"    # 输入CSV文件路径
  output_file: "./data/results.csv"     # 输出CSV文件路径
  checkpoint_dir: "./checkpoints/"      # 检查点保存目录
```

## 运行脚本

### 智谱AI方式

```bash
python batch_zhipu_inference.py -c zhipuai_config.yaml
```

或使用默认配置文件名称：

```bash
python batch_zhipu_inference.py
```

### OpenAI SDK方式

```bash
python batch_openai_inference.py -c openai_config.yaml
```

或使用默认配置文件名称：

```bash
python batch_openai_inference.py
```

注意：当前`batch_openai_inference.py`文件名可能仍为`batch_kimi_inference.py`。

## 参数说明

### 智谱AI方式参数

- `api_key`: 智谱AI API密钥
- `model_name`: 模型名称（如"glm-z1-airx"）
- `system_prompt`: 系统提示词（可选）
- `temperature`: 温度参数，控制输出随机性（可选）
- `top_p`: 采样参数（可选）
- `max_tokens`: 最大生成token数（可选）

### OpenAI SDK方式参数

- `api_key`: API密钥
- `base_url`: API基础URL
- `model_name`: 模型名称
- `system_prompt`: 系统提示词
- `temperature`: 温度参数，控制输出随机性
- `top_p`/`top_k`: 采样参数

### 共同的运行时参数

- `max_concurrent`: 最大并发请求数
- `retry_times`: 失败重试次数
- `retry_delay`: 重试间隔(秒)
- `save_interval`: 检查点保存间隔
- `log_level`: 日志级别

## 输出结果

### 智谱AI方式输出

输出CSV文件包含以下列：
- `id`: 问题ID
- `question`: 原问题
- `answer`: 模型最终回答（`</think>`之后的内容）
- `reasoning_content`: 模型思考过程（`<think>`和`</think>`之间的内容）
- `status`: 状态(success或failed)
- `tokens`: 消耗的token数量
- `error`: 错误信息(如果失败)

#### 思考内容提取说明

该脚本会自动从模型返回的内容中提取思考过程和最终答案：

1. 如果返回内容包含`<think>...</think>`标签，则：
   - `reasoning_content`为标签之间的内容
   - `answer`为`</think>`之后的内容

2. 如果仅有`<think>`但没有`</think>`标签，则：
   - `reasoning_content`为`<think>`之后的所有内容
   - `answer`为空字符串

3. 如果没有任何标签，则：
   - `reasoning_content`为`None`
   - `answer`为完整的返回内容

### OpenAI SDK方式输出

输出CSV文件包含以下列：
- `id`: 问题ID
- `question`: 原问题
- `answer`: 模型回答
- `reasoning_content`: 如果模型返回了reasoning_content字段，会被提取（部分模型支持）
- `status`: 状态(success或failed)
- `tokens`: 消耗的token数量
- `error`: 错误信息(如果失败)

## 注意事项

- 请确保配置了正确的API密钥、模型名称和基础URL
- 为避免请求过于频繁，建议根据您的API限制合理设置并发数
- 对于大量数据处理，建议先进行小规模测试，确认配置正确后再处理全部数据
- 智谱AI和OpenAI接口的参数可能有所不同，请参考各自的API文档进行配置 