#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
批量调用Kimi大模型推理脚本
支持异步并发、错误重试和断点续传功能
"""

import os
import sys
import time
import json
import asyncio
import logging
import argparse
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path

import yaml
import pandas as pd
import aiofiles
from tqdm import tqdm
from colorlog import ColoredFormatter
from openai import AsyncOpenAI


class Config:
    """配置管理类，负责加载和验证配置"""
    
    def __init__(self, config_path: str):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = self._load_config()
        self._validate_config()
        
    def _load_config(self) -> Dict:
        """
        加载YAML配置文件
        
        Returns:
            配置字典
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            raise ValueError(f"加载配置文件失败: {e}")
    
    def _validate_config(self) -> None:
        """
        验证配置合法性
        """
        # 检查必要的配置项
        required_configs = [
            ('model', 'api_key'),
            ('model', 'base_url'),
            ('model', 'model_name'),
            ('runtime', 'max_concurrent'),
            ('runtime', 'retry_times'),
            ('io', 'input_file'),
            ('io', 'output_file'),
            ('io', 'checkpoint_dir')
        ]
        
        for section, key in required_configs:
            if section not in self.config:
                raise ValueError(f"配置文件缺少 '{section}' 部分")
            if key not in self.config[section]:
                raise ValueError(f"配置文件缺少 '{section}.{key}' 配置项")
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            section: 配置部分
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        if section not in self.config:
            return default
        if key not in self.config[section]:
            return default
        return self.config[section][key]
    
    @property
    def model_config(self) -> Dict:
        """获取模型配置"""
        return self.config.get('model', {})
    
    @property
    def runtime_config(self) -> Dict:
        """获取运行时配置"""
        return self.config.get('runtime', {})
    
    @property
    def io_config(self) -> Dict:
        """获取IO配置"""
        return self.config.get('io', {})


class LoggerSetup:
    """日志设置类"""
    
    @staticmethod
    def setup_logger(log_level: str = "INFO") -> logging.Logger:
        """
        设置彩色日志
        
        Args:
            log_level: 日志级别
            
        Returns:
            logger实例
        """
        log_levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        level = log_levels.get(log_level.upper(), logging.INFO)
        
        logger = logging.getLogger()
        logger.setLevel(level)
        
        # 清除已有的处理器
        for handler in logger.handlers:
            logger.removeHandler(handler)
            
        # 创建一个控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        
        # 设置彩色日志格式
        formatter = ColoredFormatter(
            "%(log_color)s%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white"
            }
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger


class CheckpointManager:
    """检查点管理类，负责保存和加载检查点"""
    
    def __init__(self, checkpoint_dir: str, save_interval: int = 10):
        """
        初始化检查点管理器
        
        Args:
            checkpoint_dir: 检查点目录
            save_interval: 保存间隔
        """
        self.checkpoint_dir = checkpoint_dir
        self.save_interval = save_interval
        self.checkpoint_file = os.path.join(checkpoint_dir, "checkpoint.json")
        self.temp_checkpoint_file = os.path.join(checkpoint_dir, "checkpoint_temp.json")
        self.lock = asyncio.Lock()
        
        # 确保检查点目录存在
        os.makedirs(checkpoint_dir, exist_ok=True)
        
    async def save_checkpoint(self, results: Dict) -> bool:
        """
        保存检查点 (线程安全)
        
        Args:
            results: 结果字典
            
        Returns:
            保存是否成功
        """
        async with self.lock: # <--- 获取锁
            try:
                # 先写入临时文件
                async with aiofiles.open(self.temp_checkpoint_file, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(results, ensure_ascii=False, indent=2))
                
                # 成功写入后，替换原文件 (这部分现在在锁的保护下是安全的)
                if os.path.exists(self.temp_checkpoint_file):
                    if os.path.exists(self.checkpoint_file):
                        os.remove(self.checkpoint_file)
                    os.rename(self.temp_checkpoint_file, self.checkpoint_file)
                    
                # 使用DEBUG级别避免在频繁保存时产生过多日志
                logging.debug(f"已保存检查点 (Processed: {results['metadata']['processed_count']})") 
                return True
            except Exception as e:
                logging.error(f"保存检查点失败: {e}")
                return False
            # 锁在退出 async with 块时自动释放
    
    def load_checkpoint(self) -> Optional[Dict]:
        """
        加载检查点
        
        Returns:
            检查点数据，如果不存在则返回None
        """
        if not os.path.exists(self.checkpoint_file):
            logging.info("未找到检查点文件，将从头开始处理")
            return None
        
        try:
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
                
            logging.info(f"成功加载检查点，已处理 {checkpoint_data['metadata']['processed_count']} 条数据")
            return checkpoint_data
        except Exception as e:
            logging.error(f"加载检查点失败: {e}")
            return None


