# Batch Large Language Model (LLM) Inference Scripts

## Overview

This project provides two methods for batch-calling LLM APIs: using the ZhipuAI SDK and using an OpenAI-compatible interface. Both methods share the following features:

- Support for concurrent requests (multithreading/async) to improve efficiency
- Automatic retry for failed requests
- Checkpointing for resumable processing
- Periodic checkpoint saving to prevent data loss
- Progress display and statistics

### ZhipuAI Method Features

- Uses the official ZhipuAI SDK
- Multithreaded concurrent processing
- Automatically extracts the reasoning process (content between `<think>...</think>` tags) and the final answer from model output

### OpenAI SDK Method Features

- Uses the standard OpenAI SDK
- Asynchronous concurrent processing
- Suitable for APIs compatible with the OpenAI interface

## Installation

### Method 1: Using an Environment File

```bash
# Create a conda environment
conda create -n llm_batch python=3.10 -y
conda activate llm_batch

# Install dependencies
pip install -r requirements.txt
```

### Method 2: Manual Installation

Install dependencies according to the script you use:

```bash
# ZhipuAI method dependencies
pip install zhipuai pandas pyyaml tqdm colorlog

# OpenAI SDK method dependencies
pip install openai pandas pyyaml tqdm colorlog aiofiles
```

## Prepare Input Data

Both methods use the same input data format: a CSV file that **must contain the columns `id` and `question`**:

```csv
id,question
1,"What is artificial intelligence?"
2,"How to learn Python programming?"
...
```

## Configuration

### ZhipuAI Method Configuration

Edit the `zhipuai_config.yaml` file:

```yaml
# ZhipuAI model configuration
model:
  api_key: "YOUR_ZHIPUAI_API_KEY"  # Required
  model_name: "glm-z1-airx"         # Required
  system_prompt: "You are an AI assistant"  # Optional
  temperature: 0.7                   # Optional
  top_p: 0.9                         # Optional
  max_tokens: 4096                   # Optional

runtime:
  max_concurrent: 5                  # Required
  retry_times: 3                     # Required
  retry_delay: 1                     # Seconds
  save_interval: 10                  # Save checkpoint every N items
  log_level: "INFO"                  # DEBUG, INFO, WARNING, ERROR, CRITICAL

io:
  input_file: "./data/questions.csv"     # Required
  output_file: "./data/results.csv"      # Required
  checkpoint_dir: "./checkpoints/"       # Required
```

### OpenAI SDK Method Configuration

Edit the `openai_config.yaml` file (previously called `doubao_infer.yaml`):

```yaml
# OpenAI API configuration
model:
  api_key: "YOUR_API_KEY"                # Replace with your API key
  base_url: "https://api.example.com/v1" # Base URL, modify as needed
  model_name: "model-name"               # Model name
  system_prompt: "You are an AI assistant..." # Optional
  temperature: 0.3                       # Optional
  top_p: 1.0                             # Optional
  top_k: 50                              # Optional, may not be supported by all APIs

runtime:
  max_concurrent: 5                      # Max concurrency
  retry_times: 3                         # Retry times
  retry_delay: 1                         # Retry interval (seconds)
  save_interval: 10                      # Save checkpoint every N items
  log_level: "INFO"                      # Log level

io:
  input_file: "./data/questions.csv"     # Input CSV file path
  output_file: "./data/results.csv"      # Output CSV file path
  checkpoint_dir: "./checkpoints/"       # Checkpoint directory
```

## Running the Scripts

### ZhipuAI Method

```bash
python batch_zhipu_inference.py -c zhipuai_config.yaml
```

Or use the default config file name:

```bash
python batch_zhipu_inference.py
```

### OpenAI SDK Method

```bash
python batch_openai_inference.py -c openai_config.yaml
```

Or use the default config file name:

```bash
python batch_openai_inference.py
```

Note: The current script file may still be named `batch_kimi_inference.py`.

## Parameter Description

### ZhipuAI Method Parameters

- `api_key`: ZhipuAI API key
- `model_name`: Model name (e.g., "glm-z1-airx")
- `system_prompt`: System prompt (optional)
- `temperature`: Controls output randomness (optional)
- `top_p`: Sampling parameter (optional)
- `max_tokens`: Maximum number of generated tokens (optional)

### OpenAI SDK Method Parameters

- `api_key`: API key
- `base_url`: API base URL
- `model_name`: Model name
- `system_prompt`: System prompt
- `temperature`: Controls output randomness
- `top_p`/`top_k`: Sampling parameters

### Common Runtime Parameters

- `max_concurrent`: Maximum concurrent requests
- `retry_times`: Number of retries for failures
- `retry_delay`: Retry interval (seconds)
- `save_interval`: Checkpoint save interval
- `log_level`: Log level

## Output Results

### ZhipuAI Method Output

The output CSV file contains the following columns:
- `id`: Question ID
- `question`: Original question
- `answer`: Final answer from the model (content after `</think>`)
- `reasoning_content`: Reasoning process (content between `<think>` and `</think>`)
- `status`: Status (success or failed)
- `tokens`: Number of tokens used
- `error`: Error message (if failed)

#### Reasoning Content Extraction

The script automatically extracts the reasoning process and final answer from the model's response:

1. If the response contains `<think>...</think>` tags:
   - `reasoning_content` is the content between the tags
   - `answer` is the content after `</think>`
2. If only `<think>` is present (no `</think>`):
   - `reasoning_content` is the content after `<think>`
   - `answer` is an empty string
3. If no tags are present:
   - `reasoning_content` is `None`
   - `answer` is the full response

### OpenAI SDK Method Output

The output CSV file contains the following columns:
- `id`: Question ID
- `question`: Original question
- `answer`: Model answer
- `reasoning_content`: If the model returns a `reasoning_content` field, it will be extracted (supported by some models)
- `status`: Status (success or failed)
- `tokens`: Number of tokens used
- `error`: Error message (if failed)

## Notes

- Make sure to configure the correct API key, model name, and base URL
- To avoid excessive requests, set concurrency according to your API limits
- For large-scale data, test with a small batch first to confirm your configuration
- ZhipuAI and OpenAI API parameters may differ; refer to their respective documentation for details 