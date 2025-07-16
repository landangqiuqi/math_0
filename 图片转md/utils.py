import os
import glob
import requests
import json
from typing import List, Optional
import shutil
import datetime

class DeepSeekProcessor:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        
    def process_text_files(self, input_dir: str, output_dir: str, original_image_name: str = None) -> Optional[str]:
        """处理输入目录中的所有文本文件并保存结果到输出目录"""
        try:
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 读取并合并最新的两个txt文件内容
            txt_files = sorted(
                glob.glob(os.path.join(input_dir, "*.txt")),
                key=os.path.getmtime,
                reverse=True
            )[:2]  # 只取最新的两个文件
            
            if len(txt_files) < 2:
                print("需要两个文本文件进行处理")
                return None
                
            # 读取文件内容
            content1 = self._read_file_content(txt_files[0])
            content2 = self._read_file_content(txt_files[1])
            
            if not content1 or not content2:
                return None
                
            # 合并内容并添加说明
            combined_text = (
                "以下是图片识别的两个版本文本，请合并优化为规范的Markdown格式:\n\n"
                f"版本1(含公式):\n{content1}\n\n"
                f"版本2(不含公式):\n{content2}\n\n"
                "请将以上内容合并优化为:"
                "1. 结构清晰的Markdown文档"
                "2. 正确还原数学公式为LaTeX格式"
                "3. 修正识别错误的符号和术语"
                "4. 其他无关内容，你的想法都不要输出"
                "5.使用英语回答，内容的原文是英文"
            )
            
            # 调用DeepSeek API处理文本
            processed_text = self._call_deepseek_api(combined_text)
            if not processed_text:
                return None
                
            # 生成输出文件名
            if original_image_name:
                base_name = os.path.splitext(os.path.basename(original_image_name))[0]
                output_filename = f"{base_name}_processed.txt"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"processed_result_{timestamp}.txt"
                
            output_path = os.path.join(output_dir, output_filename)
            
            # 保存处理结果
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(processed_text)
                
            # 清空输入目录
            self._clear_input_directory(input_dir)
            
            return output_path
            
        except Exception as e:
            print(f"处理过程中发生错误: {str(e)}")
            return None
            
    def _read_file_content(self, file_path: str) -> Optional[str]:
        """读取单个文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            print(f"读取文件 {file_path} 时出错: {str(e)}")
            return None
        
    def _call_deepseek_api(self, text: str) -> Optional[str]:
        """调用DeepSeek API处理文本"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [{
                "role": "system",
                "content": "你是一个专业的文本整理助手，擅长将OCR识别结果修复为规范的Markdown格式，特别是数学公式部分。注意注意你的输出结果只要markdown部分，其他什么都不要输出"
            },{
                "role": "user", 
                "content": text
            }],
            "temperature": 0.3,
            "max_tokens": 4000
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"调用DeepSeek API失败: {str(e)}")
            return None
            
    def _clear_input_directory(self, input_dir: str):
        """清空输入目录"""
        for filename in os.listdir(input_dir):
            file_path = os.path.join(input_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"删除文件 {file_path} 时出错: {str(e)}")
