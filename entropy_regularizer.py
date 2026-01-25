"""
Entropy Regularizer 可视化动画
运行命令:
  完整动画: manim -pql entropy_regularizer.py EntropyRegularizer
  单独场景: manim -pql entropy_regularizer.py Scene1Title
           manim -pql entropy_regularizer.py Scene2DistributionSpreading
           manim -pql entropy_regularizer.py Scene3LossFunction
           manim -pql entropy_regularizer.py Scene4ExitDistribution
           manim -pql entropy_regularizer.py Scene5PriorDistribution
           manim -pql entropy_regularizer.py Scene6KLDivergence
           manim -pql entropy_regularizer.py Scene7BetaCoefficient
           manim -pql entropy_regularizer.py Scene8PonderNetGeometric
           manim -pql entropy_regularizer.py Scene9KVCacheTransition
  高质量渲染: manim -pqh entropy_regularizer.py EntropyRegularizer
"""

from manim import *
import numpy as np

# ===== 颜色配置 =====
COLORS = {
    'background': '#0d1117',
    'primary_text': '#ffffff',
    'secondary_text': '#8b949e',
    'accent_blue': '#58a6ff',
    'accent_teal': '#3fb950',
    'warning_red': '#f85149',
    'highlight_yellow': '#d29922',
    'grid': '#2d333b',
    'uniform_prior': '#58a6ff',
    'geometric_prior': '#8b949e',
    'formula_purple': '#9B59B6',
}

# 简化颜色引用
EXIT_COLOR = COLORS['warning_red']
SURVIVE_COLOR = COLORS['accent_teal']
HIGHLIGHT_COLOR = COLORS['highlight_yellow']
LOOP_COLOR = COLORS['accent_blue']
FORMULA_COLOR = COLORS['formula_purple']
SECONDARY_TEXT = COLORS['secondary_text']


# ===== Scene 1: Section Title =====
class Scene1Title(Scene):
    """Scene 1: Section Title (2 seconds)"""
    def construct(self):
        # 设置纯黑色背景
        self.camera.background_color = BLACK

        # 背景渐变效果 - 使用深蓝到黑色
        # Manim 默认背景，我们通过添加渐变矩形实现

        # 标题
        title = Tex(
            r"\textbf{Entropy Regularizer}",
            font_size=72,
            color=WHITE
        )
        title.scale(0.95)  # 初始稍小

        # 动画：淡入并轻微放大
        self.play(
            FadeIn(title, scale=0.95),
            title.animate.scale(1.0 / 0.95),
            run_time=1
        )

        # 保持1秒
        self.wait(1)

        # 淡出
        self.play(FadeOut(title), run_time=0.5)


# ===== Scene 2: Distribution Spreading =====
class Scene2DistributionSpreading(Scene):
    """Scene 2: The Core Solution — Distribution Spreading (6 seconds)
    使用折线图，并做 in-place 变换从 spiky 到 uniform
    """
    def construct(self):
        # 设置纯黑色背景
        self.camera.background_color = BLACK

        # 数据
        before_probs = [0.02, 0.03, 0.05, 0.90]  # 坍塌分布 (spiky)
        after_probs = [0.22, 0.28, 0.25, 0.25]   # 均匀分布
        steps = [1, 2, 3, 4]

        # 坐标轴参数
        chart_width = 8
        chart_height = 4

        # 创建坐标轴（居中）
        axes = Axes(
            x_range=[0, 5, 1],
            y_range=[0, 1.0, 0.2],
            x_length=chart_width,
            y_length=chart_height,
            axis_config={"color": SECONDARY_TEXT, "include_tip": False},
            y_axis_config={"include_numbers": True, "font_size": 20},
        )
        axes.shift(DOWN * 0.3)

        # X轴标签
        x_labels = VGroup()
        for i, step in enumerate(steps):
            label = Tex(str(step), font_size=20, color=SECONDARY_TEXT)
            label.move_to(axes.c2p(i + 1, 0) + DOWN * 0.35)
            x_labels.add(label)

        # X轴标题
        x_title = Tex(r"Loop Step", font_size=18, color=SECONDARY_TEXT)
        x_title.next_to(axes.x_axis, DOWN, buff=0.6)

        # Y轴标题
        y_title = MathTex(r"p(t|x)", font_size=26, color=SECONDARY_TEXT)
        y_title.next_to(axes.y_axis, UP, buff=0.2)

        # ===== 创建折线图（spiky 分布）=====
        # 创建点
        before_points = [axes.c2p(i + 1, prob) for i, prob in enumerate(before_probs)]
        after_points = [axes.c2p(i + 1, prob) for i, prob in enumerate(after_probs)]

        # 创建折线
        before_line = VMobject(color=EXIT_COLOR, stroke_width=4)
        before_line.set_points_as_corners(before_points)

        # 创建点标记
        before_dots = VGroup()
        for point in before_points:
            dot = Dot(point, color=EXIT_COLOR, radius=0.1)
            before_dots.add(dot)

        # 显示坐标轴
        self.play(Create(axes), Write(x_title), Write(y_title), run_time=0.6)
        self.play(
            LaggedStart(*[Write(l) for l in x_labels], lag_ratio=0.1),
            run_time=0.4
        )

        # 显示 spiky 折线
        self.play(
            Create(before_line),
            LaggedStart(*[FadeIn(d, scale=1.5) for d in before_dots], lag_ratio=0.15),
            run_time=1
        )

        # 等待一下
        self.wait(0.5)

        # ===== In-place 变换到 uniform =====
        # 创建目标折线
        after_line = VMobject(color=SURVIVE_COLOR, stroke_width=4)
        after_line.set_points_as_corners(after_points)

        # 创建目标点标记
        after_dots = VGroup()
        for point in after_points:
            dot = Dot(point, color=SURVIVE_COLOR, radius=0.1)
            after_dots.add(dot)

        # 变换动画 - in-place morphing
        self.play(
            Transform(before_line, after_line),
            *[Transform(before_dots[i], after_dots[i]) for i in range(4)],
            run_time=2
        )

        # 保持显示
        self.wait(1)

        # 淡出
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


# ===== Scene 3: Loss Function with Entropy Term =====
class Scene3LossFunction(Scene):
    """Scene 3: The Loss Function with Entropy Term (8 seconds)"""
    def construct(self):
        # 设置纯黑色背景
        self.camera.background_color = BLACK

        # 标题

        # ===== Phase A: 显示基础损失 (0-2s) =====
        # 第一项：期望任务损失
        term1 = MathTex(
            r"\mathcal{L} = \sum_{t=1}^{T_{\max}} p_\phi(t \mid x)\,\mathcal{L}^{(t)}",
            font_size=42
        )
        term1.shift(UP * 1)

        self.play(Write(term1), run_time=1.5)

        # 下括号：expected task loss
        brace1 = Brace(term1[0][2:], DOWN, color=SECONDARY_TEXT)
        brace1_label = Tex(r"expected task loss", font_size=18, color=SECONDARY_TEXT)
        brace1_label.next_to(brace1, DOWN, buff=0.1)

        self.play(GrowFromCenter(brace1), Write(brace1_label), run_time=0.8)

        self.wait(0.5)

        # ===== Phase B: 添加熵项 (2-5s) =====
        # 准备熵项
        entropy_term = MathTex(
            r"- \beta \cdot H\!\left(p_\phi(\cdot \mid x)\right)",
            font_size=42,
            color=LOOP_COLOR
        )
        # 先定位到 term1 右侧
        entropy_term.next_to(term1, RIGHT, buff=0.1)

        # 计算完整公式的中心位置
        full_width = term1.get_width() + entropy_term.get_width() + 0.1
        target_center = ORIGIN + UP * 1
        shift_amount = target_center + LEFT * (full_width / 2 - term1.get_width() / 2) - term1.get_center()

        # 左移第一项、大括号和标签，为第二项腾出空间
        self.play(
            term1.animate.shift(shift_amount),
            brace1.animate.shift(shift_amount),
            brace1_label.animate.shift(shift_amount),
            run_time=0.5
        )

        # 更新熵项位置
        entropy_term.next_to(term1, RIGHT, buff=0.1)

        self.play(Write(entropy_term), run_time=1.5)

        # 第二项的下括号 - 与第一个括号对齐
        brace2 = Brace(entropy_term, DOWN, color=LOOP_COLOR)
        # 让两个括号在同一高度（顶部对齐）
        brace2.align_to(brace1, UP)
        brace2_label = Tex(r"entropy regularization", font_size=18, color=LOOP_COLOR)
        brace2_label.next_to(brace2, DOWN, buff=0.1)

        self.play(GrowFromCenter(brace2), Write(brace2_label), run_time=0.8)

        self.wait(0.5)

        # 保持显示一段时间
        self.wait(2)

        # 淡出
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


