#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成测试图片的脚本
用于测试GIF制作工具
"""

import os
from PIL import Image, ImageDraw, ImageFont
import random

def create_test_images(output_folder, count=50):
    """创建测试图片"""
    os.makedirs(output_folder, exist_ok=True)
    
    width, height = 400, 300
    colors = [
        (255, 100, 100), (100, 255, 100), (100, 100, 255),
        (255, 255, 100), (255, 100, 255), (100, 255, 255),
        (255, 200, 100), (200, 100, 255), (100, 200, 255)
    ]
    
    for i in range(count):
        # 创建渐变背景
        img = Image.new('RGB', (width, height), color=colors[i % len(colors)])
        draw = ImageDraw.Draw(img)
        
        # 绘制数字
        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            font = ImageFont.load_default()
        
        text = str(i + 1)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # 绘制阴影
        draw.text((x+2, y+2), text, fill=(0, 0, 0), font=font)
        # 绘制文字
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
        
        # 绘制装饰
        for _ in range(5):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = x1 + random.randint(-50, 50)
            y2 = y1 + random.randint(-50, 50)
            color = random.choice(colors)
            draw.line([(x1, y1), (x2, y2)], fill=color, width=3)
        
        # 保存图片
        filename = f"frame_{i+1:03d}.jpg"
        filepath = os.path.join(output_folder, filename)
        img.save(filepath, quality=95)
        print(f"创建测试图片：{filename}")
    
    print(f"共创建 {count} 张测试图片在文件夹：{output_folder}")

if __name__ == "__main__":
    output_dir = "test_images"
    create_test_images(output_dir, count=100)
    print("测试图片创建完成！")
    print("现在可以运行：python gif_maker.py 来制作GIF")