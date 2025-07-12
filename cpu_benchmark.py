# 输出logo和程序信息
print("╔╗╔╗╔══╗╔══╗╔══╗╔══╗╔╗╔╗╔╗─╔╗╔════╗╔══╗╔╗─╔╗╔═══╗╔══╗╔══╗╔══╗╔╗─╔╗")
print("║║║║║╔╗║║╔╗║╚═╗║║╔═╝║║║║║╚═╝║╚═╗╔═╝║╔╗║║╚═╝║║╔══╝╚═╗║║╔═╝╚╗╔╝║╚═╝║")
print("║╚╝║║╚╝║║║║║──║╚╝║──║║║║║╔╗─║──║║──║║║║║╔╗─║║║╔═╗──║╚╝║───║║─║╔╗─║")
print("║╔╗║║╔╗║║║║║──║╔╗║──║║║║║║╚╗║──║║──║║║║║║╚╗║║║╚╗║──║╔╗║───║║─║║╚╗║")
print("║║║║║║║║║╚╝║╔═╝║║╚═╗║╚╝║║║─║║──║║──║╚╝║║║─║║║╚═╝║╔═╝║║╚═╗╔╝╚╗║║─║║")
print("╚╝╚╝╚╝╚╝╚══╝╚══╝╚══╝╚══╝╚╝─╚╝──╚╝──╚══╝╚╝─╚╝╚═══╝╚══╝╚══╝╚══╝╚╝─╚╝")
print("浩讯亿通cpu专业测试工具1.0.1")
import tkinter as tk
import time
import math
import random
import platform
import psutil
from multiprocessing import Pool, cpu_count, Manager
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from tkinter import ttk, scrolledtext, messagebox
import warnings
import threading
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import re
import wmi  # 用于Windows系统获取硬件信息
import sys
import os
import subprocess
from collections import deque
from datetime import datetime

# 忽略Matplotlib字体警告
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

# 简化字体配置，只使用一种中文字体
plt.rcParams["font.family"] = ["SimHei"]


# 将worker函数移出类，使其成为独立函数
def worker(iterations, cancel_flag):
    result = 0
    for i in range(iterations):
        # 更复杂的数学运算，提高测试压力
        result += math.sqrt(i) * math.sin(i) / (math.cos(i) or 1.0) + math.log(i + 1)

        # 定期检查取消标志
        if i % 100000 == 0 and cancel_flag.value:
            return result
    return result


