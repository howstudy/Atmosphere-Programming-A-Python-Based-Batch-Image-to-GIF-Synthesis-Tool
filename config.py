#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件
用户可以在此自定义默认设置
"""

# 默认设置
DEFAULT_SETTINGS = {
    # 输出设置
    'output_filename': 'animation.gif',
    'default_output_dir': './output',
    
    # 帧设置
    'default_duration': 500,  # 毫秒
    'default_loop': 0,  # 0为无限循环
    'max_frames': 2000,
    
    # 质量设置
    'optimize_gif': True,
    'image_quality': 85,
    'max_width': 1920,
    'max_height': 1080,
    
    # 排序设置
    'sort_numerically': True,
    'case_sensitive_sort': False,
    
    # 支持的图片格式
    'supported_formats': {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'},
    
    # 界面设置
    'gui_theme': 'default',  # default, dark, light
    'window_size': '600x500',
    'show_preview': True,
    
    # 处理设置
    'resize_large_images': True,
    'resize_method': 'LANCZOS',  # NEAREST, BILINEAR, BICUBIC, LANCZOS
    'color_palette': 256,  # GIF颜色数
    
    # 日志设置
    'log_level': 'INFO',  # DEBUG, INFO, WARNING, ERROR
    'save_log': False,
    'log_file': 'gif_maker.log'
}

# 高级设置
ADVANCED_SETTINGS = {
    # 内存管理
    'max_memory_usage': '1GB',  # 最大内存使用
    'batch_size': 50,  # 每批处理的图片数量
    
    # 性能优化
    'use_multithreading': True,
    'max_workers': 4,
    
    # 文件处理
    'skip_corrupted': True,
    'backup_originals': False,
    
    # 输出优化
    'compress_output': True,
    'compression_level': 6
}

def get_setting(key, default=None):
    """获取设置值"""
    return DEFAULT_SETTINGS.get(key, default)

def update_setting(key, value):
    """更新设置值"""
    if key in DEFAULT_SETTINGS:
        DEFAULT_SETTINGS[key] = value
        return True
    return False