# ===== Scene 4: Exit Distribution Term =====
class Scene4ExitDistribution(Scene):
    """Scene 4: Exit Distribution Term (4 seconds)"""
    def construct(self):
        # 设置纯黑色背景
        self.camera.background_color = BLACK

        # 完整公式（半透明）
        full_formula = MathTex(
            r"\mathcal{L} = \sum_{t=1}^{T_{\max}} p_\phi(t \mid x)\,\mathcal{L}^{(t)} - \beta \cdot H\!\left(p_\phi(\cdot \mid x)\right)",
            font_size=36
        )
        full_formula.shift(UP * 2)
        full_formula.set_opacity(0.3)

        self.play(FadeIn(full_formula), run_time=0.5)

        # ===== Phase A: 高亮退出分布 (0-2s) =====
        # 提取并高亮 p_φ(t|x)
        exit_dist = MathTex(r"p_\phi(t \mid x)", font_size=56, color=WHITE)
        exit_dist.shift(UP * 0.5)

        self.play(Write(exit_dist), run_time=0.8)

        # 标签
        exit_label = Tex(r"\textbf{Exit Distribution}", font_size=28, color=LOOP_COLOR)
        exit_label.next_to(exit_dist, DOWN, buff=0.5)

        self.play(Write(exit_label), run_time=0.5)

        # ===== Phase B: 连接到含义 (2-4s) =====
        # 创建迷你柱状图展示分布
        mini_chart_center = DOWN * 1.8

        # 迷你柱子
        mini_probs = [0.25, 0.30, 0.25, 0.20]
        mini_bars = VGroup()
        bar_width = 0.4
        bar_scale = 2.5

        for i, prob in enumerate(mini_probs):
            bar = Rectangle(
                width=bar_width,
                height=prob * bar_scale,
                color=LOOP_COLOR,
                fill_opacity=0.8,
                stroke_width=1
            )
            bar.move_to(mini_chart_center + RIGHT * (i - 1.5) * 0.6 + UP * (prob * bar_scale / 2))
            mini_bars.add(bar)

        # 基线
        baseline = Line(
            mini_chart_center + LEFT * 1.5,
            mini_chart_center + RIGHT * 1.5,
            color=SECONDARY_TEXT,
            stroke_width=2
        )

        # 标签
        mini_labels = VGroup()
        for i in range(4):
            label = Tex(str(i + 1), font_size=14, color=SECONDARY_TEXT)
            label.move_to(mini_chart_center + RIGHT * (i - 1.5) * 0.6 + DOWN * 0.3)
            mini_labels.add(label)

        mini_title = Tex(r"P(exit at each step)", font_size=18, color=SECONDARY_TEXT)
        mini_title.next_to(baseline, DOWN, buff=0.5)

        # 连接箭头
        connect_arrow = Arrow(
            exit_label.get_bottom(),
            mini_title.get_top() + UP * 0.8,
            color=SECONDARY_TEXT,
            stroke_width=2
        )

        self.play(
            GrowArrow(connect_arrow),
            Create(baseline),
            run_time=0.5
        )

        self.play(
            LaggedStart(*[GrowFromEdge(bar, DOWN) for bar in mini_bars], lag_ratio=0.1),
            LaggedStart(*[Write(l) for l in mini_labels], lag_ratio=0.1),
            run_time=0.8
        )

        self.play(Write(mini_title), run_time=0.4)

        # 柱子脉冲动画（依次闪烁）
        for i, bar in enumerate(mini_bars):
            self.play(
                bar.animate.set_fill(opacity=1),
                run_time=0.15
            )
            self.play(
                bar.animate.set_fill(opacity=0.8),
                run_time=0.15
            )

        self.wait(0.5)

        # 淡出
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


# ===== Scene 5: Prior Distribution Term =====
class Scene5PriorDistribution(Scene):
    """Scene 5: Prior Distribution Term (4 seconds)"""
    def construct(self):
        # 设置纯黑色背景
        self.camera.background_color = BLACK

        # 标题
        title = Tex(
            r"The target: a prior distribution",
            font_size=28,
            color=SECONDARY_TEXT
        )
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.8)

        # ===== Phase A: 介绍 KL 形式 (0-2s) =====
        # KL 散度形式的公式
        kl_formula = MathTex(
            r"\beta \cdot \text{KL}\big(p_\phi(\cdot \mid x)\,\|\,\pi(\cdot)\big)",
            font_size=44
        )
        kl_formula.shift(UP * 1)

        self.play(Write(kl_formula), run_time=1)

        # 高亮先验分布 π(·)
        # 找到 π(·) 的位置并高亮
        prior_highlight = MathTex(r"\pi(\cdot)", font_size=44, color=LOOP_COLOR)
        prior_highlight.move_to(kl_formula.get_center() + RIGHT * 2.2)

        # 标签
        prior_label = Tex(r"\textbf{Prior Distribution}", font_size=24, color=LOOP_COLOR)
        prior_label.next_to(prior_highlight, DOWN, buff=0.3)

        self.play(
            FadeIn(prior_highlight, scale=1.2),
            Write(prior_label),
            run_time=0.8
        )

        # ===== Phase B: 显示均匀先验 (2-4s) =====
        # 均匀分布柱状图
        uniform_center = DOWN * 1.5

        uniform_probs = [0.25, 0.25, 0.25, 0.25]
        uniform_bars = VGroup()
        bar_width = 0.5
        bar_scale = 3

        for i, prob in enumerate(uniform_probs):
            bar = Rectangle(
                width=bar_width,
                height=prob * bar_scale,
                color=SURVIVE_COLOR,
                fill_opacity=0.8,
                stroke_width=1
            )
            bar.move_to(uniform_center + RIGHT * (i - 1.5) * 0.7 + UP * (prob * bar_scale / 2))
            uniform_bars.add(bar)

        # 基线
        baseline = Line(
            uniform_center + LEFT * 2,
            uniform_center + RIGHT * 2,
            color=SECONDARY_TEXT,
            stroke_width=2
        )

        # 标签
        step_labels = VGroup()
        for i in range(4):
            label = Tex(str(i + 1), font_size=16, color=SECONDARY_TEXT)
            label.move_to(uniform_center + RIGHT * (i - 1.5) * 0.7 + DOWN * 0.3)
            step_labels.add(label)

        # 公式标签
        uniform_formula = MathTex(
            r"\pi(t) = \frac{1}{T_{\max}}",
            font_size=28,
            color=SURVIVE_COLOR
        )
        uniform_formula.next_to(baseline, DOWN, buff=0.6)

        # 虚线连接
        dotted_lines = VGroup()
        for bar in uniform_bars:
            line = DashedLine(
                bar.get_top(),
                bar.get_top() + UP * 0.3,
                color=SECONDARY_TEXT,
                stroke_width=1,
                dash_length=0.05
            )
            dotted_lines.add(line)

        self.play(
            Create(baseline),
            LaggedStart(*[GrowFromEdge(bar, DOWN) for bar in uniform_bars], lag_ratio=0.1),
            LaggedStart(*[Write(l) for l in step_labels], lag_ratio=0.1),
            run_time=1
        )

        self.play(Write(uniform_formula), run_time=0.6)

        # 显示这是目标
        target_text = Tex(r"$\leftarrow$ Target we want to match", font_size=18, color=SECONDARY_TEXT)
        target_text.next_to(uniform_bars, RIGHT, buff=0.5)

        self.play(Write(target_text), run_time=0.5)

        self.wait(0.5)

        # 淡出
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


