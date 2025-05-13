# BeyongSafeAnswer: A Benchmark for Evaluating True Risk Awareness in Large Reasoning Models

## 项目结构

```
BSA_OpenSource/
├── Batch_Call_LLM/       # 批量调用LLM的脚本和配置
│   ├── batch_zhipu_inference.py    # 智谱AI接口调用脚本
│   ├── batch_openai_inference.py   # OpenAI兼容接口调用脚本
│   ├── zhipuai_config.yaml         # 智谱AI配置文件
│   └── openai_config.yaml          # OpenAI兼容接口配置文件
├── Croissant/            # Croissant数据格式支持
│   ├── croissant.json    # Croissant元数据文件
│   └── data/             # 数据存储目录
├── Evaluation_Metric/    # 评估指标计算工具
│   ├── evaluate.py       # 评估脚本
│   └── README.md         # 评估模块说明
├── Prompt/               # 提示词模板集合
│   ├── Safe_Rules.md     # 安全规则提示词
│   ├── Thinking_Accuracy_Judge.md  # 思考准确性判断提示词
│   └── Safe_Ans_Judge.md # 安全回答判断提示词
└── requirements.txt      # 项目依赖
```

## 安装说明

1. 克隆项目仓库：
```bash
git clone [仓库URL]
cd BSA_OpenSource
```

2. 创建并激活虚拟环境：
```bash
conda create -n bsa_env python=3.10 -y
conda activate bsa_env
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

## 模块使用指南

### 批量调用LLM (Batch_Call_LLM)

支持两种调用方式：智谱AI接口和OpenAI兼容接口。两种方法都支持并发请求、自动重试、断点续传等功能。

有关评估指标的详细说明，请参阅`Batch_Call_LLM/README.md`。

#### 智谱AI接口使用方法：

1. 编辑`zhipuai_config.yaml`配置文件
2. 运行命令：
```bash
python Batch_Call_LLM/batch_zhipu_inference.py -c Batch_Call_LLM/zhipuai_config.yaml
```

#### OpenAI兼容接口使用方法：

1. 编辑`openai_config.yaml`配置文件
2. 运行命令：
```bash
python Batch_Call_LLM/batch_openai_inference.py -c Batch_Call_LLM/openai_config.yaml
```

### 评估指标计算 (Evaluation_Metric)

用于评估模型输出质量的工具，支持多种评估指标。

使用方法：
```bash
python Evaluation_Metric/evaluate.py [参数]
```

有关评估指标的详细说明，请参阅`Evaluation_Metric/README.md`。

### 提示词模板 (Prompt)

包含多种预设的提示词模板，可用于不同场景的LLM调用。主要模板包括：

- `Safe_Rules.md`：安全规则提示词
- `Thinking_Accuracy_Judge.md`：思考准确性判断提示词
- `Safe_Ans_Judge.md`：安全回答判断提示词

## 项目依赖

主要依赖包括：
- zhipuai：智谱AI官方SDK
- openai：OpenAI官方SDK
- pandas：数据处理
- pyyaml：配置文件解析
- tqdm：进度显示
- colorlog：彩色日志输出
- aiofiles：异步文件处理
- mlcroissant：Croissant数据格式支持

## 开源许可

本项目采用[知识共享署名-非商业性使用 4.0 国际许可协议（CC BY-NC 4.0）](https://creativecommons.org/licenses/by-nc/4.0/deed.zh)进行许可。

这意味着您可以：
- **共享**：在任何媒介以任何形式复制、发行本作品
- **演绎**：修改、转换或以本作品为基础进行创作

但必须遵循以下条件：
- **署名**：您必须给出适当的署名，提供指向本许可协议的链接，同时标明是否对原始作品作了修改
- **非商业性使用**：您不得将本作品用于商业目的

详细许可条款请参阅项目根目录下的LICENSE文件或访问：https://creativecommons.org/licenses/by-nc/4.0/legalcode.zh-Hans

## 贡献指南

[请在此处添加贡献指南] 