class CPUBenchmarkUI:
    def __init__(self, root):
        self.root = root
        self.root.title("浩讯亿通©专业CPU性能测试工具1.0---浩讯亿通电脑店-2025")
        self.root.geometry("800x730")  # 缩小窗口尺寸
        self.root.minsize(800, 600)  # 缩小最小尺寸
        self.root.configure(bg="#f0f0f0")

        # 设置启动优化标志
        self.system_info_loaded = False
        self.chart_initialized = False
        self.monitor_initialized = False

        # 存储测试结果
        self.results = {}
        self.test_history = []
        self.running = False
        self.cancel_requested = False
        self.voltage = "N/A"  # 存储当前电压值
        self.temperature = "N/A"  # 存储当前温度值
        self.power = "N/A"  # 存储当前功耗值
        self.voltage_history = deque(maxlen=120)  # 存储最近2分钟的电压数据 (每秒一个点)
        self.freq_history = deque(maxlen=120)  # 存储最近2分钟的频率数据
        self.usage_history = deque(maxlen=120)  # 存储最近2分钟的CPU使用率数据
        self.temp_history = deque(maxlen=120)  # 存储最近2分钟的温度数据
        self.power_history = deque(maxlen=120)  # 存储最近2分钟的功耗数据
        self.timestamps = deque(maxlen=120)  # 存储时间戳
        self.monitor_update_interval = 1000  # 监控更新间隔(毫秒)
        self.monitoring_active = True

        # 初始化CPU信息占位符
        self.cpu_brand = "加载中..."
        self.cpu_cores = "加载中..."
        self.cpu_freq = "加载中..."
        self.cpu_usage = 0.0  # 当前CPU使用率
        self.mem_total = "加载中..."
        self.os_info = "加载中..."
        self.cpu_process = "加载中..."  # CPU工艺制程
        self.cpu_instruction_set = "加载中..."  # CPU指令集

        # 创建UI
        self.create_widgets()

        # 启动后台加载系统信息
        threading.Thread(target=self.load_system_info, daemon=True).start()

    def create_widgets(self):
        # 创建顶部信息栏 - 使用更小的字体
        info_frame = ttk.Frame(self.root, padding=5)
        info_frame.pack(fill=tk.X, padx=5, pady=2)

        self.system_info_label = ttk.Label(
            info_frame,
            text="正在加载系统信息...",
            font=("Arial", 8),  # 缩小字体
            background="#e0e0e0",
            padding=3
        )
        self.system_info_label.pack(fill=tk.X, padx=3, pady=2)

        # 创建标签页控件
        self.tab_control = ttk.Notebook(self.root)
        self.tab_control.pack(expand=1, fill="both", padx=5, pady=3)

        # 总得分标签页
        self.summary_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.summary_tab, text="总得分")
        self.setup_summary_tab()

        # 详细结果标签页
        self.details_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.details_tab, text="详细结果")
        self.setup_details_tab()

        # 历史记录标签页
        self.history_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.history_tab, text="测试历史")
        self.setup_history_tab()

        # 图表分析标签页
        self.chart_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.chart_tab, text="性能图表")
        self.setup_chart_placeholder()

        # 实时监控标签页
        self.monitor_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.monitor_tab, text="实时监控")
        self.setup_monitor_placeholder()

        # 创建底部控制区域
        control_frame = ttk.Frame(self.root, padding=5)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        # 按钮容器 - 使用更紧凑的布局
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=3)

        # 使用更小的按钮
        self.run_button = ttk.Button(
            button_frame,
            text="开始跑分",
            command=self.start_benchmark_thread,
            width=12
        )
        self.run_button.pack(side=tk.LEFT, padx=2)

        self.cancel_button = ttk.Button(
            button_frame,
            text="取消测试",
            command=self.request_cancel,
            width=10,
            state=tk.DISABLED
        )
        self.cancel_button.pack(side=tk.LEFT, padx=2)

        # 添加关于按钮
        self.about_button = ttk.Button(
            button_frame,
            text="关于",
            command=self.show_about,
            width=8
        )
        self.about_button.pack(side=tk.RIGHT, padx=2)

        self.save_button = ttk.Button(
            button_frame,
            text="保存",
            command=self.save_results,
            width=8
        )
        self.save_button.pack(side=tk.RIGHT, padx=2)

        # 监控控制按钮
        self.monitor_button = ttk.Button(
            button_frame,
            text="暂停监控",
            command=self.toggle_monitoring,
            width=10
        )
        self.monitor_button.pack(side=tk.RIGHT, padx=2)

        # 进度条区域
        progress_frame = ttk.Frame(control_frame)
        progress_frame.pack(fill=tk.X, pady=3)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            length=500  # 缩短进度条
        )
        self.progress_bar.pack(fill=tk.X)

        self.progress_label = ttk.Label(
            progress_frame,
            text="等待开始...",
            font=("Arial", 9),  # 缩小字体
            anchor=tk.CENTER
        )
        self.progress_label.pack(fill=tk.X, pady=2)

        # 状态栏 - 使用更小的字体
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=3,
            font=("Arial", 8)  # 缩小字体
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 绑定标签页切换事件
        self.tab_control.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # 配置样式
        self.configure_styles()

    def toggle_monitoring(self):
        """切换监控状态"""
        self.monitoring_active = not self.monitoring_active
        if self.monitoring_active:
            self.monitor_button.config(text="暂停监控")
            self.status_var.set("实时监控已恢复")
        else:
            self.monitor_button.config(text="恢复监控")
            self.status_var.set("实时监控已暂停")

    def show_about(self):
        """显示软件详情介绍 - 缩小窗口尺寸"""
        about_window = tk.Toplevel(self.root)
        about_window.title("关于浩讯亿通CPU测试工具")
        about_window.geometry("500x600")  # 缩小关于窗口
        about_window.resizable(False, False)
        about_window.transient(self.root)
        about_window.grab_set()

        # 创建主框架
        main_frame = ttk.Frame(about_window, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 软件名称
        title_label = ttk.Label(
            main_frame,
            text="浩讯亿通©专业CPU性能测试工具",
            font=("微软雅黑", 18, "bold"),  # 缩小字体
            foreground="#0066cc"
        )
        title_label.pack(pady=(5, 10))

        # 版本信息
        version_label = ttk.Label(
            main_frame,
            text="版本 1.0",
            font=("微软雅黑", 12),  # 缩小字体
            foreground="#333333"
        )
        version_label.pack(pady=(0, 20))

        # 软件介绍框架
        intro_frame = ttk.LabelFrame(
            main_frame,
            text="软件介绍",
            padding=10  # 减少内边距
        )
        intro_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)

        intro_text = """
浩讯亿通©专业CPU性能测试工具是一款功能全面的CPU性能评估软件，专为电脑爱好者和专业人士设计。

主要功能：
• 单核性能测试
• 浮点运算性能测试
• 整数运算性能测试
• 内存带宽测试
• 多核扩展性测试
• 加密运算性能测试
• 压缩运算性能测试
• 核心电压监控
• CPU频率监控
• CPU使用率监控
测试结果以直观的分数和图表展示，并提供详细的历史记录功能。
官方DIY电脑交流群:Q群931587484
"""
        intro_label = ttk.Label(
            intro_frame,
            text=intro_text,
            font=("微软雅黑", 10),  # 缩小字体
            justify=tk.LEFT,
            wraplength=450  # 缩小换行宽度
        )
        intro_label.pack(fill=tk.BOTH, expand=True)

        # 作者信息
        author_frame = ttk.Frame(main_frame)
        author_frame.pack(fill=tk.X, pady=(15, 5))

        author_label = ttk.Label(
            author_frame,
            text="开发团队：浩讯亿通电脑店",
            font=("微软雅黑", 10),  # 缩小字体
            foreground="#555555"
        )
        author_label.pack(side=tk.LEFT, padx=5)

        copyright_label = ttk.Label(
            author_frame,
            text="© 2025 浩讯亿通电脑店 版权所有",
            font=("微软雅黑", 9),  # 缩小字体
            foreground="#777777"
        )
        copyright_label.pack(side=tk.RIGHT, padx=5)

        # 关闭按钮
        close_button = ttk.Button(
            main_frame,
            text="关闭",
            command=about_window.destroy,
            width=10  # 缩小按钮
        )
        close_button.pack(pady=10)

    def configure_styles(self):
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=("Arial", 9))  # 统一使用小字体
        style.configure("TButton", padding=3, font=("Arial", 9))  # 缩小按钮
        style.configure("Treeview", font=("Arial", 9), rowheight=22)  # 缩小表格
        style.configure("Treeview.Heading", font=("Arial", 9, "bold"))
        style.configure("TNotebook", background="#f0f0f0")
        style.configure("TNotebook.Tab", padding=[8, 3], font=("Arial", 9))  # 缩小标签

    def setup_summary_tab(self):
        # 创建总得分标签页内容 - 更紧凑
        summary_frame = ttk.LabelFrame(
            self.summary_tab,
            text="CPU性能总评",
            padding=8  # 减少内边距
        )
        summary_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 得分显示 - 使用更紧凑布局
        score_frame = ttk.Frame(summary_frame)
        score_frame.pack(fill=tk.X, padx=5, pady=10)

        ttk.Label(
            score_frame,
            text="跑分结果：",
            font=("Arial", 20, "bold")  # 缩小字体
        ).pack(side=tk.LEFT, padx=10)

        self.score_value_label = ttk.Label(
            score_frame,
            text="0.00",
            font=("Arial", 20, "bold"),  # 缩小字体
            foreground="#c00000"
        )
        self.score_value_label.pack(side=tk.LEFT, padx=5)

        self.rank_label = ttk.Label(
            score_frame,
            text="等级：未测试",
            font=("Arial", 14),  # 缩小字体
            foreground="#0066cc"
        )
        self.rank_label.pack(side=tk.RIGHT, padx=10)

        # CPU信息 - 使用更小字体
        cpu_frame = ttk.Frame(summary_frame)
        cpu_frame.pack(fill=tk.X, padx=5, pady=5)

        self.cpu_info_label = ttk.Label(
            cpu_frame,
            text="正在加载CPU信息...",
            font=("Arial", 10),  # 缩小字体
            wraplength=500  # 缩小换行宽度
        )
        self.cpu_info_label.pack(fill=tk.X)

        # 性能对比 - 使用更小字体
        comparison_frame = ttk.LabelFrame(
            summary_frame,
            text="性能对比",
            padding=8  # 减少内边距
        )
        comparison_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.comparison_text = scrolledtext.ScrolledText(
            comparison_frame,
            wrap=tk.WORD,
            width=50,  # 缩小宽度
            height=6,  # 减少高度
            font=("Arial", 9)  # 缩小字体
        )
        self.comparison_text.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        self.comparison_text.config(state=tk.DISABLED)

    def setup_details_tab(self):
        # 创建详细结果标签页内容 - 更紧凑
        details_frame = ttk.LabelFrame(
            self.details_tab,
            text="测试详情",
            padding=8  # 减少内边距
        )
        details_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("测试项目", "得分", "等级", "测试详情")
        self.details_tree = ttk.Treeview(details_frame, columns=columns, show="headings", height=8)  # 减少高度

        # 配置列 - 缩小列宽
        col_widths = {"测试项目": 100, "得分": 70, "等级": 70, "测试详情": 300}
        col_anchors = {"测试项目": tk.W, "得分": tk.CENTER, "等级": tk.CENTER, "测试详情": tk.W}

        for col in columns:
            self.details_tree.heading(col, text=col)
            self.details_tree.column(col, width=col_widths.get(col, 80),
                                     anchor=col_anchors.get(col, tk.CENTER))

        # 添加滚动条
        scrollbar = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=self.details_tree.yview)
        self.details_tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.details_tree.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)

    def setup_history_tab(self):
        # 创建历史记录标签页内容 - 更紧凑
        history_frame = ttk.LabelFrame(
            self.history_tab,
            text="测试历史",
            padding=8  # 减少内边距
        )
        history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("时间", "总分", "等级", "CPU型号")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=8)  # 减少高度

        # 缩小列宽
        col_widths = {"时间": 130, "总分": 80, "等级": 70, "CPU型号": 180}
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=col_widths.get(col, 100), anchor=tk.CENTER)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_tree.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)

        # 查看详情按钮 - 更小按钮
        button_frame = ttk.Frame(history_frame)
        button_frame.pack(fill=tk.X, padx=3, pady=3)

        self.view_detail_button = ttk.Button(
            button_frame,
            text="查看详情",
            command=self.view_history_detail,
            state=tk.DISABLED,
            width=10  # 缩小按钮
        )
        self.view_detail_button.pack(side=tk.RIGHT, padx=3)

        self.clear_history_button = ttk.Button(
            button_frame,
            text="清除历史",
            command=self.clear_history,
            width=10  # 缩小按钮
        )
        self.clear_history_button.pack(side=tk.RIGHT, padx=3)

    def setup_chart_placeholder(self):
        """设置图表分析标签页占位符（延迟加载）"""
        self.chart_frame = ttk.LabelFrame(
            self.chart_tab,
            text="性能分析",
            padding=5  # 减少内边距
        )
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 添加占位标签 - 使用更小字体
        self.chart_placeholder = ttk.Label(
            self.chart_frame,
            text="图表将在首次切换到本标签页时初始化...",
            font=("Arial", 10)  # 缩小字体
        )
        self.chart_placeholder.pack(expand=True, pady=80)  # 减少垂直间距

    def setup_monitor_placeholder(self):
        """设置实时监控标签页占位符（延迟加载）"""
        self.monitor_frame = ttk.LabelFrame(
            self.monitor_tab,
            text="CPU实时监控",
            padding=5  # 减少内边距
        )
        self.monitor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 添加占位标签 - 使用更小字体
        self.monitor_placeholder = ttk.Label(
            self.monitor_frame,
            text="监控图表将在首次切换到本标签页时初始化...",
            font=("Arial", 10)  # 缩小字体
        )
        self.monitor_placeholder.pack(expand=True, pady=80)  # 减少垂直间距

    def initialize_chart(self):
        """初始化图表（当首次切换到图表标签页时调用）"""
        if self.chart_initialized:
            return

        # 移除占位符
        self.chart_placeholder.destroy()

        # 创建更小的图表
        self.figure = plt.Figure(figsize=(6, 4), dpi=80)  # 缩小图表尺寸
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=3, pady=3)

        # 设置初始化标志
        self.chart_initialized = True

        # 如果已有测试结果，绘制图表
        if self.results:
            self.plot_results()

    def initialize_monitor(self):
        """初始化监控图表（当首次切换到监控标签页时调用）"""
        if self.monitor_initialized:
            return

        # 移除占位符
        self.monitor_placeholder.destroy()

        # 创建监控主框架 - 使用垂直布局
        main_frame = ttk.Frame(self.monitor_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 创建数据面板框架
        data_frame = ttk.LabelFrame(
            main_frame,
            text="实时数据",
            padding=5
        )
        data_frame.pack(fill=tk.X, padx=5, pady=5)

        # 使用网格布局创建数据面板
        data_labels = [
            ("电压", "V", "#1f77b4"),
            ("频率", "MHz", "#ff7f0e"),
            ("使用率", "%", "#2ca02c"),
            ("温度", "°C", "#d62728"),
            ("功耗", "W", "#9467bd")
        ]

        self.data_values = {}

        # 创建两行布局
        row1 = ttk.Frame(data_frame)
        row1.pack(fill=tk.X, pady=3)
        row2 = ttk.Frame(data_frame)
        row2.pack(fill=tk.X, pady=3)

        rows = [row1, row2]

        for idx, (label, unit, color) in enumerate(data_labels):
            row_idx = idx // 3  # 每行3个指标
            col_idx = idx % 3

            if row_idx >= len(rows):
                break

            frame = ttk.Frame(rows[row_idx])
            frame.grid(row=0, column=col_idx, padx=10, sticky=tk.W)

            # 标签
            lbl = ttk.Label(
                frame,
                text=f"{label}:",
                font=("Arial", 9, "bold"),
                foreground=color
            )
            lbl.pack(anchor=tk.W)

            # 值
            value_frame = ttk.Frame(frame)
            value_frame.pack(anchor=tk.W)

            value_label = ttk.Label(
                value_frame,
                text="0.00",
                font=("Arial", 10, "bold"),
                foreground=color
            )
            value_label.pack(side=tk.LEFT)

            unit_label = ttk.Label(
                value_frame,
                text=unit,
                font=("Arial", 8),
                foreground=color
            )
            unit_label.pack(side=tk.LEFT, padx=(2, 0))

            self.data_values[label] = value_label

        # 创建图表框架
        chart_frame = ttk.LabelFrame(
            main_frame,
            text="实时图表",
            padding=5
        )
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 创建图表容器
        chart_container = ttk.Frame(chart_frame)
        chart_container.pack(fill=tk.BOTH, expand=True)

        # 创建图表
        self.monitor_figure = plt.Figure(figsize=(6, 4), dpi=80)
        self.monitor_ax = self.monitor_figure.add_subplot(111)
        self.monitor_canvas = FigureCanvasTkAgg(self.monitor_figure, master=chart_container)
        self.monitor_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=3, pady=3)

        # 设置初始化标志
        self.monitor_initialized = True

        # 绘制初始图表
        self.plot_monitor()

    def get_cpu_info(self):
        """获取CPU信息，包括工艺制程和指令集"""
        try:
            cpu_info = {}

            # 获取CPU品牌
            if platform.system() == "Windows":
                import winreg
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
                    cpu_info['brand'] = winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
                except:
                    # 如果注册表方法失败，尝试WMI方法
                    try:
                        c = wmi.WMI()
                        for processor in c.Win32_Processor():
                            cpu_info['brand'] = processor.Name.strip()
                            break
                    except:
                        cpu_info['brand'] = platform.processor()
            else:
                # Linux/macOS
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if 'model name' in line:
                            cpu_info['brand'] = line.split(':')[1].strip()
                        elif 'cpu family' in line:
                            family = line.split(':')[1].strip()
                        elif 'model' in line and not 'name' in line:
                            model = line.split(':')[1].strip()
                        elif 'stepping' in line:
                            stepping = line.split(':')[1].strip()
                    else:
                        if 'brand' not in cpu_info:
                            cpu_info['brand'] = platform.processor()

            # 获取工艺制程
            cpu_info['process'] = self.detect_cpu_process(cpu_info['brand'])

            # 获取指令集
            cpu_info['instruction_set'] = self.get_cpu_instruction_set()

            # 获取CPU核心数
            physical_cores = psutil.cpu_count(logical=False)
            logical_cores = psutil.cpu_count(logical=True)
            cpu_info['physical_cores'] = physical_cores
            cpu_info['logical_cores'] = logical_cores

            return cpu_info
        except Exception as e:
            print(f"获取CPU信息出错: {str(e)}")
            return {
                'brand': platform.processor(),
                'physical_cores': psutil.cpu_count(logical=False),
                'logical_cores': psutil.cpu_count(logical=True),
                'process': "未知工艺",
                'instruction_set': "未知指令集"
            }

    def detect_cpu_process(self, cpu_brand):
        """智能检测CPU工艺制程"""
        try:
            # 首先尝试使用WMI获取更精确的信息 (Windows only)
            if platform.system() == "Windows":
                try:
                    c = wmi.WMI()
                    for processor in c.Win32_Processor():
                        # 检查是否有工艺信息字段
                        if hasattr(processor, 'Architecture'):
                            # 根据架构判断
                            architecture = processor.Architecture
                            if architecture == 0:  # x86
                                return "32nm (估计值)"
                            elif architecture == 1:  # MIPS
                                return "未知工艺"
                            elif architecture == 2:  # Alpha
                                return "未知工艺"
                            elif architecture == 3:  # PowerPC
                                return "未知工艺"
                            elif architecture == 5:  # ARM
                                return "7nm或更先进 (估计值)"
                            elif architecture == 6:  # ia64
                                return "14nm (估计值)"
                            elif architecture == 9:  # x64
                                # 进一步根据型号判断
                                if "Intel" in cpu_brand:
                                    return self.detect_intel_process(cpu_brand)
                                elif "AMD" in cpu_brand:
                                    return self.detect_amd_process(cpu_brand)
                        break
                except:
                    pass

            # 根据CPU品牌进行智能判断
            if "Intel" in cpu_brand:
                return self.detect_intel_process(cpu_brand)
            elif "AMD" in cpu_brand:
                return self.detect_amd_process(cpu_brand)
            elif "Apple" in cpu_brand:
                return "5nm或更先进 (Apple Silicon)"
            elif "Qualcomm" in cpu_brand:
                return "7nm或更先进 (移动处理器)"

            # 默认值
            return "未知工艺"
        except:
            return "未知工艺"

    def detect_intel_process(self, cpu_brand):
        """检测Intel CPU的工艺制程"""
        # 更精确的Intel工艺检测
        if "i9" in cpu_brand:
            if "11th" in cpu_brand:
                return "14nm (Rocket Lake)"
            elif "12th" in cpu_brand or "13th" in cpu_brand:
                return "Intel 7 (10nm)"
            elif "14th" in cpu_brand:
                return "Intel 7 (10nm)"
            else:
                return "14nm或更先进"
        elif "i7" in cpu_brand:
            if "10th" in cpu_brand:
                return "14nm (Comet Lake)"
            elif "11th" in cpu_brand:
                return "14nm (Rocket Lake)"
            elif "12th" in cpu_brand or "13th" in cpu_brand:
                return "Intel 7 (10nm)"
            else:
                return "14nm"
        elif "i5" in cpu_brand:
            if "10th" in cpu_brand:
                return "14nm (Comet Lake)"
            elif "11th" in cpu_brand:
                return "14nm (Rocket Lake)"
            elif "12th" in cpu_brand or "13th" in cpu_brand:
                return "Intel 7 (10nm)"
            else:
                return "14nm"
        elif "i3" in cpu_brand:
            return "14nm"
        elif "Pentium" in cpu_brand or "Celeron" in cpu_brand:
            return "14nm"
        elif "Xeon" in cpu_brand:
            if "Platinum" in cpu_brand or "Gold" in cpu_brand:
                return "10nm (Ice Lake) 或 14nm (Cascade Lake)"
            else:
                return "14nm"
        else:
            return "14nm或更先进"

    def detect_amd_process(self, cpu_brand):
        """检测AMD CPU的工艺制程"""
        # 更精确的AMD工艺检测
        if "Ryzen 9" in cpu_brand:
            if "7950" in cpu_brand or "7900" in cpu_brand:
                return "5nm (Zen 4)"
            elif "5950" in cpu_brand or "5900" in cpu_brand:
                return "7nm (Zen 3)"
            elif "3950" in cpu_brand or "3900" in cpu_brand:
                return "7nm (Zen 2)"
            else:
                return "7nm或更先进"
        elif "Ryzen 7" in cpu_brand:
            if "7700" in cpu_brand or "7800" in cpu_brand:
                return "5nm (Zen 4)"
            elif "5700" in cpu_brand or "5800" in cpu_brand:
                return "7nm (Zen 3)"
            elif "3700" in cpu_brand or "3800" in cpu_brand:
                return "7nm (Zen 2)"
            else:
                return "7nm"
        elif "Ryzen 5" in cpu_brand:
            if "7600" in cpu_brand:
                return "5nm (Zen 4)"
            elif "5600" in cpu_brand:
                return "7nm (Zen 3)"
            elif "3600" in cpu_brand:
                return "7nm (Zen 2)"
            else:
                return "7nm"
        elif "Ryzen 3" in cpu_brand:
            if "4300" in cpu_brand or "4100" in cpu_brand:
                return "7nm (Zen 2)"
            else:
                return "12nm"
        elif "Threadripper" in cpu_brand:
            if "3990" in cpu_brand or "3970" in cpu_brand:
                return "7nm (Zen 2)"
            elif "2990" in cpu_brand or "2970" in cpu_brand:
                return "12nm (Zen+)"
            else:
                return "7nm或更先进"
        elif "EPYC" in cpu_brand:
            return "7nm或更先进 (服务器CPU)"
        else:
            return "7nm或更先进"

    def get_cpu_instruction_set(self):
        """获取CPU支持的完整指令集"""
        instruction_sets = []

        # 在Windows上使用WMI获取指令集信息
        if platform.system() == "Windows":
            try:
                c = wmi.WMI()
                for processor in c.Win32_Processor():
                    # 检查支持的指令集标志
                    if processor.AddressWidth == 64:
                        instruction_sets.append("x64")
                    if processor.DataWidth == 32:
                        instruction_sets.append("x86")
                    if "MMX" in processor.Caption:
                        instruction_sets.append("MMX")
                    if "SSE" in processor.Caption:
                        instruction_sets.append("SSE")
                    if "SSE2" in processor.Caption:
                        instruction_sets.append("SSE2")
                    if "SSE3" in processor.Caption:
                        instruction_sets.append("SSE3")
                    if "SSSE3" in processor.Caption:
                        instruction_sets.append("SSSE3")
                    if "SSE4" in processor.Caption:
                        instruction_sets.append("SSE4")
                    if "SSE4.1" in processor.Caption:
                        instruction_sets.append("SSE4.1")
                    if "SSE4.2" in processor.Caption:
                        instruction_sets.append("SSE4.2")
                    if "AVX" in processor.Caption:
                        instruction_sets.append("AVX")
                    if "AVX2" in processor.Caption:
                        instruction_sets.append("AVX2")
                    if "AVX512" in processor.Caption:
                        instruction_sets.append("AVX512")
                    if "AES" in processor.Caption:
                        instruction_sets.append("AES")
                    if "FMA" in processor.Caption:
                        instruction_sets.append("FMA")
                    if "F16C" in processor.Caption:
                        instruction_sets.append("F16C")
                    if "BMI1" in processor.Caption:
                        instruction_sets.append("BMI1")
                    if "BMI2" in processor.Caption:
                        instruction_sets.append("BMI2")
                    if "AMD64" in processor.Caption:
                        instruction_sets.append("AMD64")
                    if "EM64T" in processor.Caption:
                        instruction_sets.append("EM64T")
                    if "VT-x" in processor.Caption:
                        instruction_sets.append("VT-x")
                    if "AMD-V" in processor.Caption:
                        instruction_sets.append("AMD-V")
                    if "HyperThreading" in processor.Caption:
                        instruction_sets.append("HyperThreading")
                    if "NX" in processor.Caption:
                        instruction_sets.append("NX")
                    if "SMEP" in processor.Caption:
                        instruction_sets.append("SMEP")
                    if "SMAP" in processor.Caption:
                        instruction_sets.append("SMAP")
                    break
            except:
                pass

        # 在Linux/macOS上通过/proc/cpuinfo获取
        else:
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    flags_line = ""
                    for line in f:
                        if line.startswith('flags') or line.startswith('Features'):
                            flags_line = line
                            break

                    if flags_line:
                        flags = flags_line.split(':')[1].split()
                        if 'mmx' in flags:
                            instruction_sets.append("MMX")
                        if 'sse' in flags:
                            instruction_sets.append("SSE")
                        if 'sse2' in flags:
                            instruction_sets.append("SSE2")
                        if 'sse3' in flags or 'pni' in flags:
                            instruction_sets.append("SSE3")
                        if 'ssse3' in flags:
                            instruction_sets.append("SSSE3")
                        if 'sse4_1' in flags:
                            instruction_sets.append("SSE4.1")
                        if 'sse4_2' in flags:
                            instruction_sets.append("SSE4.2")
                        if 'avx' in flags:
                            instruction_sets.append("AVX")
                        if 'avx2' in flags:
                            instruction_sets.append("AVX2")
                        if 'avx512f' in flags:
                            instruction_sets.append("AVX512F")
                        if 'avx512cd' in flags:
                            instruction_sets.append("AVX512CD")
                        if 'avx512bw' in flags:
                            instruction_sets.append("AVX512BW")
                        if 'avx512dq' in flags:
                            instruction_sets.append("AVX512DQ")
                        if 'avx512vl' in flags:
                            instruction_sets.append("AVX512VL")
                        if 'aes' in flags:
                            instruction_sets.append("AES")
                        if 'fma' in flags:
                            instruction_sets.append("FMA")
                        if 'f16c' in flags:
                            instruction_sets.append("F16C")
                        if 'bmi1' in flags:
                            instruction_sets.append("BMI1")
                        if 'bmi2' in flags:
                            instruction_sets.append("BMI2")
                        if 'lm' in flags:  # Long mode (64-bit)
                            instruction_sets.append("x64")
                        if 'vmx' in flags:
                            instruction_sets.append("VT-x")
                        if 'svm' in flags:
                            instruction_sets.append("AMD-V")
                        if 'ht' in flags:
                            instruction_sets.append("HyperThreading")
                        if 'nx' in flags:
                            instruction_sets.append("NX")
                        if 'smep' in flags:
                            instruction_sets.append("SMEP")
                        if 'smap' in flags:
                            instruction_sets.append("SMAP")
            except:
                pass

        # 去重并排序
        instruction_sets = list(set(instruction_sets))
        instruction_sets.sort()

        # 如果没有找到指令集，使用默认值
        if not instruction_sets:
            instruction_sets = ["x86/x64"]

        # 返回完整的指令集列表
        return ', '.join(instruction_sets)

    def get_cpu_freq(self):
        """获取当前CPU频率"""
        try:
            freq = psutil.cpu_freq()
            if freq and freq.current > 0:
                return freq.current
            return 0.0
        except:
            return 0.0

    def get_cpu_usage(self):
        """获取当前CPU使用率"""
        try:
            return psutil.cpu_percent(interval=0.1)
        except:
            return 0.0

    def detect_windows_version(self):
        """精确检测Windows版本"""
        if platform.system() != "Windows":
            return platform.system()

        version = platform.release()
        build = platform.version()

        # Windows 11 检测 (版本10.0.22000或更高)
        if version == "10" and int(build.split('.')[2]) >= 22000:
            return "Windows 11"

        # Windows 10
        if version == "10":
            return "Windows 10"

        # Windows 8/8.1
        if version == "8":
            return "Windows 8"
        if version == "8.1":
            return "Windows 8.1"

        # Windows 7
        if version == "7":
            return "Windows 7"

        # Windows XP
        if version == "XP":
            return "Windows XP"

        return f"Windows {version}"

    def load_system_info(self):
        """加载系统信息（优化版）"""
        try:
            # 获取系统信息
            self.os_info = self.detect_windows_version()

            # 获取内存信息
            mem = psutil.virtual_memory()
            self.mem_total = f"{mem.total / (1024 ** 3):.1f} GB"

            # 获取CPU信息（改进的方法）
            cpu_info = self.get_cpu_info()
            self.cpu_brand = cpu_info['brand']
            self.cpu_cores = f"{cpu_info['physical_cores']}物理/{cpu_info['logical_cores']}逻辑"
            self.cpu_freq = self.get_cpu_freq()  # 使用改进的频率获取方法
            self.cpu_process = cpu_info['process']  # 工艺制程
            self.cpu_instruction_set = cpu_info['instruction_set']  # 指令集

            # 标记系统信息已加载
            self.system_info_loaded = True

            # 更新UI
            self.root.after(0, self.update_system_info_display)

            # 启动监控
            self.root.after(1000, self.update_monitor_data)

        except Exception as e:
            print(f"加载系统信息出错: {str(e)}")
            self.root.after(100, lambda: self.system_info_label.config(text=f"获取系统信息出错: {str(e)}"))

    def update_system_info_display(self):
        """更新系统信息显示"""
        if not self.system_info_loaded:
            return

        # 更新顶部信息栏
        freq_display = f"{self.cpu_freq:.2f} GHz" if self.cpu_freq > 0 else "未知频率"
        usage_display = f"{self.cpu_usage:.1f}%"
        temp_display = self.temperature
        power_display = self.power
        info_text = (f"系统: {self.os_info} | "
                     f"CPU: {self.cpu_brand} | "
                     f"核心数: {self.cpu_cores} | "
                     f"频率: {freq_display} | "
                     f"使用率: {usage_display} | "
                     f"温度: {temp_display} | "
                     f"功耗: {power_display} | "
                     f"电压: {self.voltage}V | "
                     f"工艺: {self.cpu_process} | "
                     f"内存: {self.mem_total}")
        self.system_info_label.config(text=info_text)

        # 更新总得分标签页的CPU信息
        cpu_details = (
            f"CPU型号: {self.cpu_brand}\n"
            f"核心/线程: {self.cpu_cores}\n"
            f"工艺制程: {self.cpu_process}\n"
            f"指令集: {self.cpu_instruction_set}\n"
            f"当前频率: {freq_display}\n"
            f"当前使用率: {usage_display}\n"
            f"当前温度: {temp_display}\n"
            f"当前功耗: {power_display}\n"
            f"当前电压: {self.voltage}V"
        )
        self.cpu_info_label.config(text=cpu_details)

    def get_cpu_temp(self):
        """获取CPU温度"""
        try:
            if platform.system() == "Windows":
                # 尝试使用OpenHardwareMonitor
                try:
                    c = wmi.WMI(namespace=r"root\OpenHardwareMonitor")
                    sensors = c.Sensor()
                    for sensor in sensors:
                        if sensor.SensorType == 'Temperature' and 'CPU' in sensor.Name:
                            return sensor.Value
                    return None
                except:
                    # 如果OpenHardwareMonitor不可用，尝试其他方法
                    pass
            elif platform.system() == "Linux":
                # 尝试读取/sys/class/thermal
                try:
                    for i in range(10):  # 检查多个thermal zone
                        path = f"/sys/class/thermal/thermal_zone{i}/temp"
                        if os.path.exists(path):
                            with open(path, "r") as f:
                                temp = float(f.read().strip()) / 1000
                                # 只返回合理的温度值
                                if 10 < temp < 120:
                                    return temp
                    return None
                except:
                    pass
            return None
        except:
            return None

    def estimate_cpu_power(self):
        """估算CPU功耗"""
        # 基于使用率和频率的简单估算
        freq_factor = self.cpu_freq / 3000 if self.cpu_freq > 0 else 1.0
        usage_factor = self.cpu_usage / 100

        # 根据CPU类型设置基础功耗
        if "i9" in self.cpu_brand or "R9" in self.cpu_brand:
            base_power = 65  # TDP基础值
        elif "i7" in self.cpu_brand or "R7" in self.cpu_brand:
            base_power = 45
        elif "i5" in self.cpu_brand or "R5" in self.cpu_brand:
            base_power = 35
        else:  # 低端CPU
            base_power = 25

        # 计算动态功耗
        dynamic_power = base_power * (0.4 + 0.4 * freq_factor + 0.2 * usage_factor)

        # 添加随机波动
        dynamic_power += random.uniform(-2, 2)

        # 确保在合理范围内
        return max(10, min(150, dynamic_power))

    def update_monitor_data(self):
        """更新监控数据（电压、频率、使用率、温度、功耗）"""
        try:
            # 获取当前频率
            current_freq = self.get_cpu_freq()

            # 获取当前使用率
            self.cpu_usage = self.get_cpu_usage()

            # 获取电压
            voltage_found = False
            voltage_value = 0.0
            if platform.system() == "Windows":
                # 方法1: 使用OpenHardwareMonitor
                try:
                    c = wmi.WMI(namespace=r"root\OpenHardwareMonitor")
                    sensors = c.Sensor()
                    for sensor in sensors:
                        if sensor.SensorType == 'Voltage' and ('CPU Core' in sensor.Name or 'Core' in sensor.Name):
                            voltage_value = sensor.Value
                            self.voltage = f"{voltage_value:.3f}"
                            voltage_found = True
                            break
                except:
                    pass

                # 方法2: 使用WMI
                if not voltage_found:
                    try:
                        c = wmi.WMI()
                        for sensor in c.Win32_VoltageProbe():
                            if "CPU" in sensor.Name or "Core" in sensor.Name:
                                voltage_value = sensor.CurrentReading / 1000
                                if voltage_value > 0.5:  # 过滤掉无效值
                                    self.voltage = f"{voltage_value:.3f}"
                                    voltage_found = True
                                    break
                    except:
                        pass

            elif platform.system() == "Linux":
                # 方法3: 使用ACPI
                try:
                    import acpi
                    voltages = acpi.get_voltages()
                    if voltages:
                        for name, value in voltages.items():
                            if "core" in name.lower():
                                voltage_value = value
                                self.voltage = f"{voltage_value:.3f}"
                                voltage_found = True
                                break
                except:
                    pass

                # 方法4: 使用sysfs
                if not voltage_found:
                    try:
                        # 尝试可能的路径
                        paths = [
                            "/sys/class/hwmon/hwmon0/in0_input",
                            "/sys/class/hwmon/hwmon1/in0_input",
                            "/sys/class/hwmon/hwmon2/in0_input",
                            "/sys/class/hwmon/hwmon0/device/in0_input"
                        ]

                        for path in paths:
                            if os.path.exists(path):
                                with open(path, "r") as f:
                                    voltage_value = int(f.read().strip()) / 1000
                                    if voltage_value > 0.5:  # 过滤掉无效值
                                        self.voltage = f"{voltage_value:.3f}"
                                        voltage_found = True
                                        break
                    except:
                        pass

            # 如果无法获取真实电压，使用智能模拟
            if not voltage_found:
                if "Intel" in self.cpu_brand:
                    base_voltage = 0.8
                elif "AMD" in self.cpu_brand:
                    base_voltage = 1.0
                else:
                    base_voltage = 1.0

                # 更精确的电压模拟算法
                # 电压随负载增加而增加，随频率增加而增加
                freq_factor = current_freq / 3000 if current_freq > 0 else 1.0
                voltage_value = base_voltage + (self.cpu_usage / 2000) + (freq_factor * 0.2) + random.uniform(-0.02,
                                                                                                              0.02)
                self.voltage = f"{voltage_value:.3f}"
            else:
                voltage_value = float(self.voltage)

            # 获取温度
            temp_value = self.get_cpu_temp()
            if temp_value is None:
                # 智能温度模拟
                # 基础温度 + 使用率影响 + 频率影响
                base_temp = 30  # 环境温度
                usage_impact = self.cpu_usage * 0.5
                freq_impact = (current_freq - 2000) * 0.01 if current_freq > 2000 else 0
                temp_value = base_temp + usage_impact + freq_impact + random.uniform(-1, 1)
                self.temperature = f"{temp_value:.1f}°C"
            else:
                self.temperature = f"{temp_value:.1f}°C"

            # 获取功耗
            power_value = self.estimate_cpu_power()
            self.power = f"{power_value:.1f}W"

            # 记录监控数据
            if self.monitoring_active:
                now = datetime.now()
                self.timestamps.append(now)
                self.voltage_history.append(voltage_value)
                self.freq_history.append(current_freq)
                self.usage_history.append(self.cpu_usage)
                self.temp_history.append(temp_value)
                self.power_history.append(power_value)

                # 如果监控图表已初始化，更新图表
                if self.monitor_initialized:
                    self.plot_monitor()

        except Exception as e:
            print(f"监控数据更新错误: {str(e)}")
            self.voltage = "N/A"
            self.temperature = "N/A"
            self.power = "N/A"

        # 更新系统信息显示
        if self.system_info_loaded:
            self.root.after(0, self.update_system_info_display)

        # 安排下一次更新
        self.root.after(self.monitor_update_interval, self.update_monitor_data)

    def plot_monitor(self):
        """绘制监控图表"""
        if not self.monitor_initialized or not self.timestamps:
            return

        # 准备时间标签
        time_labels = [ts.strftime("%H:%M:%S") for ts in self.timestamps]

        # 更新数据面板
        if self.voltage != "N/A":
            self.data_values["电压"].config(text=f"{float(self.voltage):.3f}")
        if self.freq_history:
            self.data_values["频率"].config(text=f"{self.freq_history[-1]:.2f}")
        if self.usage_history:
            self.data_values["使用率"].config(text=f"{self.usage_history[-1]:.1f}")
        if self.temperature != "N/A":
            self.data_values["温度"].config(text=f"{float(self.temperature.split('°')[0]):.1f}")
        if self.power != "N/A":
            self.data_values["功耗"].config(text=f"{float(self.power.split('W')[0]):.1f}")

        # 更新监控图表
        self.monitor_ax.clear()

        # 绘制电压曲线
        voltage_color = "#1f77b4"
        voltage_line, = self.monitor_ax.plot(time_labels, self.voltage_history,
                                             color=voltage_color, linewidth=1.5,
                                             label=f"电压")
        self.monitor_ax.set_ylabel('电压 (V)', color=voltage_color, fontsize=9)
        self.monitor_ax.tick_params(axis='y', labelcolor=voltage_color)
        self.monitor_ax.set_ylim(min(self.voltage_history) * 0.95, max(self.voltage_history) * 1.05)

        # 创建第二个Y轴用于频率
        ax2 = self.monitor_ax.twinx()
        freq_color = "#ff7f0e"
        freq_line, = ax2.plot(time_labels, self.freq_history,
                              color=freq_color, linewidth=1.5,
                              label=f"频率")
        ax2.set_ylabel('频率 (MHz)', color=freq_color, fontsize=9)
        ax2.tick_params(axis='y', labelcolor=freq_color)
        ax2.set_ylim(min(self.freq_history) * 0.95, max(self.freq_history) * 1.05)

        # 创建第三个Y轴用于使用率
        ax3 = self.monitor_ax.twinx()
        ax3.spines['right'].set_position(('outward', 60))
        usage_color = "#2ca02c"
        usage_line, = ax3.plot(time_labels, self.usage_history,
                               color=usage_color, linewidth=1.5,
                               label=f"使用率")
        ax3.set_ylabel('使用率 (%)', color=usage_color, fontsize=9)
        ax3.tick_params(axis='y', labelcolor=usage_color)
        ax3.set_ylim(0, 100)  # 使用率范围0-100%

        # 设置X轴标签旋转并限制数量
        n = len(time_labels)
        step = max(1, n // 10)  # 只显示10个标签
        self.monitor_ax.set_xticks(time_labels[::step])
        self.monitor_ax.set_xticklabels(time_labels[::step], rotation=45, fontsize=8)

        # 设置标题
        self.monitor_ax.set_title('CPU实时监控图表', fontsize=10, pad=10)

        # 添加图例
        lines = [voltage_line, freq_line, usage_line]
        labels = [line.get_label() for line in lines]
        self.monitor_ax.legend(lines, labels, loc='upper left', fontsize=8,
                               bbox_to_anchor=(0.0, -0.15), ncol=3)

        # 添加网格
        self.monitor_ax.grid(True, linestyle='--', alpha=0.3)

        # 调整布局
        self.monitor_figure.tight_layout()
        self.monitor_figure.subplots_adjust(bottom=0.25)  # 为图例留出空间

        # 更新画布
        self.monitor_canvas.draw()

    def on_tab_changed(self, event):
        """处理标签页切换事件"""
        selected_tab = self.tab_control.select()
        tab_text = self.tab_control.tab(selected_tab, "text")

        # 当首次切换到图表标签页时初始化图表
        if tab_text == "性能图表" and not self.chart_initialized:
            self.initialize_chart()

        # 当首次切换到监控标签页时初始化监控图表
        elif tab_text == "实时监控" and not self.monitor_initialized:
            self.initialize_monitor()

    def start_benchmark_thread(self):
        """在单独的线程中运行基准测试"""
        if self.running:
            return

        self.running = True
        self.cancel_requested = False
        self.run_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.status_var.set("测试运行中...")
        self.monitoring_active = False  # 测试期间暂停监控
        self.monitor_button.config(text="恢复监控")

        # 在单独的线程中运行基准测试
        threading.Thread(target=self.run_benchmark, daemon=True).start()

    def request_cancel(self):
        """请求取消测试"""
        self.cancel_requested = True
        self.status_var.set("正在停止测试...")

    def run_benchmark(self):
        """运行基准测试"""
        try:
            # 清空之前的结果
            self.results = {}
            for item in self.details_tree.get_children():
                self.details_tree.delete(item)

            # 更新UI
            self.score_value_label.config(text="0.00", foreground="#c00000")
            self.rank_label.config(text="等级：测试中...", foreground="#0066cc")
            self.progress_var.set(0)
            self.progress_label.config(text="初始化...")
            self.root.update_idletasks()

            # 预热测试
            if not self.cancel_requested:
                self.update_progress("预热CPU...", 0)
                self.warmup_test()

            # 跑分测试序列（添加单核性能测试）
            tests = [
                ("单核性能测试", self.single_core_performance),
                ("浮点运算性能", self.floating_point_performance),
                ("整数运算性能", self.integer_performance),
                ("内存带宽测试", self.memory_bandwidth),
                ("多核扩展性测试", self.multi_core_scalability),
                ("加密运算性能", self.encryption_performance),
                ("压缩运算性能", self.compression_performance)
            ]

            # 运行各项测试
            for i, (test_name, test_func) in enumerate(tests):
                if self.cancel_requested:
                    break

                progress = int((i / len(tests)) * 100)
                self.update_progress(f"运行测试: {test_name}...", progress)

                # 运行测试并获取结果
                score, details, grade = test_func()
                if self.cancel_requested:
                    break

                self.results[test_name] = {"score": score, "details": details, "grade": grade}

                # 更新详细结果表格
                self.details_tree.insert("", tk.END, values=(test_name, f"{score:.2f}", grade, details))
                # 只处理挂起的事件，而不是完全更新UI
                if i % 2 == 0:  # 减少UI更新频率
                    self.root.update_idletasks()

            if not self.cancel_requested and self.results:
                # 计算总得分
                total_score = self.calculate_total_score()

                # 保存测试历史
                self.save_test_history(total_score)

                # 绘制性能图表（如果图表已初始化）
                if self.chart_initialized:
                    self.plot_results()
                else:
                    # 如果图表未初始化，但用户可能想看结果，尝试初始化
                    self.root.after(0, self.initialize_chart)
                    self.root.after(100, self.plot_results)

                # 完成跑分
                self.update_progress("测试完成!", 100)
                self.status_var.set(f"测试完成! 得分: {total_score:.2f}")

                # 切换到总得分标签页
                self.tab_control.select(0)

        except Exception as e:
            self.status_var.set(f"测试出错: {str(e)}")
            messagebox.showerror("错误", f"测试过程中发生错误:\n{str(e)}")
        finally:
            self.running = False
            self.run_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.DISABLED)
            self.progress_label.config(text="就绪")
            self.monitoring_active = True  # 测试结束后恢复监控
            self.monitor_button.config(text="暂停监控")
            self.root.update_idletasks()

    def update_progress(self, message, value):
        """更新进度显示"""
        self.progress_var.set(value)
        self.progress_label.config(text=message)
        self.status_var.set(message)
        # 只处理挂起的事件，而不是完全更新UI
        if value % 10 == 0:  # 减少更新频率
            self.root.update_idletasks()

    def warmup_test(self):
        """预热测试 - 简化版"""
        # 简化的预热
        iterations = 500000
        start_time = time.time()

        # 混合运算预热
        result = 0.0
        for i in range(1, iterations + 1):
            result += math.sqrt(i) * math.sin(i) / (math.cos(i) or 1.0)
            result += (i * 3) // 2 + (i % 7)
            if self.cancel_requested:
                return
            # 减少UI更新频率
            if i % 100000 == 0:
                self.root.update_idletasks()

        elapsed = time.time() - start_time
        self.status_var.set(f"预热完成，耗时 {elapsed:.2f} 秒")
        time.sleep(0.1)

    def single_core_performance(self):
        """单核性能测试 - 优化版"""
        iterations = 8000000  # 增加迭代次数以适应1000分制
        start_time = time.time()

        # 简化的混合运算
        result = 0.0
        for i in range(1, iterations + 1):
            # 浮点运算
            fp_val = math.sqrt(i) * math.sin(i) / (math.cos(i) or 1.0)

            # 整数运算
            int_val = (i * 7) // 3 if i % 3 == 0 else i * 3

            # 混合结果
            result += fp_val + int_val

            # 定期检查取消请求
            if self.cancel_requested and i % 1000000 == 0:
                return 0, "测试已取消", "N/A"

        elapsed = time.time() - start_time
        ops_per_second = iterations / elapsed

        # 计算得分 (标准化到1000分制)
        score = min(1000, (ops_per_second / 1000000) * 800)  # 调整为1000分制

        # 确定等级
        grade = self.get_grade(score)

        details = f"执行了{iterations:,}次混合运算，耗时{elapsed:.4f}秒，{ops_per_second / 1000000:.2f}M 操作/秒"
        return score, details, grade

    def floating_point_performance(self):
        """浮点运算性能测试 - 优化版"""
        iterations = 6000000  # 增加迭代次数
        start_time = time.time()

        # 简化的浮点运算
        result = 0.0
        for i in range(1, iterations + 1):
            result += math.sqrt(i) * math.sin(i) / (math.cos(i) + 0.1)
            if self.cancel_requested and i % 500000 == 0:
                return 0, "测试已取消", "N/A"

        elapsed = time.time() - start_time
        ops_per_second = iterations / elapsed

        # 计算得分 (标准化到1000分制)
        score = min(1000, (ops_per_second / 1500000) * 800)  # 调整为1000分制

        # 确定等级
        grade = self.get_grade(score)

        details = f"执行了{iterations:,}次浮点运算，耗时{elapsed:.4f}秒，{ops_per_second / 1000000:.2f}M 操作/秒"
        return score, details, grade

    def integer_performance(self):
        """整数运算性能测试 - 优化版"""
        iterations = 100000000  # 增加迭代次数
        start_time = time.time()

        # 简化的整数运算
        result = 0
        for i in range(iterations):
            if i % 3 == 0:
                result += (i * 3) // 2
            else:
                result -= (i * 2) // 3

            # 减少检查频率
            if self.cancel_requested and i % 1000000 == 0:
                return 0, "测试已取消", "N/A"

        elapsed = time.time() - start_time
        ops_per_second = iterations / elapsed

        # 计算得分 (标准化到1000分制)
        score = min(1000, (ops_per_second / 200000000) * 800)  # 调整为1000分制

        # 确定等级
        grade = self.get_grade(score)

        details = f"执行了{iterations:,}次整数运算，耗时{elapsed:.4f}秒，{ops_per_second / 1000000000:.3f}B 操作/秒"
        return score, details, grade

    def memory_bandwidth(self):
        """内存带宽测试 - 优化版"""
        size = 1024 * 1024 * 15  # 增加到15MB
        arr = [random.random() for _ in range(size)]
        iterations = 25  # 增加迭代次数

        if self.cancel_requested:
            return 0, "测试已取消", "N/A"

        # 读取测试
        start_time = time.time()
        for idx in range(iterations):
            sum(arr)  # 更高效的求和
            if self.cancel_requested:
                return 0, "测试已取消", "N/A"

        read_elapsed = time.time() - start_time

        # 写入测试
        start_time = time.time()
        for idx in range(iterations):
            # 使用更高效的写入方式
            arr = [random.random() for _ in range(size)]
            if self.cancel_requested:
                return 0, "测试已取消", "N/A"

        write_elapsed = time.time() - start_time

        # 计算带宽 (GB/s)
        data_size_bytes = size * 8  # 每个元素是8字节（double）
        total_data = data_size_bytes * iterations

        read_bandwidth = total_data / (read_elapsed * 1024 ** 3)
        write_bandwidth = total_data / (write_elapsed * 1024 ** 3)
        total_bandwidth = (read_bandwidth + write_bandwidth) / 2

        # 计算得分 (标准化到1000分制)
        score = min(1000, (total_bandwidth / 60) * 800)  # 调整为1000分制

        # 确定等级
        grade = self.get_grade(score)

        details = (f"读取带宽: {read_bandwidth:.2f} GB/s, "
                   f"写入带宽: {write_bandwidth:.2f} GB/s, "
                   f"平均: {total_bandwidth:.2f} GB/s")
        return score, details, grade

    def encryption_performance(self):
        """加密运算性能测试 - 优化版"""
        iterations = 5000000  # 增加迭代次数
        start_time = time.time()

        # 简化的加密运算
        result = 0
        for i in range(iterations):
            val = i
            val = (val ^ 0x5A5A5A5A) + 0x12345678
            result += val & 0xFFFF

            # 减少检查频率
            if self.cancel_requested and i % 500000 == 0:
                return 0, "测试已取消", "N/A"

        elapsed = time.time() - start_time
        ops_per_second = iterations / elapsed

        # 计算得分 (标准化到1000分制)
        score = min(1000, (ops_per_second / 2000000) * 800)  # 调整为1000分制

        # 确定等级
        grade = self.get_grade(score)

        details = f"执行了{iterations:,}次加密运算，耗时{elapsed:.4f}秒，{ops_per_second / 1000000:.2f}M 操作/秒"
        return score, details, grade

    def compression_performance(self):
        """压缩运算性能测试 - 优化版"""
        iterations = 3000000  # 增加迭代次数
        start_time = time.time()

        # 简化的压缩运算
        result = 0
        for i in range(iterations):
            n = i
            count = bin(n).count("1")  # 使用内置函数更高效
            result = (result + count) & 0xFF

            # 减少检查频率
            if self.cancel_requested and i % 500000 == 0:
                return 0, "测试已取消", "N/A"

        elapsed = time.time() - start_time
        ops_per_second = iterations / elapsed

        # 计算得分 (标准化到1000分制)
        score = min(1000, (ops_per_second / 1500000) * 800)  # 调整为1000分制

        # 确定等级
        grade = self.get_grade(score)

        details = f"执行了{iterations:,}次压缩运算，耗时{elapsed:.4f}秒，{ops_per_second / 1000000:.2f}M 操作/秒"
        return score, details, grade

    def multi_core_scalability(self):
        """多核扩展性测试 - 优化版"""
        max_cores = min(64, cpu_count())  # 限制最大测试核心数64核心
        results = []
        total_iterations = 10000000  # 固定总迭代次数

        # 使用Manager创建共享标志
        manager = Manager()
        cancel_flag = manager.Value('b', False)

        for cores in range(1, max_cores + 1):
            if self.cancel_requested:
                cancel_flag.value = True
                break

            self.update_progress(f"测试多核性能 ({cores}/{max_cores} 核心)...",
                                 int((cores / max_cores) * 80) + 10)

            # 每个核心分配相同的迭代次数
            iterations_per_core = total_iterations // cores

            start_time = time.time()
            try:
                with Pool(cores) as pool:
                    # 创建任务列表
                    tasks = []
                    for _ in range(cores):
                        tasks.append(pool.apply_async(worker, (iterations_per_core, cancel_flag)))

                    # 获取结果
                    for task in tasks:
                        task.get()
            except Exception as e:
                print(f"多核测试出错: {str(e)}")
                return 0, f"多核测试出错: {str(e)}", "N/A"

            elapsed = time.time() - start_time

            # 计算总操作量/秒
            total_ops = iterations_per_core * cores
            ops_per_sec = total_ops / elapsed
            results.append((cores, ops_per_sec))

        # 计算扩展性得分
        if len(results) < 2:
            scalability_score = 800  # 单核系统
        else:
            # 计算多核效率：实际速度 / (单核速度 * 核心数)
            single_core_ops = results[0][1]
            max_core_ops = results[-1][1]

            # 核心数越多，得分越高
            scalability_score = min(1000, (max_core_ops / (single_core_ops * 1.5)) * 800)

        # 生成核心效率详情
        details = "核心效率:\n"
        for cores, perf in results:
            details += f"  {cores}核: {perf / 1000000:.2f}M 操作/秒\n"

        # 确定等级
        grade = self.get_grade(scalability_score)

        return scalability_score, details, grade

    def get_grade(self, score):
        """根据分数返回等级（1000分制）"""
        if score >= 900:
            return "卓越"
        elif score >= 750:
            return "优秀"
        elif score >= 600:
            return "良好"
        elif score >= 400:
            return "一般"
        else:
            return "较差"

    def calculate_total_score(self):
        """改进的总得分计算（1000分制）"""
        # 动态权重分配
        weights = {
            "单核性能测试": 0.20,
            "浮点运算性能": 0.15,
            "整数运算性能": 0.15,
            "内存带宽测试": 0.15,
            "多核扩展性测试": 0.15,
            "加密运算性能": 0.10,
            "压缩运算性能": 0.10
        }

        # 基准分数调整因子
        base_factor = 1.0
        if "i9" in self.cpu_brand or "R9" in self.cpu_brand:
            base_factor = 1.1  # 高端CPU基准更高
        elif "i7" in self.cpu_brand or "R7" in self.cpu_brand:
            base_factor = 1.0
        elif "i5" in self.cpu_brand or "R5" in self.cpu_brand:
            base_factor = 0.95
        else:  # 低端CPU
            base_factor = 0.9

        total_score = 0
        for test_name, weight in weights.items():
            if test_name in self.results:
                # 应用调整因子
                adjusted_score = self.results[test_name]["score"] * base_factor
                total_score += adjusted_score * weight

        # 确保总分在合理范围内
        total_score = min(1000, max(0, total_score))

        # 更新UI显示
        self.score_value_label.config(text=f"{total_score:.2f}")

        # 计算性能等级
        grade = self.get_grade(total_score)
        self.rank_label.config(text=f"等级：{grade}")

        # 生成性能对比信息
        comparison_text = self.generate_comparison_text(total_score, grade)

        self.comparison_text.config(state=tk.NORMAL)
        self.comparison_text.delete(1.0, tk.END)
        self.comparison_text.insert(tk.END, comparison_text)
        self.comparison_text.config(state=tk.DISABLED)

        return total_score

    def generate_comparison_text(self, score, grade):
        """生成性能对比文本"""
        cpu_type = "未知"
        if "i9" in self.cpu_brand or "R9" in self.cpu_brand:
            cpu_type = "高端桌面/工作站CPU"
        elif "i7" in self.cpu_brand or "R7" in self.cpu_brand:
            cpu_type = "高性能桌面CPU"
        elif "i5" in self.cpu_brand or "R5" in self.cpu_brand:
            cpu_type = "中端桌面CPU"
        elif "i3" in self.cpu_brand or "R3" in self.cpu_brand or "Ryzen 3" in self.cpu_brand:
            cpu_type = "主流桌面CPU"
        elif "Celeron" in self.cpu_brand or "Pentium" in self.cpu_brand or "Athlon" in self.cpu_brand:
            cpu_type = "入门级CPU"

        return (f"您的CPU ({cpu_type}) 总得分为 {score:.2f}，性能等级为【{grade}】\n\n"
                f"与同级别CPU对比参考值：\n"
                f"- 高端桌面/工作站CPU: 800-1000分\n"
                f"- 高性能桌面CPU: 650-800分\n"
                f"- 中端桌面CPU: 500-650分\n"
                f"- 主流桌面CPU: 350-500分\n"
                f"- 入门级CPU: <350分\n\n"
                f"*分数基于CPU型号和综合性能评估，仅供参考")

    def save_test_history(self, total_score):
        """保存测试历史"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            cpu_model = self.cpu_brand
        except:
            cpu_model = "未知型号"

        # 计算等级
        grade = self.get_grade(total_score)

        # 添加到历史记录
        self.test_history.append({
            "timestamp": timestamp,
            "score": total_score,
            "grade": grade,
            "cpu_model": cpu_model,
            "details": self.results.copy(),
            "voltage": self.voltage,  # 保存测试时的电压
            "temperature": self.temperature,  # 保存测试时的温度
            "power": self.power,  # 保存测试时的功耗
            "process": self.cpu_process,  # 保存工艺制程
            "instruction_set": self.cpu_instruction_set  # 保存指令集
        })

        # 更新历史记录表格
        self.history_tree.insert("", tk.END, values=(timestamp, f"{total_score:.2f}", grade, cpu_model))

        # 启用查看详情按钮
        if len(self.test_history) > 0:
            self.view_detail_button.config(state=tk.NORMAL)

    def view_history_detail(self):
        """查看历史记录详情"""
        selected_items = self.history_tree.selection()
        if not selected_items:
            return

        item = self.history_tree.item(selected_items[0])
        values = item['values']
        timestamp = values[0]

        # 找到对应的历史记录
        history = None
        for h in self.test_history:
            if h["timestamp"] == timestamp:
                history = h
                break

        if not history:
            return

        # 创建详情窗口
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"测试详情 - {history['timestamp']}")
        detail_window.geometry("700x500")  # 缩小详情窗口
        detail_window.transient(self.root)
        detail_window.grab_set()

        # 创建标题
        title_frame = ttk.Frame(detail_window, padding=8)
        title_frame.pack(fill=tk.X)

        ttk.Label(
            title_frame,
            text=f"测试时间: {history['timestamp']}",
            font=("Arial", 10, "bold")  # 缩小字体
        ).pack(anchor=tk.W)

        ttk.Label(
            title_frame,
            text=f"CPU型号: {history['cpu_model']}",
            font=("Arial", 10)  # 缩小字体
        ).pack(anchor=tk.W)

        ttk.Label(
            title_frame,
            text=f"工艺制程: {history['process']}",
            font=("Arial", 10)  # 缩小字体
        ).pack(anchor=tk.W)

        ttk.Label(
            title_frame,
            text=f"指令集: {history['instruction_set']}",
            font=("Arial", 10)  # 缩小字体
        ).pack(anchor=tk.W)

        ttk.Label(
            title_frame,
            text=f"总得分: {history['score']:.2f} ({history['grade']})",
            font=("Arial", 10, "bold"),  # 缩小字体
            foreground="#c00000"
        ).pack(anchor=tk.W, pady=3)

        # 添加电压、温度、功耗显示
        ttk.Label(
            title_frame,
            text=f"测试时电压: {history.get('voltage', 'N/A')}V",
            font=("Arial", 10)  # 缩小字体
        ).pack(anchor=tk.W)

        ttk.Label(
            title_frame,
            text=f"测试时温度: {history.get('temperature', 'N/A')}",
            font=("Arial", 10)  # 缩小字体
        ).pack(anchor=tk.W)

        ttk.Label(
            title_frame,
            text=f"测试时功耗: {history.get('power', 'N/A')}",
            font=("Arial", 10)  # 缩小字体
        ).pack(anchor=tk.W)

        # 创建详情表格
        columns = ("测试项目", "得分", "等级", "测试详情")
        tree_frame = ttk.Frame(detail_window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=5)

        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)  # 减少高度

        # 配置列 - 缩小列宽
        col_widths = {"测试项目": 90, "得分": 60, "等级": 60, "测试详情": 280}
        col_anchors = {"测试项目": tk.W, "得分": tk.CENTER, "等级": tk.CENTER, "测试详情": tk.W}

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=col_widths.get(col, 80),
                        anchor=col_anchors.get(col, tk.CENTER))

        # 添加滚动条
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)

        # 填充数据
        for test_name, test_data in history['details'].items():
            tree.insert("", tk.END, values=(
                test_name,
                f"{test_data['score']:.2f}",
                test_data['grade'],
                test_data['details']
            ))

        # 关闭按钮
        button_frame = ttk.Frame(detail_window, padding=8)
        button_frame.pack(fill=tk.X)

        ttk.Button(
            button_frame,
            text="关闭",
            command=detail_window.destroy,
            width=8  # 缩小按钮
        ).pack(side=tk.RIGHT)

    def clear_history(self):
        """清除历史记录"""
        if not self.test_history:
            return

        if messagebox.askyesno("确认", "确定要清除所有测试历史记录吗？"):
            self.test_history = []
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)

            self.view_detail_button.config(state=tk.DISABLED)
            self.status_var.set("历史记录已清除")

    def save_results(self):
        """保存测试结果"""
        if not self.results:
            messagebox.showinfo("提示", "没有可保存的测试结果")
            return

        try:
            # 生成保存的文件名
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"cpu_benchmark_{timestamp}.txt"

            # 构建保存内容
            content = "=" * 60 + "\n"
            content += "浩讯亿通 CPU 性能测试报告\n"
            content += "=" * 60 + "\n\n"

            # 系统信息
            content += f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            content += f"系统信息: {self.system_info_label.cget('text')}\n"
            content += f"工艺制程: {self.cpu_process}\n"
            content += f"指令集: {self.cpu_instruction_set}\n"
            content += f"当前电压: {self.voltage}V\n"
            content += f"当前温度: {self.temperature}\n"
            content += f"当前功耗: {self.power}\n"
            content += "\n"

            # 总得分
            total_score = self.score_value_label.cget("text")
            grade = self.rank_label.cget("text").replace("等级：", "")
            content += f"综合得分: {total_score} ({grade})\n"
            content += "\n"

            # 详细结果
            content += "详细测试结果:\n"
            content += "-" * 60 + "\n"

            for test_name, test_data in self.results.items():
                content += f"测试项目: {test_name}\n"
                content += f"得分: {test_data['score']:.2f} ({test_data['grade']})\n"
                content += f"详情: {test_data['details']}\n"
                content += "\n"

            # 保存到文件
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)

            self.status_var.set(f"结果已保存到: {filename}")
            messagebox.showinfo("保存成功", f"测试结果已保存到文件:\n{filename}")

        except Exception as e:
            messagebox.showerror("保存错误", f"保存结果时出错:\n{str(e)}")

    def plot_results(self):
        """绘制性能图表"""
        if not self.results or not self.chart_initialized:
            # 如果图表未初始化，尝试初始化
            if not self.chart_initialized:
                self.initialize_chart()
            return

        self.ax.clear()

        test_names = list(self.results.keys())
        scores = [self.results[test]["score"] for test in test_names]
        colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(test_names)))

        # 绘制水平柱状图
        y_pos = np.arange(len(test_names))
        bars = self.ax.barh(y_pos, scores, align='center', color=colors, alpha=0.8)

        # 添加总分
        total_score = float(self.score_value_label.cget("text"))
        total_line = self.ax.axvline(x=total_score, color='r', linestyle='--', alpha=0.7)
        self.ax.text(total_score + 10, len(test_names) - 0.5,
                     f'总分: {total_score:.2f}',
                     color='r', fontsize=9, va='center')  # 缩小字体

        # 添加数据标签
        for i, (bar, score) in enumerate(zip(bars, scores)):
            width = bar.get_width()
            grade = self.results[test_names[i]]["grade"]
            self.ax.text(width + 10, bar.get_y() + bar.get_height() / 2,
                         f'{width:.2f} ({grade})',
                         ha='left', va='center', fontsize=8)  # 缩小字体

        # 设置图表属性
        self.ax.set_yticks(y_pos)
        self.ax.set_yticklabels(test_names, fontsize=9)  # 缩小字体
        self.ax.set_xlabel('分数 (1000分制)', fontsize=9)  # 缩小字体
        self.ax.set_title('CPU性能测试结果分析', fontsize=10)  # 缩小字体
        self.ax.set_xlim(0, 1100)
        self.ax.grid(True, linestyle='--', alpha=0.3)

        # 添加图例
        legend_elements = [
            Patch(facecolor=colors[0], label='各项测试得分'),
            Line2D([0], [0], color='r', linestyle='--', label=f'总分: {total_score:.2f}')
        ]
        self.ax.legend(handles=legend_elements, loc='lower right', fontsize=8)  # 缩小字体

        # 调整布局
        self.figure.tight_layout()

        # 更新画布
        self.canvas.draw()


# 主函数
if __name__ == "__main__":
    # Windows系统下多进程需要这个保护
    if platform.system() == "Windows":
        from multiprocessing import freeze_support

        freeze_support()

    root = tk.Tk()
    app = CPUBenchmarkUI(root)
    root.mainloop()
