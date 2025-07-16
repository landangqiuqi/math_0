# -*- coding: utf-8 -*-
"""
Created on Tue Jul  8 21:33:40 2025

@author: thats
"""
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import tkinter as tk
from tkinter import filedialog, messagebox
from pix2text import Pix2Text
from datetime import datetime
import json
from pix2text import TextFormulaOCR
import pix2text



class LaTeXOCRApp:
    def __init__(self, master):
        self.master = master
        master.title("LaTeX-OCR 识别工具")
        master.geometry("600x400")  # 稍微增大窗口尺寸
        
        # 设置UI风格
        self.setup_ui()
        
        # 初始化OCR引擎（显示加载状态）
        self.result_label.config(text="正在初始化OCR引擎...", fg="blue")
        self.master.update()
        
        try:
            self.p2t = Pix2Text(
                enable_formula=False,
                text_ocr_config={
                    'model_name': 'english_gb',  # 强制使用英文模型
                    'rec_model_name': 'en_PP-OCRv3',  # PaddleOCR 英文识别模型
                    'det_model_name': 'en_PP-OCRv3_det',  # 英文检测模型
                    'lang': 'en'  # 显式指定语言
                    }
                )




            self.result_label.config(text="OCR引擎已就绪，请选择图片", fg="green")
        except Exception as e:
            self.result_label.config(text=f"引擎初始化失败: {str(e)}", fg="red")
            messagebox.showerror("初始化错误", f"无法加载OCR引擎:\n{str(e)}")
            self.select_btn.config(state=tk.DISABLED)

    def setup_ui(self):
        """设置用户界面"""
        # 主标题
        self.label = tk.Label(self.master, text="图片转LaTeX工具", 
                            font=('Arial', 14, 'bold'))
        self.label.pack(pady=15)
        
        # 副标题
        self.sub_label = tk.Label(self.master, text="支持识别文本和数学公式", 
                                font=('Arial', 10))
        self.sub_label.pack()
        
        # 选择按钮
        self.select_btn = tk.Button(self.master, text="选择图片", 
                                   command=self.select_image, 
                                   height=2, width=20,
                                   font=('Arial', 10),
                                   bg="#4CAF50", fg="white")
        self.select_btn.pack(pady=20)
        
        # 结果标签
        self.result_label = tk.Label(self.master, text="", 
                                    font=('Arial', 10), 
                                    wraplength=500, justify=tk.LEFT)
        self.result_label.pack(pady=10)
        
        # 状态栏
        self.status_bar = tk.Label(self.master, text="就绪", bd=1, 
                                 relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def select_image(self, file_path=None):
        """选择并处理图片"""
        if not file_path:
            file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            self.status_bar.config(text="已取消选择")
            return
            
        self.status_bar.config(text="处理中...")
        self.result_label.config(text="正在识别图片...", fg="blue")
        self.master.update()
        
        try:
            # 验证图片文件
            if not os.path.isfile(file_path):
                raise ValueError("文件不存在或不可读")
                
            if os.path.getsize(file_path) == 0:
                raise ValueError("文件为空")
            
            # 执行识别
            result = self.p2t.recognize(file_path)
            
            # 处理不同格式的结果
            if isinstance(result, str):
                # 尝试解析可能返回的JSON字符串
                try:
                    result = json.loads(result)
                    combined_text = result.get('text', '')
                except json.JSONDecodeError:
                    combined_text = result
            elif isinstance(result, dict):
                combined_text = result.get('text', '')
            else:
                combined_text = str(result)
            
            # 确保有识别结果
            if not combined_text.strip():
                raise ValueError("未识别到有效内容")
            
            # 生成输出路径
            output_dir = r"D:\workspace2025\python机器学习\图片转模型\pic2txt"
            os.makedirs(output_dir, exist_ok=True)
            
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(output_dir, f"{base_name}_识别结果_{timestamp}.txt")
            
            # 保存结果
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(combined_text)
            
            # 显示成功信息
            success_msg = f"识别成功！结果已保存到:\n{output_path}"


            self.result_label.config(text=success_msg, fg="green")
            self.status_bar.config(text="识别完成")
            
            # 提供打开文件选项
            if messagebox.askyesno("完成", f"{success_msg}\n\n是否要打开结果文件？"):
                os.startfile(output_path)
                
        except Exception as e:
            error_msg = f"识别失败: {str(e)}"
            self.result_label.config(text=error_msg, fg="red")
            self.status_bar.config(text="识别失败")
            messagebox.showerror("错误", error_msg)
            
            # 如果是模型相关错误，尝试重新初始化
            if "model" in str(e).lower() or "load" in str(e).lower():
                self.retry_initialize_engine()

    def retry_initialize_engine(self):
        """尝试重新初始化OCR引擎"""
        answer = messagebox.askyesno("引擎错误", "OCR引擎出现问题，是否尝试重新初始化？")
        if answer:
            try:
                self.result_label.config(text="正在重新初始化OCR引擎...", fg="blue")
                self.master.update()
                
                self.p2t = Pix2Text.from_config(enable_formula=True)
                self.result_label.config(text="OCR引擎已重新初始化，请重试", fg="green")
                self.select_btn.config(state=tk.NORMAL)
            except Exception as e:
                self.result_label.config(text=f"重新初始化失败: {str(e)}", fg="red")
                self.select_btn.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    try:
        print("Pix2Text版本:", pix2text.__version__)  # 需要 >=1.0

        app = LaTeXOCRApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("致命错误", f"应用程序崩溃:\n{str(e)}")
