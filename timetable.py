# -*- coding: utf-8 -*-
"""
课程作业管理 GUI 程序
- 课表显示：周一至周五，每天 13 节课
- 支持手动添加 / 编辑 / 删除课程
- 预加载示例课程数据
"""

import ctypes
import re
import tkinter as tk
from tkinter import ttk, messagebox


def enable_high_dpi():
    """在 Windows 上启用高 DPI 感知，避免界面模糊、发虚。"""
    try:
        # Per-Monitor DPI Aware (Windows 8.1+)
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            # 降级：System DPI Aware (Windows Vista+)
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

DAYS = ["星期一", "星期二", "星期三", "星期四", "星期五"]
PERIODS = 13
MAX_WEEK = 16

# 课程卡片配色（按课程名循环分配）
COLORS = [
    "#E3F2FD", "#BBDEFB", "#90CAF9", "#64B5F6", "#42A5F5",
    "#E8EAF6", "#C5CAE9", "#9FA8DA", "#7986CB", "#5C6BC0",
    "#E1F5FE", "#B3E5FC", "#81D4FA", "#4FC3F7", "#29B6F6",
]


def parse_weeks(text):
    """把 '1-12周' / '第1周' 解析成周次集合"""
    text = text.replace("第", "").strip()
    result = set()
    for part in text.split(","):
        part = part.strip()
        m = re.match(r"(\d+)(?:-(\d+))?周?", part)
        if m:
            a = int(m.group(1))
            b = int(m.group(2)) if m.group(2) else a
            result.update(range(a, b + 1))
    return result


class Course:
    def __init__(self, name, day, start, end, weeks, campus, location):
        self.name = name
        self.day = day          # 0..4
        self.start = start      # 1..13
        self.end = end          # 1..13
        self.weeks = weeks      # 原始字符串，如 "1-12周"
        self.campus = campus
        self.location = location
        self._week_set = parse_weeks(weeks)

    def active_in_week(self, week):
        return week in self._week_set

    def period_text(self):
        return f"{self.start}-{self.end}节"


def sample_courses():
    data = [
        # 星期一
        ("生产计划与控制", 0, 3, 4, "1-12周", "闵行", "下院312"),
        ("计算复杂性", 0, 1, 2, "1-12周", "闵行", "东下院402"),
        ("生产系统建模与仿真", 0, 6, 8, "第1周", "闵行", "东下院102"),
        ("生产系统建模与仿真", 0, 6, 8, "2-16周", "闵行", "东中院3-206"),
        ("新兴风险的感知与沟通", 0, 9, 10, "1-16周", "闵行", "上院501"),
        ("大数据算法与分析", 0, 11, 13, "1-16周", "闵行", "下院113"),
        # 星期二
        ("优化算法设计", 1, 3, 4, "1-8周", "闵行", "东下院202"),
        ("管理学基础", 1, 7, 8, "1-12周", "闵行", "东下院202"),
        ("日语（1）", 1, 9, 10, "1-16周", "闵行", "上院404"),
        ("软件工程", 1, 11, 13, "1-16周", "闵行", "上院203"),
        # 星期三
        ("人因工程", 2, 3, 4, "1-12周", "闵行", "下院312"),
        ("中国医疗保险制度的转型发展与创新", 2, 11, 13, "5-15周", "闵行", "上院203"),
        # 星期四
        ("计算复杂性", 3, 1, 2, "1-12周", "闵行", "东下院311"),
        ("生产计划与控制", 3, 3, 4, "1-12周", "闵行", "下院312"),
        ("毛泽东思想和中国特色社会主义理论体系概论", 3, 6, 8, "1-16周", "闵行", "上院115"),
        ("日语（1）", 3, 9, 10, "1-16周", "闵行", "上院404"),
        ("优化算法设计", 3, 12, 13, "1-8周", "闵行", "东下院202"),
        # 星期五
        ("人因工程", 4, 1, 2, "1-12周", "闵行", "下院312"),
        ("管理学基础", 4, 3, 4, "1-12周", "闵行", "东下院202"),
        ("工程与社会", 4, 7, 9, "1-11周", "闵行", "东下院309"),
    ]
    return [Course(*row) for row in data]