class KimiCaller:
    """Kimi模型调用类，负责异步调用模型API"""
    
    def __init__(self, config: Dict):
        """
        初始化模型调用器
        
        Args:
            config: 模型配置
        """
        self.client = AsyncOpenAI(
            api_key=config["api_key"],
            base_url=config["base_url"]
        )
        self.model_config = config
        self.semaphore = asyncio.Semaphore(config.get("max_concurrent", 5))
        self.retry_times = config.get("retry_times", 3)
        self.retry_delay = config.get("retry_delay", 1)
        
    async def call_model(self, question_id: str, question: str) -> Dict:
        """
        调用模型API
        
        Args:
            question_id: 问题ID
            question: 问题文本
            
        Returns:
            API调用结果
        """
        logging.debug(f"ID {question_id} 开始尝试调用API")
        for attempt in range(self.retry_times + 1):
            try:
                async with self.semaphore:  # 使用信号量控制并发
                    logging.debug(f"ID {question_id} (尝试 {attempt+1}) 获取到信号量，开始请求")
                    start_time = time.time()
                    
                    messages = []
                    system_prompt_content = self.model_config.get("system_prompt")
                    if system_prompt_content:
                        messages.append({"role": "system", "content": system_prompt_content})
                    messages.append({"role": "user", "content": question})

                    api_params = {
                        "model": self.model_config["model_name"],
                        "messages": messages
                    }

                    temperature = self.model_config.get("temperature")
                    if temperature is not None:
                        api_params["temperature"] = temperature
                    
                    top_p = self.model_config.get("top_p")
                    if top_p is not None:
                        api_params["top_p"] = top_p

                    top_k = self.model_config.get("top_k")
                    if top_k is not None:
                        api_params["top_k"] = top_k
                                        
                    completion = await self.client.chat.completions.create(**api_params)
                    
                    answer = completion.choices[0].message.content
                    # 安全地获取 reasoning_content, 如果不存在则为 None
                    reasoning_content = getattr(completion.choices[0].message, 'reasoning_content', None)
                    tokens = completion.usage.total_tokens if hasattr(completion, 'usage') else 0
                    
                    result = {
                        "id": question_id,
                        "question": question,
                        "answer": answer,
                        "reasoning_content": reasoning_content,
                        "status": "success",
                        "tokens": tokens,
                        "time": time.time() - start_time
                    }
                    logging.debug(f"ID {question_id} (尝试 {attempt+1}) 请求成功")
                    return result
                    
            except Exception as e:
                error_msg = str(e)
                if attempt < self.retry_times:
                    logging.error(f"ID {question_id} 调用失败 (尝试 {attempt+1}/{self.retry_times+1}): {error_msg}")
                    await asyncio.sleep(self.retry_delay)
                else:
                    logging.error(f"ID {question_id} 所有重试失败: {error_msg}")
                    return {
                        "id": question_id,
                        "question": question,
                        "answer": None,
                        "reasoning_content": None,
                        "status": "failed",
                        "error": error_msg,
                        "tokens": 0,
                        "time": 0
                    }


