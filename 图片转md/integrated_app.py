import os
import tkinter as tk
import time
import gc
import psutil
import threading
from tkinter import filedialog, messagebox
from pic2txt import LaTeXOCRApp
from utils import DeepSeekProcessor
from datetime import datetime

class IntegratedOCRApp:
    def __init__(self, master):
        self.master = master
        master.title("图片转模型整合工具")
        master.geometry("800x600")
        
        # 初始化DeepSeek处理器
        self.deepseek_processor = DeepSeekProcessor(
            api_key="sk-c3b9d4aca1544ee4982a5e14010dd120"  # 替换为你的API密钥
        )
        
        # 设置UI
        self.setup_ui()
        
        # 确保必要的目录存在
        self.ensure_directories()
        
    def ensure_directories(self):
        """确保必要的目录存在"""
        os.makedirs("pic2txt", exist_ok=True)
        os.makedirs("output", exist_ok=True)
        
    def setup_ui(self):
        """设置用户界面"""
        # 主标题
        self.title_label = tk.Label(
            self.master, 
            text="图片转模型整合工具", 
            font=('Arial', 16, 'bold')
        )
        self.title_label.pack(pady=20)
        
        # 图片选择按钮
        self.select_btn = tk.Button(
            self.master,
            text="选择单张图片处理",
            command=self.start_processing,
            height=2,
            width=30,
            font=('Arial', 12),
            bg="#4CAF50",
            fg="white"
        )
        self.select_btn.pack(pady=10)
        
        # 批量处理按钮
        self.batch_btn = tk.Button(
            self.master,
            text="批量处理图片",
            command=self.start_batch_processing,
            height=2,
            width=30,
            font=('Arial', 12),
            bg="#2196F3",
            fg="white"
        )
        self.batch_btn.pack(pady=10)
        
        # 进度标签
        self.progress_label = tk.Label(
            self.master,
            text="就绪",
            font=('Arial', 10),
            fg="blue"
        )
        self.progress_label.pack(pady=10)
        
        # 结果文本框
        self.result_text = tk.Text(
            self.master,
            height=20,
            width=80,
            wrap=tk.WORD,
            font=('Arial', 10)
        )
        self.result_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = tk.Scrollbar(self.result_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.result_text.yview)
        
        # 内存监控按钮和显示
        self.memory_frame = tk.Frame(self.master)
        self.memory_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.memory_btn = tk.Button(
            self.memory_frame,
            text="显示内存使用",
            command=self.show_memory_usage,
            width=15
        )
        self.memory_btn.pack(side=tk.LEFT, padx=5)
        
        self.memory_label = tk.Label(
            self.memory_frame,
            text="内存: 0MB",
            width=20,
            anchor=tk.W
        )
        self.memory_label.pack(side=tk.LEFT)
        
        # 状态栏
        self.status_bar = tk.Label(
            self.master,
            text="就绪",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 启动内存监控
        self.update_memory_usage()
    
    def start_batch_processing(self):
        """开始批量处理流程"""
        file_paths = filedialog.askopenfilenames(
            title="选择多个图片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp"), ("所有文件", "*.*")]
        )
        
        if not file_paths:
            self.update_status("已取消选择")
            return
            
        # 禁用按钮防止重复点击
        self.batch_btn.config(state=tk.DISABLED)
        
        # 在新线程中处理，避免阻塞UI
        processing_thread = threading.Thread(
            target=self.process_images_sequentially,
            args=(file_paths,),
            daemon=True
        )
        processing_thread.start()
        
    def start_processing(self):
        """开始处理流程"""
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            self.update_status("已取消选择")
            return
            
        # 禁用按钮防止重复点击
        self.select_btn.config(state=tk.DISABLED)
        
        # 在新线程中处理，避免阻塞UI
        processing_thread = threading.Thread(
            target=self.process_image,
            args=(file_path,),
            daemon=True
        )
        processing_thread.start()
    
    def process_image(self, image_path):
        """处理图片的完整流程"""
        try:
            # 在主线程中创建Tkinter窗口
            self.master.after(0, lambda: self.update_progress("正在初始化OCR处理..."))
            
            # 在主线程中创建OCR应用
            root = tk.Tk()
            root.withdraw()
            ocr_app = LaTeXOCRApp(root)
            
            # 处理图片(在主线程中执行)
            self.master.after(0, lambda: self.update_progress("正在处理图片(双模式)..."))
            ocr_app.select_image(image_path)
            
            # 使用事件循环检查处理状态
            def check_processing():
                try:
                    if len(os.listdir("pic2txt")) >= 2:
                        # 处理完成后的逻辑
                        self.update_progress("正在调用DeepSeek API处理文本...")
                        result_path = self.deepseek_processor.process_text_files(
                            "pic2txt",
                            "output",
                            image_path
                        )
                        if result_path:
                            with open(result_path, 'r', encoding='utf-8') as f:
                                result_content = f.read()
                            self.update_result(result_content)
                            self.update_progress(f"处理完成！结果已保存到: {result_path}")
                            self.update_status("处理成功")
                        else:
                            self.update_progress("处理失败，请查看错误信息")
                            self.update_status("处理失败")
                    else:
                        if hasattr(gc, 'collect'):
                            gc.collect()
                        self.master.after(500, check_processing)
                except Exception as e:
                    err_msg = f"处理错误: {e}"  # 使用局部变量
                    print(f"检查处理状态时出错: {err_msg}")
                    def _update_error():
                        self.update_progress(err_msg)
                    self.master.after(0, _update_error)
            
            self.master.after(0, check_processing)
                
            self.update_progress("正在调用DeepSeek API处理文本...")
            result_path = self.deepseek_processor.process_text_files(
                "pic2txt",
                "output",
                image_path  # 传入原始图片路径用于生成输出文件名
            )
            
            if result_path:
                with open(result_path, 'r', encoding='utf-8') as f:
                    result_content = f.read()
                
                self.update_result(result_content)
                self.update_progress(f"处理完成！结果已保存到: {result_path}")
                self.update_status("处理成功")
            else:
                self.update_progress("处理失败，请查看错误信息")
                self.update_status("处理失败")
                
        except Exception as e:
            self.update_progress(f"处理过程中发生错误: {str(e)}")
            self.update_status("处理失败")
            messagebox.showerror("错误", f"处理失败:\n{str(e)}")
            
        finally:
            # 显式清理资源
            if ocr_app:
                try:
                    if hasattr(ocr_app, 'p2t_formula'):
                        del ocr_app.p2t_formula
                    if hasattr(ocr_app, 'p2t_text'):
                        del ocr_app.p2t_text
                    del ocr_app
                except Exception as e:
                    print(f"清理OCR应用时出错: {str(e)}")
            
            if root:
                try:
                    root.destroy()
                except Exception as e:
                    print(f"销毁窗口时出错: {str(e)}")
            
            # 强制垃圾回收
            if hasattr(gc, 'collect'):
                gc.collect()
            
            self.master.after(0, lambda: self.select_btn.config(state=tk.NORMAL))
    

        
    def update_progress(self, message):
        """更新进度信息(线程安全)"""
        def _update():
            self.progress_label.config(text=message)
            self.progress_label.update_idletasks()
        self.master.after(0, _update)
        
    def update_result(self, content):
        """更新结果文本框(线程安全)"""
        def _update():
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, content)
            self.result_text.see(tk.END)
            self.result_text.update_idletasks()
        self.master.after(0, _update)
        
    def process_images_sequentially(self, file_paths):
        """顺序处理多个图片"""
        try:
            total = len(file_paths)
            for i, file_path in enumerate(file_paths, 1):
                self.update_progress(f"正在处理图片 {i}/{total}")
                self.update_status(f"处理中 {i}/{total}")
                
                # 清空临时文件夹
                self.clear_pic2txt_folder()
                
                # 处理当前图片
                self.process_image(file_path)
                
                # 等待处理完成
                while len(os.listdir("output")) < i:
                    time.sleep(0.5)
            
            self.update_progress(f"批量处理完成！共处理 {total} 张图片")
            self.update_status("批量处理完成")
            
        except Exception as e:
            self.update_progress(f"批量处理过程中发生错误: {str(e)}")
            self.update_status("批量处理失败")
            messagebox.showerror("错误", f"批量处理失败:\n{str(e)}")
            
        finally:
            self.master.after(0, lambda: self.batch_btn.config(state=tk.NORMAL))
    
    def clear_pic2txt_folder(self):
        """清空pic2txt文件夹"""
        for filename in os.listdir("pic2txt"):
            file_path = os.path.join("pic2txt", filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"删除文件 {file_path} 时出错: {str(e)}")

    def update_status(self, message):
        """更新状态栏"""
        self.master.after(0, lambda: self.status_bar.config(text=message))
        
    def show_memory_usage(self):
        """显示当前内存使用情况"""
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        mem_mb = mem_info.rss / (1024 * 1024)
        self.memory_label.config(text=f"内存: {mem_mb:.2f}MB")
        
    def update_memory_usage(self):
        """定时更新内存使用显示"""
        self.show_memory_usage()
        self.master.after(1000, self.update_memory_usage)  # 每秒更新一次

if __name__ == "__main__":
    root = tk.Tk()
    app = IntegratedOCRApp(root)
    root.mainloop()