# ===== Scene 6: KL Divergence Explanation =====
class Scene6KLDivergence(Scene):
    """Scene 6: KL Divergence Explanation (5 seconds)"""
    def construct(self):
        # 设置纯黑色背景
        self.camera.background_color = BLACK

        # 标题
        title = Tex(
            r"KL Divergence: matching distributions",
            font_size=28,
            color=SECONDARY_TEXT
        )
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.8)

        # ===== Phase A: 设置对比 (0-2s) =====
        # 左侧：学习到的退出分布（偏斜）
        left_center = LEFT * 3 + DOWN * 0.5

        learned_probs = [0.15, 0.20, 0.15, 0.50]  # 偏斜分布
        left_bars = VGroup()
        bar_width = 0.4
        bar_scale = 3

        for i, prob in enumerate(learned_probs):
            bar = Rectangle(
                width=bar_width,
                height=prob * bar_scale,
                color=EXIT_COLOR,
                fill_opacity=0.8,
                stroke_width=1
            )
            bar.move_to(left_center + RIGHT * (i - 1.5) * 0.5 + UP * (prob * bar_scale / 2))
            left_bars.add(bar)

        left_baseline = Line(
            left_center + LEFT * 1.3,
            left_center + RIGHT * 1.3,
            color=SECONDARY_TEXT,
            stroke_width=2
        )

        left_label = MathTex(r"p_\phi(t|x)", font_size=24, color=EXIT_COLOR)
        left_label.next_to(left_baseline, DOWN, buff=0.3)

        # 右侧：均匀先验
        right_center = RIGHT * 3 + DOWN * 0.5

        uniform_probs = [0.25, 0.25, 0.25, 0.25]
        right_bars = VGroup()

        for i, prob in enumerate(uniform_probs):
            bar = Rectangle(
                width=bar_width,
                height=prob * bar_scale,
                color=SURVIVE_COLOR,
                fill_opacity=0.8,
                stroke_width=1
            )
            bar.move_to(right_center + RIGHT * (i - 1.5) * 0.5 + UP * (prob * bar_scale / 2))
            right_bars.add(bar)

        right_baseline = Line(
            right_center + LEFT * 1.3,
            right_center + RIGHT * 1.3,
            color=SECONDARY_TEXT,
            stroke_width=2
        )

        right_label = MathTex(r"\pi(t)", font_size=24, color=SURVIVE_COLOR)
        right_label.next_to(right_baseline, DOWN, buff=0.3)

        # 中间：KL 散度箭头
        kl_arrow = DoubleArrow(
            LEFT * 0.8,
            RIGHT * 0.8,
            color=HIGHLIGHT_COLOR,
            stroke_width=3
        )
        kl_arrow.shift(DOWN * 0.5)

        kl_label = Tex(r"KL Divergence", font_size=20, color=HIGHLIGHT_COLOR)
        kl_label.next_to(kl_arrow, UP, buff=0.15)

        # 显示左侧分布
        self.play(
            Create(left_baseline),
            LaggedStart(*[GrowFromEdge(bar, DOWN) for bar in left_bars], lag_ratio=0.1),
            Write(left_label),
            run_time=0.8
        )

        # 显示右侧分布
        self.play(
            Create(right_baseline),
            LaggedStart(*[GrowFromEdge(bar, DOWN) for bar in right_bars], lag_ratio=0.1),
            Write(right_label),
            run_time=0.8
        )

        # 显示 KL 箭头
        self.play(
            GrowArrow(kl_arrow),
            Write(kl_label),
            run_time=0.5
        )

        # ===== Phase B: 显示匹配过程 (2-5s) =====
        # KL 值指示器
        kl_value = MathTex(r"\text{KL} = 0.8", font_size=24, color=HIGHLIGHT_COLOR)
        kl_value.next_to(kl_arrow, DOWN, buff=0.3)
        self.play(Write(kl_value), run_time=0.3)

        # 动画：左侧分布逐渐变成均匀分布
        target_probs_list = [
            [0.18, 0.22, 0.20, 0.40],  # KL = 0.4
            [0.22, 0.26, 0.24, 0.28],  # KL = 0.1
            [0.25, 0.25, 0.25, 0.25],  # KL = 0.0
        ]
        kl_values = ["0.4", "0.1", "0.0"]

        for target_probs, kl_str in zip(target_probs_list, kl_values):
            # 更新柱子
            new_bars = VGroup()
            for i, prob in enumerate(target_probs):
                bar = Rectangle(
                    width=bar_width,
                    height=prob * bar_scale,
                    color=EXIT_COLOR if kl_str != "0.0" else SURVIVE_COLOR,
                    fill_opacity=0.8,
                    stroke_width=1
                )
                bar.move_to(left_center + RIGHT * (i - 1.5) * 0.5 + UP * (prob * bar_scale / 2))
                new_bars.add(bar)

            # 更新 KL 值
            new_kl = MathTex(rf"\text{{KL}} = {kl_str}", font_size=24, color=HIGHLIGHT_COLOR)
            new_kl.next_to(kl_arrow, DOWN, buff=0.3)

            self.play(
                *[Transform(left_bars[i], new_bars[i]) for i in range(4)],
                Transform(kl_value, new_kl),
                run_time=0.6
            )

        # 匹配完成，显示对勾
        check_mark = MathTex(r"\checkmark", font_size=40, color=SURVIVE_COLOR)
        check_mark.next_to(kl_value, RIGHT, buff=0.3)

        match_text = Tex(r"Distributions matched!", font_size=20, color=SURVIVE_COLOR)
        match_text.to_edge(DOWN, buff=0.8)

        self.play(
            FadeIn(check_mark, scale=1.5),
            Write(match_text),
            run_time=0.5
        )

        self.wait(0.8)

        # 淡出
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


