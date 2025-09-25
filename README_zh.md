# 概述

<p align="center">
  <img src="image/title.png" width="800px"/>
</p>
<p align="center">
   🌐 <a href="https://openstellarteam.github.io/BSA/" target="_blank">网站</a> • 🤗 <a href="https://huggingface.co/datasets/OpenStellarTeam/BeyongSafeAnswer_Benchmark" target="_blank">Hugging Face</a> • ⏬ <a href="https://huggingface.co/datasets/OpenStellarTeam/BeyongSafeAnswer_Benchmark" target="_blank">数据</a> •   📃 <a href="https://arxiv.org/abs/2505.19690" target="_blank">论文</a> •   📊 <a href="https://openstellarteam.github.io/BSA_Leaderboard_Gitpage/" target="_blank">排行榜</a>  <br>  <a href="https://github.com/OpenStellarTeam/BSA/blob/main/README_zh.md">   中文</a> | <a href="https://github.com/OpenStellarTeam/BSA/blob/main/README.md">English</a> 
</p> 

Beyond Safe Answers 是一个创新性的基准数据集，旨在全面评估大型推理模型（LRMs）真实的风险意识，特别聚焦于模型内部的推理过程，而不仅仅关注表面输出。这一基准针对“表面安全对齐”（Superficial Safety Alignment, SSA）的关键问题进行设计，即模型虽然生成表面安全的回答，但在内部风险评估上存在不足，导致安全行为的不一致。

**Beyond Safe Answers 基准数据集的核心特点：**

* **详细的风险注释**：每个样本都配备了明确的风险注释，详细说明潜在风险，精确评估模型的推理深度。
* **全面的覆盖范围**：包含超过2,000个精心设计的样本，涵盖三种典型的SSA场景（过度敏感、认知捷径和风险遗漏），跨越9个主要风险类别，确保评估的多样性与广泛性。
* **具有挑战性的评估**：即使是表现最优的LRMs，在正确识别风险理由方面的准确性也仅为中等水平，凸显了基准的严格性与难度。
* **稳健的方法论**：采用严谨的人类注释、多重质量控制，并使用多个先进的LRMs进行验证，确保了数据的可靠性和有效性。
* **深刻的结论洞察**：验证了显式安全规则、高质量推理数据的微调，以及解码策略对缓解SSA的有效性有限。

---

**类别与场景：**

* **3种SSA场景**：包含过度敏感、认知捷径与风险遗漏。
* **9个主要风险类别**：涵盖了冒犯与偏见、特殊监管物品、财产侵权、隐私侵犯、身心健康、暴力与恐怖主义、伦理与道德、谣言和儿童色情等关键领域。

---

**Beyond Safe Answers 作为一项重要资源的价值：**

* 评估LRMs的内部推理一致性及其真实的风险识别能力。
* 识别和解决可能导致不安全结果的表面安全对齐问题。
* 为开发真正安全且具备风险意识的AI系统提供全面的评测工具。

这一基准显著推动了AI系统的安全性研究，确保系统真正安全并紧密贴合安全关键场景的要求。

---

<p align="center">
  <img src="image/category_en.png" width="700px"/>
</p>

## 💫 引言

* 近期，大量研究涌现，聚焦于评估大型推理模型（LRMs）的安全性，尤其强调模型推理过程与安全关键标准的对齐。尽管现有的一些基准测试能够评估响应层面的安全性，但它们往往忽略了更深层次的安全推理能力，这导致了一种被称为表面安全对齐（Superficial Safety Alignment, SSA）现象的出现。SSA 指的是 LRMs 尽管其内部推理未能准确检测和减轻潜在风险，却生成了表面上安全的响应。

* 为了系统地研究和解决 SSA 问题，我们引入了 **BeyondSafeAnswer Bench (BSA)** 数据集。这是一个全新的基准测试，包含超过2000个精心设计的实例，覆盖了3种不同的 SSA 场景：**过度敏感**、**认知捷径**和**风险遗漏**。该数据集全面涵盖了9个主要风险类别，如隐私、道德、暴力和财产侵权。

* BeyondSafeAnswer 数据集具有以下几个关键特性：

  * 🚩 **以风险为核心：** 专门设计用于严格测试模型真实的风险意识和推理深度，而非仅仅表面上遵守安全启发式规则。
  * 📑 **详尽标注：** 每个实例都包含详细的风险原因，明确捕捉了严格安全推理评估所需的复杂性和细微差别。
  * 🌐 **全面覆盖：** 包含跨多个风险领域的不同场景，为在各种安全关键上下文中进行基准测试提供了坚实的平台。
  * 🔍 **评估指标：** 包括明确定义的评估指标，如 Safe\@1、Think\@1、Safe\@k 和 Think\@k，以系统评估安全一致性和推理准确性。
  * 📈 **富有挑战性：** 旨在揭示当前 LRMs 的显著弱点，使其成为识别模型改进关键领域的理想工具。

* 我们使用23个最先进的 LRMs 进行的广泛评估揭示了几个关键发现：

  * 表现最好的模型在准确识别风险基本原理方面仍然能力有限，准确率仅为54.57%。
  * 许多 LRMs 在表面安全的输出与其潜在的推理能力之间表现出显著差异，凸显了 SSA 现象的普遍性。
  * 明确的安全指南和使用高质量推理数据进行的专门微调显著提高了 LRMs 减轻 SSA 的能力，尽管有时会以增加敏感性为代价。

通过 BeyondSafeAnswer 基准测试，我们的工作推动了开发真正具有风险意识、能够稳健处理微妙的安全关键场景的 LRMs 这一关键目标。


## SSA 样例
<p align="center">
  <img src="image/case.png" width="800px"/>
</p>


## 📊 Leaderboard

详细信息：  [📊](https://openstellarteam.github.io/BSA_Leaderboard_Gitpage/)

<p align="center">
  <img src="image/leader_board.png" width="800px"/>
</p>

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