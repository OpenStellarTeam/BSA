# BeyongSafeAnswer: A Benchmark for Evaluating True Risk Awareness in Large Reasoning Models


## Project Structure

```
BSA_OpenSource/
├── Batch_Call_LLM/       # Scripts and configurations for batch calling LLMs
│   ├── batch_zhipu_inference.py    # ZhipuAI interface call script
│   ├── batch_openai_inference.py   # OpenAI-compatible interface call script
│   ├── zhipuai_config.yaml         # ZhipuAI configuration file
│   └── openai_config.yaml          # OpenAI-compatible interface configuration file
├── Croissant/            # Croissant data format support
│   ├── croissant.json    # Croissant metadata file
│   └── data/             # Data storage directory
├── Evaluation_Metric/    # Evaluation metric calculation tools
│   ├── evaluate.py       # Evaluation script
│   └── README.md         # Evaluation module documentation
├── Prompt/               # Collection of prompt templates
│   ├── Safe_Rules.md     # Safety rules prompts
│   ├── Thinking_Accuracy_Judge.md  # Thinking accuracy judgment prompts
│   └── Safe_Ans_Judge.md # Safe answer judgment prompts
└── requirements.txt      # Project dependencies
```

## Installation

1. Clone the project repository:
```bash
git clone [Repository URL]
cd BSA_OpenSource
```

2. Create and activate a virtual environment:
```bash
conda create -n bsa_env python=3.10 -y
conda activate bsa_env
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Module Usage Guide

### Batch Calling LLMs (Batch_Call_LLM)

Supports two calling methods: ZhipuAI interface and OpenAI-compatible interface. Both methods support concurrent requests, automatic retries, resumable processing, etc.

For detailed information on this module, please refer to `Batch_Call_LLM/README.md`.

#### ZhipuAI Interface Usage:

1. Edit the `zhipuai_config.yaml` configuration file.
2. Run the command:
```bash
python Batch_Call_LLM/batch_zhipu_inference.py -c Batch_Call_LLM/zhipuai_config.yaml
```

#### OpenAI-Compatible Interface Usage:

1. Edit the `openai_config.yaml` configuration file.
2. Run the command:
```bash
python Batch_Call_LLM/batch_openai_inference.py -c Batch_Call_LLM/openai_config.yaml
```

### Evaluation Metric Calculation (Evaluation_Metric)

Tools for evaluating model output quality, supporting various evaluation metrics.

Usage:
```bash
python Evaluation_Metric/evaluate.py [parameters]
```

For detailed information on evaluation metrics, please refer to `Evaluation_Metric/README.md`.

### Prompt Templates (Prompt)

Contains a variety of preset prompt templates for different LLM calling scenarios. Main templates include:

- `Safe_Rules.md`: Safety rules prompts
- `Thinking_Accuracy_Judge.md`: Thinking accuracy judgment prompts
- `Safe_Ans_Judge.md`: Safe answer judgment prompts

## Project Dependencies

Main dependencies include:
- zhipuai: Official ZhipuAI SDK
- openai: Official OpenAI SDK
- pandas: Data processing
- pyyaml: Configuration file parsing
- tqdm: Progress display
- colorlog: Colored log output
- aiofiles: Asynchronous file handling
- mlcroissant: Croissant data format support

## Open Source License

This project is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/).

This means you are free to:
- **Share**: copy and redistribute the material in any medium or format
- **Adapt**: remix, transform, and build upon the material

Under the following conditions:
- **Attribution**: You must give appropriate credit, provide a link to the license, and indicate if changes were made.
- **NonCommercial**: You may not use the material for commercial purposes.

For detailed license terms, please refer to the LICENSE file in the project root directory or visit: https://creativecommons.org/licenses/by-nc/4.0/legalcode

## Contribution Guidelines

[Please add contribution guidelines here] 