class CourseDialog(tk.Toplevel):
    """添加 / 编辑课程对话框"""

    def __init__(self, master, course=None):
        super().__init__(master)
        self.course = course
        self.result = None
        self.title("编辑课程" if course else "添加课程")
        self.resizable(False, False)
        self.grab_set()

        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="课程名称:").grid(row=0, column=0, sticky="e", pady=4)
        self.name_var = tk.StringVar(value=course.name if course else "")
        ttk.Entry(frm, textvariable=self.name_var, width=28).grid(row=0, column=1, pady=4, sticky="we")

        ttk.Label(frm, text="星期:").grid(row=1, column=0, sticky="e", pady=4)
        self.day_var = tk.StringVar(value=DAYS[course.day] if course else DAYS[0])
        ttk.Combobox(frm, textvariable=self.day_var, values=DAYS,
                     state="readonly", width=10).grid(row=1, column=1, sticky="w", pady=4)

        ttk.Label(frm, text="起始节次:").grid(row=2, column=0, sticky="e", pady=4)
        self.start_var = tk.IntVar(value=course.start if course else 1)
        ttk.Combobox(frm, textvariable=self.start_var, values=list(range(1, PERIODS + 1)),
                     state="readonly", width=10).grid(row=2, column=1, sticky="w", pady=4)

        ttk.Label(frm, text="结束节次:").grid(row=3, column=0, sticky="e", pady=4)
        self.end_var = tk.IntVar(value=course.end if course else 1)
        ttk.Combobox(frm, textvariable=self.end_var, values=list(range(1, PERIODS + 1)),
                     state="readonly", width=10).grid(row=3, column=1, sticky="w", pady=4)

        ttk.Label(frm, text="周次:").grid(row=4, column=0, sticky="e", pady=4)
        self.weeks_var = tk.StringVar(value=course.weeks if course else "1-16周")
        ttk.Entry(frm, textvariable=self.weeks_var, width=28).grid(row=4, column=1, pady=4, sticky="we")

        ttk.Label(frm, text="校区:").grid(row=5, column=0, sticky="e", pady=4)
        self.campus_var = tk.StringVar(value=course.campus if course else "闵行")
        ttk.Entry(frm, textvariable=self.campus_var, width=28).grid(row=5, column=1, pady=4, sticky="we")

        ttk.Label(frm, text="上课地点:").grid(row=6, column=0, sticky="e", pady=4)
        self.loc_var = tk.StringVar(value=course.location if course else "")
        ttk.Entry(frm, textvariable=self.loc_var, width=28).grid(row=6, column=1, pady=4, sticky="we")

        btn = ttk.Frame(frm)
        btn.grid(row=7, column=0, columnspan=2, pady=(12, 0))
        ttk.Button(btn, text="确定", command=self.on_ok).pack(side="left", padx=6)
        ttk.Button(btn, text="取消", command=self.destroy).pack(side="left", padx=6)

        self.bind("<Return>", lambda e: self.on_ok())
        self.bind("<Escape>", lambda e: self.destroy())

    def on_ok(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("提示", "请输入课程名称", parent=self)
            return
        day = DAYS.index(self.day_var.get())
        start = int(self.start_var.get())
        end = int(self.end_var.get())
        if start > end:
            messagebox.showwarning("提示", "起始节次不能大于结束节次", parent=self)
            return
        weeks = self.weeks_var.get().strip() or "1-16周"
        campus = self.campus_var.get().strip()
        location = self.loc_var.get().strip()
        self.result = Course(name, day, start, end, weeks, campus, location)
        self.destroy()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        # 按系统 DPI 设置 Tk 缩放，让字体/控件以原生分辨率渲染
        try:
            dpi = ctypes.windll.user32.GetDpiForSystem()
            self.tk.call("tk", "scaling", dpi / 72.0)
        except Exception:
            pass

        self.title("课程作业管理")
        self.geometry("1400x900")
        self.minsize(1100, 700)

        self.courses = sample_courses()
        self.color_map = {}
        self.current_week = tk.IntVar(value=1)
        self.filter_by_week = tk.BooleanVar(value=False)
        self._resize_job = None

        self._build_ui()
        self.refresh()

    # ---------- UI 构建 ----------
    def _build_ui(self):
        # 顶部工具栏
        bar = ttk.Frame(self, padding=(10, 8))
        bar.pack(fill="x")

        ttk.Label(bar, text="课程作业管理", font=("Microsoft YaHei", 14, "bold")).pack(side="left")
        ttk.Button(bar, text="➕ 添加课程", command=self.add_course).pack(side="left", padx=(20, 6))
        ttk.Button(bar, text="✏️ 编辑选中", command=self.edit_selected).pack(side="left", padx=6)
        ttk.Button(bar, text="🗑 删除选中", command=self.delete_selected).pack(side="left", padx=6)
        ttk.Button(bar, text="↺ 恢复示例", command=self.reset_sample).pack(side="left", padx=6)

        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=12)
        ttk.Label(bar, text="当前周次:").pack(side="left")
        ttk.Spinbox(bar, from_=1, to=MAX_WEEK, textvariable=self.current_week,
                    width=5, command=self.refresh).pack(side="left", padx=4)
        ttk.Checkbutton(bar, text="仅显示本周课程", variable=self.filter_by_week,
                        command=self.refresh).pack(side="left", padx=6)

        # 主体：左侧课表 + 右侧课程列表
        body = ttk.Panedwindow(self, orient="horizontal")
        body.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # 课表（可滚动）
        outer = ttk.Frame(body)
        body.add(outer, weight=3)

        self.canvas = tk.Canvas(outer, highlightthickness=0)
        vsb = ttk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vsb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.timetable_frame = ttk.Frame(self.canvas)
        self.timetable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.timetable_frame, anchor="nw"
        )
        # 画布尺寸变化时，拉伸内部课表框架宽度并按比例重渲染内容
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # 右侧课程列表
        right = ttk.Frame(body)
        body.add(right, weight=2)

        ttk.Label(right, text="课程列表", font=("Microsoft YaHei", 11, "bold")).pack(anchor="w", pady=(0, 4))
        cols = ("name", "day", "period", "weeks", "location")
        tree_frame = ttk.Frame(right)
        tree_frame.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=20)
        self.tree.heading("name", text="课程名称")
        self.tree.heading("day", text="星期")
        self.tree.heading("period", text="节次")
        self.tree.heading("weeks", text="周次")
        self.tree.heading("location", text="地点")
        # 课程名称列可拉伸吸收多余宽度，其余列固定，避免长名称覆盖相邻列
        self.tree.column("name", width=200, stretch=True)
        self.tree.column("day", width=60, anchor="center", stretch=False)
        self.tree.column("period", width=60, anchor="center", stretch=False)
        self.tree.column("weeks", width=80, anchor="center", stretch=False)
        self.tree.column("location", width=110, stretch=False)
        vsb_t = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb_t = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb_t.set, xscrollcommand=hsb_t.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb_t.grid(row=0, column=1, sticky="ns")
        hsb_t.grid(row=1, column=0, sticky="ew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        self.tree.bind("<Double-1>", lambda e: self.edit_selected())

    # ---------- 数据与渲染 ----------
    def color_for(self, name):
        if name not in self.color_map:
            self.color_map[name] = COLORS[len(self.color_map) % len(COLORS)]
        return self.color_map[name]

    def visible_courses(self):
        if not self.filter_by_week.get():
            return list(self.courses)
        w = self.current_week.get()
        return [c for c in self.courses if c.active_in_week(w)]

    def _get_scale(self):
        """根据课表画布宽度计算内容缩放系数（窗口越大，字号/行高越大）。"""
        w = self.canvas.winfo_width()
        if w < 50:
            w = 800
        return max(0.85, min(2.2, w / 760.0))

    def _on_canvas_configure(self, event):
        # 让课表内部框架宽高都跟随画布，行列均匀撑满整个区域
        self.canvas.itemconfig(self.canvas_window, width=event.width, height=event.height)
        # 防抖：窗口尺寸变化结束后再重渲染，避免拖动时频繁刷新
        if self._resize_job is not None:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(120, self.refresh)

    def refresh(self):
        self._render_timetable()
        self._render_list()

    def _render_timetable(self):
        for w in self.timetable_frame.winfo_children():
            w.destroy()

        courses = self.visible_courses()

        # 按窗口大小计算缩放后的尺寸
        scale = self._get_scale()
        font_head = max(9, int(10 * scale))
        font_card = max(8, int(9 * scale))
        pad = max(3, int(6 * scale))
        row_min = max(36, int(46 * scale))
        wrap = max(80, int(140 * scale))
        # 行高不超过画布可用高度，避免内容溢出被裁切
        canvas_h = self.canvas.winfo_height()
        if canvas_h > 100:
            row_min = min(row_min, (canvas_h - 50) // PERIODS)
        # 课程卡片含 3 行文字，字号受行高约束，避免文字塞满格子
        font_card = min(font_card, max(8, (row_min - pad * 2) // 4))
        font_head = min(font_head, font_card + 2)

        # 表头
        header = ttk.Label(self.timetable_frame, text="节次", relief="ridge",
                           font=("Microsoft YaHei", font_head, "bold"), padding=pad)
        header.grid(row=0, column=0, sticky="nsew")
        for d, name in enumerate(DAYS):
            lbl = ttk.Label(self.timetable_frame, text=name, relief="ridge",
                            font=("Microsoft YaHei", font_head, "bold"), padding=pad)
            lbl.grid(row=0, column=d + 1, sticky="nsew")

        # 节次标签
        for p in range(1, PERIODS + 1):
            ttk.Label(self.timetable_frame, text=str(p), relief="ridge",
                      font=("Microsoft YaHei", font_head),
                      padding=pad, anchor="center").grid(row=p, column=0, sticky="nsew")

        # 占用矩阵
        slot = [[[] for _ in range(PERIODS + 1)] for _ in range(5)]
        for c in courses:
            for p in range(c.start, c.end + 1):
                if 1 <= p <= PERIODS:
                    slot[c.day][p].append(c)

        week = self.current_week.get()

        for d in range(5):
            p = 1
            while p <= PERIODS:
                cell_courses = slot[d][p]
                q = p
                while q + 1 <= PERIODS and set(slot[d][q + 1]) == set(cell_courses):
                    q += 1
                rowspan = q - p + 1

                cell = tk.Frame(self.timetable_frame, bg="#ECEFF1",
                                highlightthickness=1, highlightbackground="#CFD8DC")
                cell.grid(row=p, column=d + 1, rowspan=rowspan, sticky="nsew", padx=1, pady=1)

                for c in cell_courses:
                    active = c.active_in_week(week)
                    color = self.color_for(c.name) if active else "#E0E0E0"
                    fg = "#000000" if active else "#9E9E9E"
                    text = f"{c.name}\n{c.weeks}\n{c.location}"
                    lbl = tk.Label(cell, text=text, bg=color, fg=fg,
                                   font=("Microsoft YaHei", font_card), justify="center",
                                   wraplength=wrap, padx=pad // 2, pady=pad // 2)
                    lbl.pack(fill="both", expand=True, padx=1, pady=1)
                    lbl.bind("<Double-Button-1>", lambda e, co=c: self.open_edit(co))
                    lbl.bind("<Button-3>", lambda e, co=c: self.ask_delete(co))
                p = q + 1

        # 列宽 / 行高配置
        self.timetable_frame.grid_columnconfigure(0, weight=0)
        for d in range(1, 6):
            self.timetable_frame.grid_columnconfigure(d, weight=1, uniform="day")
        for r in range(1, PERIODS + 1):
            self.timetable_frame.grid_rowconfigure(r, weight=1, uniform="period", minsize=row_min)

        self.timetable_frame.update_idletasks()

    def _render_list(self):
        # 让课程列表字号与行高随窗口缩放
        scale = self._get_scale()
        font_size = max(9, int(10 * scale))
        row_h = max(22, int(26 * scale))
        style = ttk.Style()
        style.configure("Treeview", font=("Microsoft YaHei", font_size), rowheight=row_h)
        style.configure("Treeview.Heading",
                        font=("Microsoft YaHei", font_size, "bold"))

        # 列宽随缩放调整（名称列可拉伸，其余固定）
        widths = {
            "name": int(200 * scale), "day": int(60 * scale),
            "period": int(60 * scale), "weeks": int(80 * scale),
            "location": int(110 * scale),
        }
        for col, w in widths.items():
            self.tree.column(col, width=w)

        for item in self.tree.get_children():
            self.tree.delete(item)
        for c in self.courses:
            self.tree.insert("", "end", iid=str(id(c)), values=(
                c.name, DAYS[c.day], c.period_text(), c.weeks, c.location,
            ))

    # ---------- 增删改 ----------
    def add_course(self):
        dlg = CourseDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            self.courses.append(dlg.result)
            self.refresh()

    def open_edit(self, course):
        dlg = CourseDialog(self, course)
        self.wait_window(dlg)
        if dlg.result:
            idx = self.courses.index(course)
            self.courses[idx] = dlg.result
            self.refresh()

    def edit_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("提示", "请先在右侧列表中选择一门课程")
            return
        course = next(c for c in self.courses if str(id(c)) == sel[0])
        self.open_edit(course)

    def ask_delete(self, course):
        if messagebox.askyesno("删除课程", f"确定删除「{course.name}」吗？"):
            self.courses.remove(course)
            self.refresh()

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("提示", "请先在右侧列表中选择一门课程")
            return
        course = next(c for c in self.courses if str(id(c)) == sel[0])
        self.ask_delete(course)

    def reset_sample(self):
        if messagebox.askyesno("恢复示例", "将清除当前所有课程并恢复为示例课表，确定吗？"):
            self.courses = sample_courses()
            self.refresh()


if __name__ == "__main__":
    enable_high_dpi()
    App().mainloop()
