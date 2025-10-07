#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量图片合成GIF工具
支持将多张图片合成为GIF动画
"""

import os
import sys
from PIL import Image, ImageSequence
import argparse
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import time


class GIFMaker:
    def __init__(self):
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        
    def create_gif_from_images(self, image_folder, output_path, duration=500, loop=0, 
                             optimize=True, quality=85, sort_numerically=True, max_frames=None):
        """
        从文件夹中的图片创建GIF
        
        Args:
            image_folder: 图片文件夹路径
            output_path: 输出GIF文件路径
            duration: 每帧显示时间（毫秒）
            loop: 循环次数（0为无限循环）
            optimize: 是否优化GIF
            quality: 图片质量（1-100）
            sort_numerically: 是否按数字排序文件名
            max_frames: 最大处理图片数量（默认不限制，自动检测内存）
        """
        try:
            import psutil
            import gc
            
            # 获取系统内存信息
            memory = psutil.virtual_memory()
            available_memory = memory.available
            
            # 动态计算最大帧数（每帧大约需要1-3MB内存，保守估计）
            if max_frames is None:
                # 保守估计：每帧需要2MB内存，预留50%安全空间
                estimated_memory_per_frame = 2 * 1024 * 1024  # 2MB
                safe_memory_limit = available_memory * 0.5  # 使用50%可用内存
                calculated_max_frames = int(safe_memory_limit / estimated_memory_per_frame)
                max_frames = min(calculated_max_frames, 10000)  # 上限10000帧
                
                print(f"系统可用内存：{available_memory / 1024 / 1024:.1f} MB")
                print(f"自动计算最大帧数：{max_frames} 张")
            
            # 获取所有图片文件
            image_files = []
            for file in os.listdir(image_folder):
                if any(file.lower().endswith(fmt) for fmt in self.supported_formats):
                    image_files.append(os.path.join(image_folder, file))
            
            if not image_files:
                raise ValueError("未找到支持的图片文件")
            
            # 排序图片文件
            if sort_numerically:
                image_files.sort(key=lambda x: int(''.join(filter(str.isdigit, os.path.basename(x))) or 0))
            else:
                image_files.sort()
            
            actual_frames = min(len(image_files), max_frames)
            if len(image_files) > max_frames:
                print(f"警告：找到 {len(image_files)} 张图片，将处理前{max_frames}张")
                image_files = image_files[:max_frames]
            else:
                print(f"将处理 {actual_frames} 张图片")
            
            # 加载并处理图片
            images = []
            base_size = None
            
            # 分批处理以避免内存溢出
            batch_size = 100
            total_processed = 0
            
            for i, img_path in enumerate(image_files):
                try:
                    img = Image.open(img_path)
                    
                    # 转换为RGB模式（如果不是的话）
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # 设置统一尺寸（使用第一张图片的尺寸）
                    if base_size is None:
                        base_size = img.size
                        # 如果图片太大，自动调整尺寸
                        max_dimension = 1920
                        if base_size[0] > max_dimension or base_size[1] > max_dimension:
                            ratio = min(max_dimension/base_size[0], max_dimension/base_size[1])
                            base_size = (int(base_size[0]*ratio), int(base_size[1]*ratio))
                            print(f"图片尺寸调整为：{base_size}")
                    else:
                        img = img.resize(base_size, Image.Resampling.LANCZOS)
                    
                    # 转换为P模式以优化GIF
                    img = img.convert('P', palette=Image.ADAPTIVE, colors=256)
                    images.append(img)
                    total_processed += 1
                    
                    # 定期清理内存
                    if (i + 1) % batch_size == 0:
                        gc.collect()
                        memory_percent = psutil.virtual_memory().percent
                        print(f"已处理 {i + 1}/{len(image_files)} 张图片 (内存使用：{memory_percent:.1f}%)")
                        
                        # 如果内存使用过高，提前警告
                        if memory_percent > 80:
                            print("警告：内存使用过高，可能无法处理更多图片")
                            if len(images) > 0:
                                break
                        
                except Exception as e:
                    print(f"处理图片 {img_path} 时出错：{e}")
                    continue
            
            if not images:
                raise ValueError("没有成功加载任何图片")
            
            # 保存为GIF
            images[0].save(
                output_path,
                save_all=True,
                append_images=images[1:],
                duration=duration,
                loop=loop,
                optimize=optimize
            )
            
            print(f"成功创建GIF：{output_path}")
            print(f"共包含 {len(images)} 帧")
            return True
            
        except Exception as e:
            print(f"创建GIF时出错：{e}")
            return False
    
    def get_image_info(self, image_folder):
        """获取图片文件夹信息"""
        try:
            image_files = []
            for file in os.listdir(image_folder):
                if any(file.lower().endswith(fmt) for fmt in self.supported_formats):
                    image_files.append(file)
            
            return {
                'count': len(image_files),
                'files': sorted(image_files),
                'formats': list(set(os.path.splitext(f)[1].lower() for f in image_files))
            }
        except Exception as e:
            print(f"获取图片信息时出错：{e}")
            return None


class GIFMakerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("批量图片合成GIF工具")
        self.root.geometry("600x500")
        self.maker = GIFMaker()
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置GUI界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 文件夹选择
        folder_frame = ttk.LabelFrame(main_frame, text="图片文件夹", padding="5")
        folder_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.folder_path = tk.StringVar()
        ttk.Entry(folder_frame, textvariable=self.folder_path, width=50).grid(
            row=0, column=0, padx=5)
        ttk.Button(folder_frame, text="浏览", command=self.browse_folder).grid(
            row=0, column=1, padx=5)
        
        # 输出文件
        output_frame = ttk.LabelFrame(main_frame, text="输出文件", padding="5")
        output_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.output_path = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_path, width=50).grid(
            row=0, column=0, padx=5)
        ttk.Button(output_frame, text="浏览", command=self.browse_output).grid(
            row=0, column=1, padx=5)
        
        # 参数设置
        params_frame = ttk.LabelFrame(main_frame, text="参数设置", padding="5")
        params_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 帧间隔
        ttk.Label(params_frame, text="帧间隔 (毫秒):").grid(row=0, column=0, sticky=tk.W)
        self.duration_var = tk.IntVar(value=500)
        ttk.Entry(params_frame, textvariable=self.duration_var, width=10).grid(
            row=0, column=1, padx=5)
        
        # 循环次数
        ttk.Label(params_frame, text="循环次数 (0=无限):").grid(row=1, column=0, sticky=tk.W)
        self.loop_var = tk.IntVar(value=0)
        ttk.Entry(params_frame, textvariable=self.loop_var, width=10).grid(
            row=1, column=1, padx=5)
        
        # 优化选项
        self.optimize_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(params_frame, text="优化GIF大小", variable=self.optimize_var).grid(
            row=2, column=0, columnspan=2, sticky=tk.W)
        
        # 数字排序
        self.sort_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(params_frame, text="按数字排序文件名", variable=self.sort_var).grid(
            row=3, column=0, columnspan=2, sticky=tk.W)
        
        # 信息区域
        self.info_text = tk.Text(main_frame, height=8, width=70)
        self.info_text.grid(row=3, column=0, columnspan=2, pady=5)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                          maximum=100)
        self.progress_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="刷新信息", command=self.refresh_info).grid(
            row=0, column=0, padx=5)
        ttk.Button(button_frame, text="开始合成", command=self.start_creation).grid(
            row=0, column=1, padx=5)
        ttk.Button(button_frame, text="退出", command=self.root.quit).grid(
            row=0, column=2, padx=5)
        
        # 配置行列权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
    def browse_folder(self):
        """浏览文件夹"""
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
            self.refresh_info()
    
    def browse_output(self):
        """浏览输出文件"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".gif",
            filetypes=[("GIF files", "*.gif"), ("All files", "*.*")]
        )
        if filename:
            self.output_path.set(filename)
    
    def refresh_info(self):
        """刷新图片信息"""
        folder = self.folder_path.get()
        if not folder or not os.path.exists(folder):
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, "请先选择有效的图片文件夹")
            return
        
        info = self.maker.get_image_info(folder)
        if info:
            self.info_text.delete(1.0, tk.END)
            info_str = f"找到图片：{info['count']} 张\n"
            info_str += f"格式：{', '.join(info['formats'])}\n"
            if info['count'] > 0:
                info_str += f"前几个文件：{', '.join(info['files'][:5])}"
                if info['count'] > 5:
                    info_str += "..."
            self.info_text.insert(1.0, info_str)
    
    def start_creation(self):
        """开始创建GIF"""
        folder = self.folder_path.get()
        output = self.output_path.get()
        
        if not folder or not os.path.exists(folder):
            messagebox.showerror("错误", "请选择有效的图片文件夹")
            return
        
        if not output:
            messagebox.showerror("错误", "请指定输出文件")
            return
        
        # 在新线程中创建GIF
        thread = threading.Thread(target=self.create_gif_thread)
        thread.daemon = True
        thread.start()
    
    def create_gif_thread(self):
        """在后台线程中创建GIF"""
        try:
            folder = self.folder_path.get()
            output = self.output_path.get()
            duration = self.duration_var.get()
            loop = self.loop_var.get()
            optimize = self.optimize_var.get()
            sort_numerically = self.sort_var.get()
            
            self.root.after(0, lambda: self.info_text.delete(1.0, tk.END))
            self.root.after(0, lambda: self.info_text.insert(1.0, "开始创建GIF..."))
            
            success = self.maker.create_gif_from_images(
                folder, output, duration, loop, optimize, 
                sort_numerically=sort_numerically
            )
            
            if success:
                self.root.after(0, lambda: messagebox.showinfo("成功", "GIF创建完成！"))
            else:
                self.root.after(0, lambda: messagebox.showerror("错误", "GIF创建失败！"))
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"创建GIF时出错：{e}"))
    
    def run(self):
        """运行GUI"""
        self.root.mainloop()


def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 命令行模式
        parser = argparse.ArgumentParser(description="批量图片合成GIF工具")
        parser.add_argument("folder", help="图片文件夹路径")
        parser.add_argument("-o", "--output", default="output.gif", help="输出GIF文件路径")
        parser.add_argument("-d", "--duration", type=int, default=500, help="每帧显示时间（毫秒）")
        parser.add_argument("-l", "--loop", type=int, default=0, help="循环次数（0为无限）")
        parser.add_argument("-m", "--max", type=int, help="最大处理图片数量（默认自动检测内存）")
        parser.add_argument("--no-optimize", action="store_true", help="不优化GIF")
        parser.add_argument("--no-sort", action="store_true", help="不按数字排序文件名")
        parser.add_argument("--max-size", type=int, help="最大图片尺寸（像素）")
        
        args = parser.parse_args()
        
        maker = GIFMaker()
        success = maker.create_gif_from_images(
            args.folder, 
            args.output, 
            args.duration, 
            args.loop, 
            not args.no_optimize,
            sort_numerically=not args.no_sort
        )
        
        sys.exit(0 if success else 1)
    else:
        # GUI模式
        gui = GIFMakerGUI()
        gui.run()


if __name__ == "__main__":
    main()