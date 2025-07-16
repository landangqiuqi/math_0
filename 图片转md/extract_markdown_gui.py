import os
import re
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import psutil

class MarkdownExtractorApp:
    def __init__(self, master):
        self.master = master
        master.title("Markdown内容提取工具")
        master.geometry("600x400")
        
        # 初始化路径
        self.input_dir = "d:/workspace2025/python机器学习/图片转模型/output"
        self.output_dir = "d:/workspace2025/python机器学习/图片转模型/readable"
        self.copy_dir = "d:/workspace2025/python机器学习/图片转模型/copy"
        
        # 创建必要的目录
        self.create_dirs()
        
        # 设置UI
        self.setup_ui()
        
        # 内存监控
        self.memory_label = tk.Label(master, text="内存: 0MB")
        self.memory_label.pack(side=tk.BOTTOM)
        self.update_memory_usage()
    
    def create_dirs(self):
        """创建必要的目录"""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.copy_dir, exist_ok=True)
    
    def setup_ui(self):
        """设置用户界面"""
        # 文件名输入
        tk.Label(self.master, text="输出文件名:").pack(pady=5)
        self.filename_entry = tk.Entry(self.master, width=40)
        self.filename_entry.pack(pady=5)
        self.filename_entry.insert(0, "extracted_markdown.txt")
        
        # 提取按钮
        extract_btn = tk.Button(
            self.master, 
            text="提取Markdown内容",
            command=self.extract_content,
            width=20
        )
        extract_btn.pack(pady=10)
        
        # 删除按钮
        delete_btn = tk.Button(
            self.master,
            text="清空output文件夹",
            command=self.clear_output,
            width=20,
            bg="#ff9999"
        )
        delete_btn.pack(pady=5)
        
        # 复制按钮
        copy_btn = tk.Button(
            self.master,
            text="复制到copy文件夹",
            command=self.copy_to_copy,
            width=20,
            bg="#99ccff"
        )
        copy_btn.pack(pady=5)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        tk.Label(self.master, textvariable=self.status_var).pack(pady=10)
    
    def update_memory_usage(self):
        """更新内存使用显示"""
        process = psutil.Process(os.getpid())
        mem_mb = process.memory_info().rss / (1024 * 1024)
        self.memory_label.config(text=f"内存: {mem_mb:.2f}MB")
        self.master.after(1000, self.update_memory_usage)
    
    def extract_content(self):
        """提取markdown内容"""
        try:
            filename = self.filename_entry.get().strip()
            if not filename:
                messagebox.showerror("错误", "请输入有效的文件名")
                return
                
            output_path = os.path.join(self.output_dir, filename)
            
            # 获取并排序文件
            files = [f for f in os.listdir(self.input_dir) if f.endswith('.txt')]
            files.sort()
            
            if not files:
                messagebox.showinfo("提示", "output文件夹中没有txt文件")
                return
            
            # 提取内容
            extracted = []
            for file in files:
                filepath = os.path.join(self.input_dir, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 提取markdown内容
                    matches = re.findall(r'```markdown\n(.*?)\n```', content, re.DOTALL)
                   # if matches:

                      #  extracted.append(f"===== {file} =====\n{matches[0].strip()}\n")
                except Exception as e:
                    print(f"处理文件 {file} 出错: {e}")
            
            # 写入输出文件
            if extracted:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(extracted))
                self.status_var.set(f"提取完成，保存到: {output_path}")
                messagebox.showinfo("完成", f"成功提取内容到:\n{output_path}")
            else:
                messagebox.showinfo("提示", "没有找到有效的markdown内容")
                
        except Exception as e:
            messagebox.showerror("错误", f"提取失败: {str(e)}")
            self.status_var.set("提取失败")
    
    def clear_output(self):
        """清空output文件夹"""
        try:
            for filename in os.listdir(self.input_dir):
                filepath = os.path.join(self.input_dir, filename)
                try:
                    if os.path.isfile(filepath):
                        os.unlink(filepath)
                except Exception as e:
                    print(f"删除文件 {filepath} 出错: {e}")
            
            self.status_var.set("output文件夹已清空")
            messagebox.showinfo("完成", "output文件夹内容已删除")
        except Exception as e:
            messagebox.showerror("错误", f"清空失败: {str(e)}")
            self.status_var.set("清空失败")
    
    def copy_to_copy(self):
        """复制到copy文件夹"""
        try:
            # 清空copy文件夹
            for filename in os.listdir(self.copy_dir):
                filepath = os.path.join(self.copy_dir, filename)
                try:
                    if os.path.isfile(filepath):
                        os.unlink(filepath)
                except Exception as e:
                    print(f"删除文件 {filepath} 出错: {e}")
            
            # 复制文件
            for filename in os.listdir(self.input_dir):
                src = os.path.join(self.input_dir, filename)
                dst = os.path.join(self.copy_dir, filename)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
            
            self.status_var.set(f"已复制到copy文件夹")
            messagebox.showinfo("完成", "文件已复制到copy文件夹")
        except Exception as e:
            messagebox.showerror("错误", f"复制失败: {str(e)}")
            self.status_var.set("复制失败")

if __name__ == "__main__":
    root = tk.Tk()
    app = MarkdownExtractorApp(root)
    root.mainloop()