# ===== Scene 7: The Beta Coefficient =====
class Scene7BetaCoefficient(Scene):
    """Scene 7: The Beta Coefficient (4 seconds)"""
    def construct(self):
        # 设置纯黑色背景
        self.camera.background_color = BLACK

        # 标题
        title = Tex(
            r"Modulating regularization strength with $\beta$",
            font_size=28,
            color=SECONDARY_TEXT
        )
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.8)

        # ===== Phase A: 高亮 beta (0-2s) =====
        # 公式
        formula = MathTex(
            r"\mathcal{L} = \text{Task Loss} - ",
            r"\beta",
            r" \cdot H(p_\phi)",
            font_size=40
        )
        formula[1].set_color(HIGHLIGHT_COLOR)
        formula.shift(UP * 1.5)

        self.play(Write(formula), run_time=1)

        # beta 脉冲并放大
        beta_copy = formula[1].copy()
        self.play(
            beta_copy.animate.scale(1.5).set_color(HIGHLIGHT_COLOR),
            run_time=0.3
        )
        self.play(
            beta_copy.animate.scale(1/1.5),
            run_time=0.3
        )
        self.remove(beta_copy)

        # 标签
        beta_label = Tex(r"strength coefficient", font_size=20, color=HIGHLIGHT_COLOR)
        beta_label.next_to(formula[1], DOWN, buff=0.5)

        self.play(Write(beta_label), run_time=0.4)

        # ===== Phase B: 显示 beta 效果 (2-4s) =====
        # 滑块可视化
        slider_center = DOWN * 1.2

        # 滑块轨道
        slider_track = Line(
            slider_center + LEFT * 3,
            slider_center + RIGHT * 3,
            color=SECONDARY_TEXT,
            stroke_width=4
        )

        # 滑块
        slider_knob = Circle(
            radius=0.15,
            color=HIGHLIGHT_COLOR,
            fill_opacity=1
        )
        slider_knob.move_to(slider_center)

        # 标签
        low_label = Tex(r"$\beta$ low", font_size=18, color=SECONDARY_TEXT)
        low_label.next_to(slider_track, LEFT, buff=0.3)

        high_label = Tex(r"$\beta$ high", font_size=18, color=SECONDARY_TEXT)
        high_label.next_to(slider_track, RIGHT, buff=0.3)

        # 效果标签
        exploitation_text = Tex(r"More exploitation", font_size=18, color=EXIT_COLOR)
        exploitation_text.move_to(slider_center + LEFT * 2 + DOWN * 0.8)

        exploration_text = Tex(r"More exploration", font_size=18, color=SURVIVE_COLOR)
        exploration_text.move_to(slider_center + RIGHT * 2 + DOWN * 0.8)

        self.play(
            Create(slider_track),
            FadeIn(slider_knob),
            Write(low_label),
            Write(high_label),
            run_time=0.6
        )

        # 滑块移动动画
        # 向右移动（高 beta）
        self.play(
            slider_knob.animate.move_to(slider_center + RIGHT * 2.5),
            Write(exploration_text),
            run_time=0.6
        )

        # 向左移动（低 beta）
        self.play(
            slider_knob.animate.move_to(slider_center + LEFT * 2.5),
            Write(exploitation_text),
            run_time=0.6
        )

        # 回到中间
        self.play(
            slider_knob.animate.move_to(slider_center),
            run_time=0.4
        )

        # 底部说明
        tradeoff_text = Tex(
            r"$\beta$ controls the exploration--exploitation tradeoff",
            font_size=22,
            color=WHITE
        )
        tradeoff_text.to_edge(DOWN, buff=0.5)

        self.play(Write(tradeoff_text), run_time=0.6)

        self.wait(0.5)

        # 淡出
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


# ===== Scene 8: PonderNet and Geometric Prior =====
class Scene8PonderNetGeometric(Scene):
    """Scene 8: PonderNet and Geometric Prior (8 seconds)
    一条条曲线出现，显示不同 λ 值 (0.1-0.9)
    """
    def construct(self):
        # 设置纯黑色背景
        self.camera.background_color = BLACK

        # ===== Phase A: 引用 (0-2s) =====
        # 引用卡片
        citation_box = RoundedRectangle(
            width=4,
            height=1.5,
            corner_radius=0.15,
            color=SECONDARY_TEXT,
            fill_opacity=0.1,
            stroke_width=2
        )
        citation_box.to_corner(UL, buff=0.5)

        citation_title = Tex(r"\textbf{PonderNet}", font_size=24, color=WHITE)
        citation_author = Tex(r"Banino et al., 2021", font_size=16, color=SECONDARY_TEXT)
        citation_org = Tex(r"Google DeepMind", font_size=14, color=LOOP_COLOR)

        citation_content = VGroup(citation_title, citation_author, citation_org)
        citation_content.arrange(DOWN, buff=0.15)
        citation_content.move_to(citation_box.get_center())

        self.play(
            FadeIn(citation_box),
            Write(citation_title),
            Write(citation_author),
            Write(citation_org),
            run_time=1
        )

        # ===== Phase B: 显示几何分布 (2-6s) =====
        # 坐标轴
        axes = Axes(
            x_range=[0, 8, 1],
            y_range=[0, 1.0, 0.2],
            x_length=8,
            y_length=4,
            axis_config={"color": SECONDARY_TEXT, "include_tip": False},
            y_axis_config={"include_numbers": True, "font_size": 18},
        )
        axes.shift(DOWN * 0.3 + RIGHT * 0.5)

        # 轴标签
        x_label = Tex(r"Loop step $t$", font_size=18, color=SECONDARY_TEXT)
        x_label.next_to(axes.x_axis, DOWN, buff=0.4)

        y_label = MathTex(r"\pi(t)", font_size=22, color=SECONDARY_TEXT)
        y_label.next_to(axes.y_axis, UP, buff=0.2)

        self.play(Create(axes), Write(x_label), Write(y_label), run_time=0.8)

        # 几何分布曲线，不同的 λ 值 (0.1 到 0.9)
        lambda_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        # 颜色从蓝色渐变到红色/粉色
        colors = [
            "#58a6ff",  # 0.1 - 蓝色
            "#4ECDC4",  # 0.2 - 青色
            "#3fb950",  # 0.3 - 绿色
            "#8BC34A",  # 0.4 - 浅绿
            "#d29922",  # 0.5 - 黄色
            "#FF9800",  # 0.6 - 橙色
            "#FF5722",  # 0.7 - 深橙
            "#f85149",  # 0.8 - 红色
            "#FF69B4",  # 0.9 - 粉色
        ]

        curves = VGroup()
        legend_items = VGroup()
        all_dots = VGroup()  # 存储所有点

        for i, (lam, color) in enumerate(zip(lambda_values, colors)):
            # 几何分布: π(t) = (1-λ)^(t-1) * λ
            def geometric_dist(t, l=lam):
                return l * ((1 - l) ** (t - 1))

            # 创建点和线
            points = []
            dots = VGroup()
            for t in range(1, 8):
                prob = geometric_dist(t)
                point = axes.c2p(t, prob)
                points.append(point)
                # 添加点标记
                dot = Dot(point, color=color, radius=0.05)
                dots.add(dot)

            # 使用折线连接（不是平滑曲线），避免负值
            curve = VMobject(color=color, stroke_width=3)
            curve.set_points_as_corners(points)
            curves.add(curve)
            all_dots.add(dots)

            # 图例
            legend_line = Line(ORIGIN, RIGHT * 0.4, color=color, stroke_width=3)
            legend_text = MathTex(rf"\lambda = {lam}", font_size=14, color=color)
            legend_item = VGroup(legend_line, legend_text)
            legend_text.next_to(legend_line, RIGHT, buff=0.08)
            legend_items.add(legend_item)

        # 排列图例
        legend_items.arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        legend_items.to_corner(UR, buff=0.5)

        # 公式
        formula = MathTex(
            r"\pi(t) = (1-\lambda)^{t-1} \cdot \lambda",
            font_size=28
        )
        formula.next_to(axes, UP, buff=0.3)

        self.play(Write(formula), run_time=0.6)

        # 一条条曲线出现，每条曲线对应不同的 λ（带点标记）
        for curve, dots, legend_item in zip(curves, all_dots, legend_items):
            self.play(
                Create(curve),
                FadeIn(dots),
                FadeIn(legend_item),
                run_time=0.4
            )

        # ===== Phase C: 显示问题 (6-8s) =====
        # 红色 X 标记在后面的步骤
        x_marks = VGroup()
        for t in [5, 6, 7]:
            x_mark = MathTex(r"\times", font_size=24, color=EXIT_COLOR)
            x_mark.move_to(axes.c2p(t, 0.05))
            x_marks.add(x_mark)

        # 注释
        problem_text = Tex(
            r"Later steps undertrained!",
            font_size=22,
            color=EXIT_COLOR
        )
        problem_text.to_edge(DOWN, buff=0.5)

        # 高亮显示问题
        self.play(
            LaggedStart(*[FadeIn(x, scale=1.5) for x in x_marks], lag_ratio=0.1),
            run_time=0.6
        )

        self.play(Write(problem_text), run_time=0.6)

        self.wait(0.8)

        # 淡出
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