class BatchProcessor:
    """批处理器，负责协调整个处理流程"""
    
    def __init__(self, config_path: str):
        """
        初始化批处理器
        
        Args:
            config_path: 配置文件路径
        """
        # 加载配置
        self.config = Config(config_path)
        
        # 设置日志
        log_level = self.config.get("runtime", "log_level", "INFO")
        self.logger = LoggerSetup.setup_logger(log_level)

        # 降低外部库的日志级别，避免过多 INFO 日志刷屏
        logging.getLogger("openai").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        
        # 初始化组件
        save_interval = self.config.get("runtime", "save_interval", 10)
        checkpoint_dir = self.config.get("io", "checkpoint_dir", "./checkpoints/")
        self.checkpoint_manager = CheckpointManager(checkpoint_dir, save_interval)
        
        model_config = self.config.model_config
        max_concurrent = self.config.get("runtime", "max_concurrent", 5)
        retry_times = self.config.get("runtime", "retry_times", 3)
        retry_delay = self.config.get("runtime", "retry_delay", 1)
        
        # 合并配置
        model_caller_config = {
            **model_config,
            "max_concurrent": max_concurrent,
            "retry_times": retry_times,
            "retry_delay": retry_delay
        }
        
        self.model_caller = KimiCaller(model_caller_config)
        self.results = None
    
    async def _init_results(self, total_count: int, input_file: str) -> Dict:
        """
        初始化结果数据结构
        
        Args:
            total_count: 总数据量
            input_file: 输入文件路径
            
        Returns:
            初始化的结果字典
        """
        return {
            "data": {},
            "metadata": {
                "last_id": None,
                "processed_count": 0,
                "total_count": total_count,
                "start_time": time.time(),
                "total_tokens": 0,
                "failed_ids": [],
                "input_file": input_file  # 添加输入文件路径
            }
        }
    
    async def process(self):
        """
        主处理流程
        """
        # 加载输入数据
        input_file = self.config.get("io", "input_file")
        if not os.path.exists(input_file):
            logging.error(f"输入文件不存在: {input_file}")
            return False
        
        df = pd.read_csv(input_file)
        if 'id' not in df.columns or 'question' not in df.columns:
            logging.error("输入CSV必须包含 'id' 和 'question' 列")
            return False
        
        total_count = len(df)
        logging.info(f"加载了 {total_count} 条数据")
        
        # 尝试加载检查点
        checkpoint_data = self.checkpoint_manager.load_checkpoint()
        processed_ids = set()
        
        if checkpoint_data:
            # 检查输入文件是否匹配
            checkpoint_input_file = checkpoint_data.get('metadata', {}).get('input_file')
            
            if checkpoint_input_file and os.path.abspath(checkpoint_input_file) != os.path.abspath(input_file):
                logging.warning(f"检查点文件与当前输入文件不匹配！")
                logging.warning(f"检查点文件: {checkpoint_input_file}")
                logging.warning(f"当前输入文件: {input_file}")
                logging.warning("将忽略现有检查点，从头开始处理新文件。")
                # 初始化结果
                self.results = await self._init_results(total_count, input_file)
            else:
                # 恢复已处理数据
                self.results = checkpoint_data
                processed_ids = set(self.results['data'].keys())
                
                # 更新元数据
                self.results['metadata']['total_count'] = total_count
                
                # 如果旧检查点没有记录输入文件，添加它
                if 'input_file' not in self.results['metadata']:
                    self.results['metadata']['input_file'] = input_file
                
                logging.info(f"从检查点恢复，跳过已处理的 {len(processed_ids)} 条数据")
        else:
            # 初始化结果
            self.results = await self._init_results(total_count, input_file)
        
        # 过滤出未处理的数据
        pending_df = df[~df['id'].astype(str).isin(processed_ids)]
        pending_count = len(pending_df)
        
        if pending_count == 0:
            logging.info("所有数据已处理完成")
            return True
        
        logging.info(f"开始处理剩余的 {pending_count} 条数据")
        
        # 开始异步处理
        tasks = []
        for _, row in pending_df.iterrows():
            task = asyncio.create_task(
                self.model_caller.call_model(str(row['id']), row['question'])
            )
            tasks.append(task)
        
        # 使用进度条处理结果
        with tqdm(total=pending_count, desc="处理进度") as pbar:
            for future in asyncio.as_completed(tasks):
                result = await future
                question_id = result['id']
                
                # 更新结果
                self.results['data'][question_id] = result
                self.results['metadata']['processed_count'] += 1
                self.results['metadata']['total_tokens'] += result.get('tokens', 0)
                self.results['metadata']['last_id'] = question_id
                
                if result['status'] == 'failed':
                    self.results['metadata']['failed_ids'].append(question_id)
                
                # 检查是否需要保存检查点
                save_interval = self.config.get("runtime", "save_interval", 10)
                if self.results['metadata']['processed_count'] % save_interval == 0:
                    await self.checkpoint_manager.save_checkpoint(self.results)
                
                pbar.update(1)
        
        # 最后再保存一次检查点
        await self.checkpoint_manager.save_checkpoint(self.results)
        
        # 保存最终结果到CSV
        await self.save_results()
        
        # 输出统计信息
        self.print_statistics()
        
        return True
    
    async def save_results(self):
        """保存结果到CSV文件"""
        output_file = self.config.get("io", "output_file")
        
        rows = []
        for item_id, item_data in self.results['data'].items():
            row = {
                'id': item_id,
                'question': item_data['question'],
                'answer': item_data.get('answer'), # 使用.get以防万一answer也是None
                'reasoning_content': item_data.get('reasoning_content'), # 新增字段
                'status': item_data['status'],
                'tokens': item_data.get('tokens', 0)
            }
            if item_data['status'] == 'failed' and 'error' in item_data:
                row['error'] = item_data['error']
            
            rows.append(row)
        
        result_df = pd.DataFrame(rows)
        
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # 定义列的顺序，确保新字段位置合理，并将error列放在最后
        columns_order = ['id', 'question', 'answer', 'reasoning_content', 'status', 'tokens', 'error']
        # 过滤掉DataFrame中实际不存在的列，以避免KeyError
        ordered_columns = [col for col in columns_order if col in result_df.columns]
        
        result_df = result_df[ordered_columns]
        result_df.to_csv(output_file, index=False, encoding='utf-8-sig') # 使用utf-8-sig确保Excel能正确打开中文
        logging.info(f"结果已保存到 {output_file}")
    
    def print_statistics(self):
        """打印统计信息"""
        if not self.results:
            return
        
        metadata = self.results['metadata']
        total_time = time.time() - metadata['start_time']
        success_count = metadata['processed_count'] - len(metadata['failed_ids'])
        
        logging.info("=" * 50)
        logging.info(f"处理完成:")
        logging.info(f"- 总数据: {metadata['total_count']}")
        logging.info(f"- 成功: {success_count}")
        logging.info(f"- 失败: {len(metadata['failed_ids'])}")
        logging.info(f"- 总Token: {metadata['total_tokens']}")
        logging.info(f"- 总耗时: {total_time:.2f}秒")
        logging.info("=" * 50)


async def main(config_path: str):
    """
    主入口函数
    
    Args:
        config_path: 配置文件路径
    """
    processor = BatchProcessor(config_path)
    await processor.process()


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="批量调用Kimi大模型推理脚本")
    parser.add_argument("-c", "--config", default="config.yaml", help="配置文件路径")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args.config)) 