# ===== Scene 9: Transition to KV-Cache Concern =====
class Scene9KVCacheTransition(Scene):
    """Scene 9: Transition to KV-Cache Concern (4 seconds)"""
    def construct(self):
        # 设置纯黑色背景
        self.camera.background_color = BLACK

        # ===== Phase A: 成功确认 (0-1.5s) =====
        # 绿色对勾和文字
        success_check = MathTex(r"\checkmark", font_size=60, color=SURVIVE_COLOR)
        success_text = Tex(
            r"\textbf{Looping Mechanism Working!}",
            font_size=32,
            color=SURVIVE_COLOR
        )

        success_group = VGroup(success_check, success_text)
        success_group.arrange(RIGHT, buff=0.5)
        success_group.shift(UP * 1.5)

        self.play(
            FadeIn(success_check, scale=1.5),
            Write(success_text),
            run_time=0.8
        )

        # 简单的庆祝效果（几个星星）
        stars = VGroup()
        star_positions = [UL * 2, UR * 2, LEFT * 3, RIGHT * 3]
        for pos in star_positions:
            star = MathTex(r"\star", font_size=24, color=HIGHLIGHT_COLOR)
            star.move_to(success_group.get_center() + pos * 0.3)
            stars.add(star)

        self.play(
            LaggedStart(*[FadeIn(s, scale=2) for s in stars], lag_ratio=0.1),
            run_time=0.5
        )

        self.wait(0.2)

        # ===== Phase B: 但是等等... (1.5-4s) =====
        # 转换为警告
        warning_icon = MathTex(r"\triangle", font_size=60, color=HIGHLIGHT_COLOR)
        warning_text = Tex(
            r"But each loop adds cost...",
            font_size=28,
            color=HIGHLIGHT_COLOR
        )

        warning_group = VGroup(warning_icon, warning_text)
        warning_group.arrange(RIGHT, buff=0.3)
        warning_group.move_to(success_group.get_center())

        self.play(
            FadeOut(stars),
            Transform(success_check, warning_icon),
            Transform(success_text, warning_text),
            run_time=0.6
        )

        # 内存块堆栈
        stack_center = DOWN * 1

        blocks = VGroup()
        block_labels = ["Loop 1 KV-Cache", "Loop 2 KV-Cache", "Loop 3 KV-Cache", "Loop 4 KV-Cache"]
        block_colors = [LOOP_COLOR, "#4A90D9", "#3D7EBF", "#2F6AA5"]

        for i, (label_text, color) in enumerate(zip(block_labels, block_colors)):
            block = RoundedRectangle(
                width=4,
                height=0.6,
                corner_radius=0.1,
                color=color,
                fill_opacity=0.7,
                stroke_width=2
            )
            block.move_to(stack_center + UP * i * 0.7)

            label = Tex(label_text, font_size=16, color=WHITE)
            label.move_to(block.get_center())

            blocks.add(VGroup(block, label))

        # 内存使用条
        memory_bar_bg = Rectangle(
            width=0.4,
            height=3,
            color=SECONDARY_TEXT,
            fill_opacity=0.2,
            stroke_width=2
        )
        memory_bar_bg.to_edge(RIGHT, buff=1)

        memory_bar_fill = Rectangle(
            width=0.35,
            height=0,
            color=EXIT_COLOR,
            fill_opacity=0.8,
            stroke_width=0
        )
        memory_bar_fill.align_to(memory_bar_bg, DOWN)
        memory_bar_fill.move_to(memory_bar_bg.get_center(), cdir=DOWN)

        memory_label = Tex(r"Memory", font_size=14, color=SECONDARY_TEXT)
        memory_label.next_to(memory_bar_bg, UP, buff=0.2)

        self.play(
            Create(memory_bar_bg),
            Write(memory_label),
            run_time=0.3
        )

        # 依次添加内存块，带"重量"效果
        for i, block in enumerate(blocks):
            # 计算新的内存条高度
            new_height = (i + 1) * 0.6
            new_fill = Rectangle(
                width=0.35,
                height=new_height,
                color=EXIT_COLOR,
                fill_opacity=0.8,
                stroke_width=0
            )
            new_fill.align_to(memory_bar_bg, DOWN)
            new_fill.move_to(memory_bar_bg.get_center(), cdir=DOWN)

            self.play(
                FadeIn(block, shift=DOWN * 0.2),
                Transform(memory_bar_fill, new_fill),
                run_time=0.3
            )
            # 轻微弹跳效果
            self.play(
                block.animate.shift(DOWN * 0.05),
                run_time=0.1
            )
            self.play(
                block.animate.shift(UP * 0.05),
                run_time=0.1
            )

        # 计算和内存图标
        icons_text = Tex(
            r"Each loop = More compute + More memory",
            font_size=22,
            color=EXIT_COLOR
        )
        icons_text.to_edge(DOWN, buff=0.5)

        self.play(Write(icons_text), run_time=0.6)

        self.wait(0.8)

        # 淡出
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


# ===== 完整动画: EntropyRegularizer =====
class EntropyRegularizer(Scene):
    """完整的 Entropy Regularizer 动画"""
    def construct(self):
        # 设置纯黑色背景
        self.camera.background_color = BLACK

        # Scene 2: Distribution Spreading
        self.scene2_distribution_spreading()

        # Scene 3: Loss Function
        self.scene3_loss_function()

        # Scene 4: Exit Distribution
        self.scene4_exit_distribution()

        # Scene 5: Prior Distribution
        self.scene5_prior_distribution()

        # Scene 6: KL Divergence
        self.scene6_kl_divergence()

        # Scene 7: Beta Coefficient
        self.scene7_beta_coefficient()

        # Scene 8: PonderNet Geometric
        self.scene8_pondernet_geometric()

        # Scene 9: KV-Cache Transition
        self.scene9_kv_cache_transition()

    def scene1_title(self):
        """Scene 1: Section Title (2 seconds)"""
        title = Tex(
            r"\textbf{Entropy Regularizer}",
            font_size=72,
            color=WHITE
        )
        title.scale(0.95)

        self.play(
            FadeIn(title, scale=0.95),
            title.animate.scale(1.0 / 0.95),
            run_time=1
        )

        self.wait(1)
        self.play(FadeOut(title), run_time=0.5)

    def scene2_distribution_spreading(self):
        """Scene 2: Distribution Spreading (6 seconds) - 折线图 in-place 变换"""
        # 数据
        before_probs = [0.02, 0.03, 0.05, 0.90]
        after_probs = [0.22, 0.28, 0.25, 0.25]

        chart_width = 8
        chart_height = 4

        # 坐标轴（居中）
        axes = Axes(
            x_range=[0, 5, 1], y_range=[0, 1.0, 0.2],
            x_length=chart_width, y_length=chart_height,
            axis_config={"color": SECONDARY_TEXT, "include_tip": False},
            y_axis_config={"include_numbers": True, "font_size": 20},
        )
        axes.shift(DOWN * 0.3)

        x_labels = VGroup()
        for i in range(4):
            label = Tex(str(i + 1), font_size=20, color=SECONDARY_TEXT)
            label.move_to(axes.c2p(i + 1, 0) + DOWN * 0.35)
            x_labels.add(label)

        x_title = Tex(r"Loop Step", font_size=18, color=SECONDARY_TEXT)
        x_title.next_to(axes.x_axis, DOWN, buff=0.6)

        y_title = MathTex(r"p(t|x)", font_size=26, color=SECONDARY_TEXT)
        y_title.next_to(axes.y_axis, UP, buff=0.2)

        # 折线图点
        before_points = [axes.c2p(i + 1, prob) for i, prob in enumerate(before_probs)]
        after_points = [axes.c2p(i + 1, prob) for i, prob in enumerate(after_probs)]

        # 创建折线
        before_line = VMobject(color=EXIT_COLOR, stroke_width=4)
        before_line.set_points_as_corners(before_points)

        before_dots = VGroup()
        for point in before_points:
            dot = Dot(point, color=EXIT_COLOR, radius=0.1)
            before_dots.add(dot)

        # 显示坐标轴
        self.play(Create(axes), Write(x_title), Write(y_title), run_time=0.5)
        self.play(LaggedStart(*[Write(l) for l in x_labels], lag_ratio=0.1), run_time=0.3)

        # 显示 spiky 折线
        self.play(
            Create(before_line),
            LaggedStart(*[FadeIn(d, scale=1.5) for d in before_dots], lag_ratio=0.1),
            run_time=0.8
        )

        self.wait(0.5)

        # In-place 变换到 uniform
        after_line = VMobject(color=SURVIVE_COLOR, stroke_width=4)
        after_line.set_points_as_corners(after_points)

        after_dots = VGroup()
        for point in after_points:
            dot = Dot(point, color=SURVIVE_COLOR, radius=0.1)
            after_dots.add(dot)

        # 变换动画
        self.play(
            Transform(before_line, after_line),
            *[Transform(before_dots[i], after_dots[i]) for i in range(4)],
            run_time=1.5
        )

        self.wait(0.8)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.6)

    def scene3_loss_function(self):
        """Scene 3: Loss Function (8 seconds)"""
        title = Tex(r"Adding entropy regularization to the loss", font_size=28, color=SECONDARY_TEXT)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.8)

        # 第一项
        term1 = MathTex(
            r"\mathcal{L} = \sum_{t=1}^{T_{\max}} p_\phi(t \mid x)\,\mathcal{L}^{(t)}",
            font_size=42
        )
        term1.shift(UP * 1)
        self.play(Write(term1), run_time=1.2)

        brace1 = Brace(term1[0][2:], DOWN, color=SECONDARY_TEXT)
        brace1_label = Tex(r"expected task loss", font_size=18, color=SECONDARY_TEXT)
        brace1_label.next_to(brace1, DOWN, buff=0.1)
        self.play(GrowFromCenter(brace1), Write(brace1_label), run_time=0.6)

        self.wait(0.3)

        # 准备熵项
        entropy_term = MathTex(r"- \beta \cdot H\!\left(p_\phi(\cdot \mid x)\right)", font_size=42, color=LOOP_COLOR)
        entropy_term.next_to(term1, RIGHT, buff=0.1)

        # 计算完整公式的中心位置
        full_width = term1.get_width() + entropy_term.get_width() + 0.1
        target_center = ORIGIN + UP * 1
        shift_amount = target_center + LEFT * (full_width / 2 - term1.get_width() / 2) - term1.get_center()

        # 左移第一项、大括号和标签，为第二项腾出空间
        self.play(
            term1.animate.shift(shift_amount),
            brace1.animate.shift(shift_amount),
            brace1_label.animate.shift(shift_amount),
            run_time=0.5
        )

        # 更新熵项位置并写入
        entropy_term.next_to(term1, RIGHT, buff=0.1)
        self.play(Write(entropy_term), run_time=1.2)

        # 第二项的下括号 - 与第一个括号对齐
        brace2 = Brace(entropy_term, DOWN, color=LOOP_COLOR)
        # 让两个括号在同一高度（顶部对齐）
        brace2.align_to(brace1, UP)
        brace2_label = Tex(r"entropy regularization", font_size=18, color=LOOP_COLOR)
        brace2_label.next_to(brace2, DOWN, buff=0.1)
        self.play(GrowFromCenter(brace2), Write(brace2_label), run_time=0.6)

        # 保持显示
        self.wait(1.5)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.6)

    def scene4_exit_distribution(self):
        """Scene 4: Exit Distribution (4 seconds)"""
        full_formula = MathTex(
            r"\mathcal{L} = \sum p_\phi(t \mid x)\,\mathcal{L}^{(t)} - \beta \cdot H(p_\phi)",
            font_size=32
        )
        full_formula.shift(UP * 2)
        full_formula.set_opacity(0.3)
        self.play(FadeIn(full_formula), run_time=0.4)

        exit_dist = MathTex(r"p_\phi(t \mid x)", font_size=56, color=WHITE)
        exit_dist.shift(UP * 0.3)
        self.play(Write(exit_dist), run_time=0.6)

        exit_label = Tex(r"\textbf{Exit Distribution}", font_size=28, color=LOOP_COLOR)
        exit_label.next_to(exit_dist, DOWN, buff=0.4)
        self.play(Write(exit_label), run_time=0.4)

        # 迷你柱状图
        mini_center = DOWN * 1.5
        mini_probs = [0.25, 0.30, 0.25, 0.20]
        mini_bars = VGroup()

        for i, prob in enumerate(mini_probs):
            bar = Rectangle(width=0.4, height=prob * 2.5, color=LOOP_COLOR, fill_opacity=0.8, stroke_width=1)
            bar.move_to(mini_center + RIGHT * (i - 1.5) * 0.6 + UP * (prob * 2.5 / 2))
            mini_bars.add(bar)

        baseline = Line(mini_center + LEFT * 1.5, mini_center + RIGHT * 1.5, color=SECONDARY_TEXT, stroke_width=2)

        self.play(Create(baseline), run_time=0.3)
        self.play(LaggedStart(*[GrowFromEdge(bar, DOWN) for bar in mini_bars], lag_ratio=0.1), run_time=0.6)

        mini_title = Tex(r"P(exit at each step)", font_size=18, color=SECONDARY_TEXT)
        mini_title.next_to(baseline, DOWN, buff=0.4)
        self.play(Write(mini_title), run_time=0.3)

        self.wait(0.5)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.6)

    def scene5_prior_distribution(self):
        """Scene 5: Prior Distribution (4 seconds)"""
        title = Tex(r"The target: a prior distribution", font_size=28, color=SECONDARY_TEXT)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.6)

        kl_formula = MathTex(r"\beta \cdot \text{KL}\big(p_\phi(\cdot \mid x)\,\|\,\pi(\cdot)\big)", font_size=44)
        kl_formula.shift(UP * 1)
        self.play(Write(kl_formula), run_time=0.8)

        prior_label = Tex(r"\textbf{Prior Distribution}", font_size=24, color=LOOP_COLOR)
        prior_label.next_to(kl_formula, DOWN, buff=0.5)
        self.play(Write(prior_label), run_time=0.4)

        # 均匀分布
        uniform_center = DOWN * 1.2
        uniform_bars = VGroup()
        for i in range(4):
            bar = Rectangle(width=0.5, height=0.25 * 3, color=SURVIVE_COLOR, fill_opacity=0.8, stroke_width=1)
            bar.move_to(uniform_center + RIGHT * (i - 1.5) * 0.7 + UP * (0.25 * 3 / 2))
            uniform_bars.add(bar)

        baseline = Line(uniform_center + LEFT * 2, uniform_center + RIGHT * 2, color=SECONDARY_TEXT, stroke_width=2)

        uniform_formula = MathTex(r"\pi(t) = \frac{1}{T_{\max}}", font_size=28, color=SURVIVE_COLOR)
        uniform_formula.next_to(baseline, DOWN, buff=0.4)

        self.play(
            Create(baseline),
            LaggedStart(*[GrowFromEdge(bar, DOWN) for bar in uniform_bars], lag_ratio=0.1),
            run_time=0.8
        )
        self.play(Write(uniform_formula), run_time=0.4)

        self.wait(0.5)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.6)

    def scene6_kl_divergence(self):
        """Scene 6: KL Divergence (5 seconds)"""
        title = Tex(r"KL Divergence: matching distributions", font_size=28, color=SECONDARY_TEXT)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.6)

        # 左侧分布
        left_center = LEFT * 3 + DOWN * 0.5
        learned_probs = [0.15, 0.20, 0.15, 0.50]
        left_bars = VGroup()

        for i, prob in enumerate(learned_probs):
            bar = Rectangle(width=0.4, height=prob * 3, color=EXIT_COLOR, fill_opacity=0.8, stroke_width=1)
            bar.move_to(left_center + RIGHT * (i - 1.5) * 0.5 + UP * (prob * 3 / 2))
            left_bars.add(bar)

        left_baseline = Line(left_center + LEFT * 1.3, left_center + RIGHT * 1.3, color=SECONDARY_TEXT, stroke_width=2)
        left_label = MathTex(r"p_\phi(t|x)", font_size=24, color=EXIT_COLOR)
        left_label.next_to(left_baseline, DOWN, buff=0.3)

        # 右侧分布
        right_center = RIGHT * 3 + DOWN * 0.5
        uniform_probs = [0.25, 0.25, 0.25, 0.25]
        right_bars = VGroup()

        for i, prob in enumerate(uniform_probs):
            bar = Rectangle(width=0.4, height=prob * 3, color=SURVIVE_COLOR, fill_opacity=0.8, stroke_width=1)
            bar.move_to(right_center + RIGHT * (i - 1.5) * 0.5 + UP * (prob * 3 / 2))
            right_bars.add(bar)

        right_baseline = Line(right_center + LEFT * 1.3, right_center + RIGHT * 1.3, color=SECONDARY_TEXT, stroke_width=2)
        right_label = MathTex(r"\pi(t)", font_size=24, color=SURVIVE_COLOR)
        right_label.next_to(right_baseline, DOWN, buff=0.3)

        # KL 箭头
        kl_arrow = DoubleArrow(LEFT * 0.8, RIGHT * 0.8, color=HIGHLIGHT_COLOR, stroke_width=3)
        kl_arrow.shift(DOWN * 0.5)
        kl_label = Tex(r"KL Divergence", font_size=20, color=HIGHLIGHT_COLOR)
        kl_label.next_to(kl_arrow, UP, buff=0.15)

        self.play(
            Create(left_baseline), Create(right_baseline),
            LaggedStart(*[GrowFromEdge(bar, DOWN) for bar in left_bars], lag_ratio=0.05),
            LaggedStart(*[GrowFromEdge(bar, DOWN) for bar in right_bars], lag_ratio=0.05),
            Write(left_label), Write(right_label),
            run_time=0.8
        )

        self.play(GrowArrow(kl_arrow), Write(kl_label), run_time=0.4)

        # KL 值
        kl_value = MathTex(r"\text{KL} = 0.8", font_size=24, color=HIGHLIGHT_COLOR)
        kl_value.next_to(kl_arrow, DOWN, buff=0.3)
        self.play(Write(kl_value), run_time=0.3)

        # 变形动画
        target_probs = [0.25, 0.25, 0.25, 0.25]
        new_bars = VGroup()
        for i, prob in enumerate(target_probs):
            bar = Rectangle(width=0.4, height=prob * 3, color=SURVIVE_COLOR, fill_opacity=0.8, stroke_width=1)
            bar.move_to(left_center + RIGHT * (i - 1.5) * 0.5 + UP * (prob * 3 / 2))
            new_bars.add(bar)

        new_kl = MathTex(r"\text{KL} = 0.0", font_size=24, color=HIGHLIGHT_COLOR)
        new_kl.next_to(kl_arrow, DOWN, buff=0.3)

        self.play(
            *[Transform(left_bars[i], new_bars[i]) for i in range(4)],
            Transform(kl_value, new_kl),
            run_time=1.5
        )

        check_mark = MathTex(r"\checkmark", font_size=40, color=SURVIVE_COLOR)
        check_mark.next_to(kl_value, RIGHT, buff=0.3)
        self.play(FadeIn(check_mark, scale=1.5), run_time=0.3)

        self.wait(0.5)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.6)

    def scene7_beta_coefficient(self):
        """Scene 7: Beta Coefficient (4 seconds)"""
        title = Tex(r"Modulating regularization strength with $\beta$", font_size=28, color=SECONDARY_TEXT)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.6)

        formula = MathTex(r"\mathcal{L} = \text{Task Loss} - ", r"\beta", r" \cdot H(p_\phi)", font_size=40)
        formula[1].set_color(HIGHLIGHT_COLOR)
        formula.shift(UP * 1.5)
        self.play(Write(formula), run_time=0.8)

        beta_label = Tex(r"strength coefficient", font_size=20, color=HIGHLIGHT_COLOR)
        beta_label.next_to(formula[1], DOWN, buff=0.4)
        self.play(Write(beta_label), run_time=0.3)

        # 滑块
        slider_center = DOWN * 1
        slider_track = Line(slider_center + LEFT * 3, slider_center + RIGHT * 3, color=SECONDARY_TEXT, stroke_width=4)
        slider_knob = Circle(radius=0.15, color=HIGHLIGHT_COLOR, fill_opacity=1)
        slider_knob.move_to(slider_center)

        low_label = Tex(r"$\beta$ low", font_size=18, color=SECONDARY_TEXT)
        low_label.next_to(slider_track, LEFT, buff=0.3)
        high_label = Tex(r"$\beta$ high", font_size=18, color=SECONDARY_TEXT)
        high_label.next_to(slider_track, RIGHT, buff=0.3)

        self.play(Create(slider_track), FadeIn(slider_knob), Write(low_label), Write(high_label), run_time=0.5)

        self.play(slider_knob.animate.move_to(slider_center + RIGHT * 2.5), run_time=0.5)
        self.play(slider_knob.animate.move_to(slider_center + LEFT * 2.5), run_time=0.5)
        self.play(slider_knob.animate.move_to(slider_center), run_time=0.3)

        tradeoff_text = Tex(r"$\beta$ controls the exploration--exploitation tradeoff", font_size=22, color=WHITE)
        tradeoff_text.to_edge(DOWN, buff=0.5)
        self.play(Write(tradeoff_text), run_time=0.5)

        self.wait(0.3)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.6)

    def scene8_pondernet_geometric(self):
        """Scene 8: PonderNet Geometric (8 seconds) - 一条条曲线出现"""
        # 引用
        citation_box = RoundedRectangle(width=3.5, height=1.2, corner_radius=0.1, color=SECONDARY_TEXT, fill_opacity=0.1, stroke_width=2)
        citation_box.to_corner(UL, buff=0.5)
        citation_title = Tex(r"\textbf{PonderNet}", font_size=22, color=WHITE)
        citation_author = Tex(r"Banino et al., 2021", font_size=14, color=SECONDARY_TEXT)
        citation_content = VGroup(citation_title, citation_author)
        citation_content.arrange(DOWN, buff=0.1)
        citation_content.move_to(citation_box.get_center())

        self.play(FadeIn(citation_box), Write(citation_title), Write(citation_author), run_time=0.8)

        # 坐标轴
        axes = Axes(
            x_range=[0, 8, 1], y_range=[0, 1.0, 0.2],
            x_length=7, y_length=3.5,
            axis_config={"color": SECONDARY_TEXT, "include_tip": False},
        )
        axes.shift(DOWN * 0.5 + RIGHT * 0.5)

        x_label = Tex(r"Loop step $t$", font_size=16, color=SECONDARY_TEXT)
        x_label.next_to(axes.x_axis, DOWN, buff=0.3)
        y_label = MathTex(r"\pi(t)", font_size=20, color=SECONDARY_TEXT)
        y_label.next_to(axes.y_axis, UP, buff=0.2)

        self.play(Create(axes), Write(x_label), Write(y_label), run_time=0.6)

        formula = MathTex(r"\pi(t) = (1-\lambda)^{t-1} \cdot \lambda", font_size=26)
        formula.next_to(axes, UP, buff=0.2)
        self.play(Write(formula), run_time=0.5)

        # 绘制曲线 - λ 从 0.1 到 0.9
        lambda_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        colors = [
            "#58a6ff", "#4ECDC4", "#3fb950", "#8BC34A", "#d29922",
            "#FF9800", "#FF5722", "#f85149", "#FF69B4"
        ]

        curves = VGroup()
        legend_items = VGroup()
        all_dots = VGroup()

        for lam, color in zip(lambda_values, colors):
            points = []
            dots = VGroup()
            for t in range(1, 8):
                prob = lam * ((1 - lam) ** (t - 1))
                point = axes.c2p(t, prob)
                points.append(point)
                dot = Dot(point, color=color, radius=0.05)
                dots.add(dot)
            # 使用折线（不是平滑曲线）
            curve = VMobject(color=color, stroke_width=2.5)
            curve.set_points_as_corners(points)
            curves.add(curve)
            all_dots.add(dots)

            legend_line = Line(ORIGIN, RIGHT * 0.4, color=color, stroke_width=3)
            legend_text = MathTex(rf"\lambda = {lam}", font_size=12, color=color)
            legend_item = VGroup(legend_line, legend_text)
            legend_text.next_to(legend_line, RIGHT, buff=0.08)
            legend_items.add(legend_item)

        legend_items.arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        legend_items.to_corner(UR, buff=0.5)

        # 一条条曲线出现（带点标记）
        for curve, dots, legend_item in zip(curves, all_dots, legend_items):
            self.play(Create(curve), FadeIn(dots), FadeIn(legend_item), run_time=0.35)

        # 问题
        x_marks = VGroup()
        for t in [5, 6, 7]:
            x_mark = MathTex(r"\times", font_size=22, color=EXIT_COLOR)
            x_mark.move_to(axes.c2p(t, 0.05))
            x_marks.add(x_mark)

        problem_text = Tex(r"Later steps undertrained!", font_size=20, color=EXIT_COLOR)
        problem_text.to_edge(DOWN, buff=0.5)

        self.play(LaggedStart(*[FadeIn(x, scale=1.5) for x in x_marks], lag_ratio=0.1), run_time=0.5)
        self.play(Write(problem_text), run_time=0.5)

        self.wait(0.5)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.6)

    def scene9_kv_cache_transition(self):
        """Scene 9: KV-Cache Transition (4 seconds)"""
        # 成功
        success_check = MathTex(r"\checkmark", font_size=60, color=SURVIVE_COLOR)
        success_text = Tex(r"\textbf{Looping Mechanism Working!}", font_size=30, color=SURVIVE_COLOR)
        success_group = VGroup(success_check, success_text)
        success_group.arrange(RIGHT, buff=0.4)
        success_group.shift(UP * 1.5)

        self.play(FadeIn(success_check, scale=1.5), Write(success_text), run_time=0.6)
        self.wait(0.3)

        # 警告
        warning_icon = MathTex(r"\triangle", font_size=60, color=HIGHLIGHT_COLOR)
        warning_text = Tex(r"But each loop adds cost...", font_size=26, color=HIGHLIGHT_COLOR)
        warning_group = VGroup(warning_icon, warning_text)
        warning_group.arrange(RIGHT, buff=0.3)
        warning_group.move_to(success_group.get_center())

        self.play(
            Transform(success_check, warning_icon),
            Transform(success_text, warning_text),
            run_time=0.5
        )

        # 内存块
        stack_center = DOWN * 1
        blocks = VGroup()
        block_labels = ["Loop 1 KV-Cache", "Loop 2 KV-Cache", "Loop 3 KV-Cache", "Loop 4 KV-Cache"]

        for i, label_text in enumerate(block_labels):
            block = RoundedRectangle(width=3.5, height=0.55, corner_radius=0.1, color=LOOP_COLOR, fill_opacity=0.7, stroke_width=2)
            block.move_to(stack_center + UP * i * 0.65)
            label = Tex(label_text, font_size=14, color=WHITE)
            label.move_to(block.get_center())
            blocks.add(VGroup(block, label))

        for block in blocks:
            self.play(FadeIn(block, shift=DOWN * 0.15), run_time=0.25)

        icons_text = Tex(r"Each loop = More compute + More memory", font_size=20, color=EXIT_COLOR)
        icons_text.to_edge(DOWN, buff=0.5)
        self.play(Write(icons_text), run_time=0.5)

        self.wait(0.5)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.6)


if __name__ == "__main__":
    print("=" * 60)
    print("Entropy Regularizer - Manim Animation")
    print("=" * 60)
    print("\n运行命令:")
    print("  完整动画: manim -pql entropy_regularizer.py EntropyRegularizer")
    print("  高质量:   manim -pqh entropy_regularizer.py EntropyRegularizer")
    print("\n单独场景:")
    print("  manim -pql entropy_regularizer.py Scene1Title")
    print("  manim -pql entropy_regularizer.py Scene2DistributionSpreading")
    print("  manim -pql entropy_regularizer.py Scene3LossFunction")
    print("  manim -pql entropy_regularizer.py Scene4ExitDistribution")
    print("  manim -pql entropy_regularizer.py Scene5PriorDistribution")
    print("  manim -pql entropy_regularizer.py Scene6KLDivergence")
    print("  manim -pql entropy_regularizer.py Scene7BetaCoefficient")
    print("  manim -pql entropy_regularizer.py Scene8PonderNetGeometric")
    print("  manim -pql entropy_regularizer.py Scene9KVCacheTransition")
    print("=" * 60)

