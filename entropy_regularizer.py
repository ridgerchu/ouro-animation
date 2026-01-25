"""
Entropy Regularizer 可视化动画
运行命令:
  完整动画: manim -pql entropy_regularizer.py EntropyRegularizer
  单独场景: manim -pql entropy_regularizer.py Scene1Title
           manim -pql entropy_regularizer.py Scene2DistributionSpreading
           manim -pql entropy_regularizer.py Scene3LossFunction
           manim -pql entropy_regularizer.py Scene8PonderNetGeometric
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


# ===== Scene 3: Loss Function with KL Divergence =====
class Scene3LossFunction(Scene):
    """Scene 3: The Loss Function with KL Divergence, Highlights, and Beta Control (~18 seconds)"""
    def construct(self):
        # 设置纯黑色背景
        self.camera.background_color = BLACK

        # ===== Phase A: 显示基础损失 (0-2s) =====
        # 第一项：期望任务损失
        term1 = MathTex(
            r"\mathcal{L} = \sum_{t=1}^{T_{\max}} p_\phi(t \mid x)\,\mathcal{L}^{(t)}",
            font_size=42
        )
        term1.shift(UP * 1.5)

        self.play(Write(term1), run_time=1.5)

        # 下括号：expected task loss
        brace1 = Brace(term1[0][2:], DOWN, color=SECONDARY_TEXT)
        brace1_label = Tex(r"expected task loss", font_size=18, color=SECONDARY_TEXT)
        brace1_label.next_to(brace1, DOWN, buff=0.1)

        self.play(GrowFromCenter(brace1), Write(brace1_label), run_time=0.8)

        self.wait(0.5)

        # ===== Phase B: 添加 KL 项 (2-5s) =====
        # 准备 KL 项 - 分段以便后续高亮（beta 单独分出来）
        kl_term = MathTex(
            r"-",
            r"\beta",  # [1] - beta coefficient
            r"\cdot \text{KL}\big(",
            r"p_\phi(\cdot \mid x)",  # [3] - exit distribution
            r"\,\|\,",
            r"\pi(\cdot)",  # [5] - prior distribution
            r"\big)",
            font_size=42,
            color=LOOP_COLOR
        )
        # 先定位到 term1 右侧
        kl_term.next_to(term1, RIGHT, buff=0.15)

        # 计算完整公式的中心位置
        full_width = term1.get_width() + kl_term.get_width() + 0.15
        target_center = ORIGIN + UP * 1.5
        shift_amount = target_center + LEFT * (full_width / 2 - term1.get_width() / 2) - term1.get_center()

        # 左移第一项、大括号和标签，为第二项腾出空间
        self.play(
            term1.animate.shift(shift_amount),
            brace1.animate.shift(shift_amount),
            brace1_label.animate.shift(shift_amount),
            run_time=0.5
        )

        # 更新 KL 项位置
        kl_term.next_to(term1, RIGHT, buff=0.15)

        self.play(Write(kl_term), run_time=1.5)

        # 第二项的下括号 - 与第一个括号对齐
        brace2 = Brace(kl_term, DOWN, color=LOOP_COLOR)
        # 让两个括号在同一高度（顶部对齐）
        brace2.align_to(brace1, UP)
        brace2_label = Tex(r"KL divergence regularization", font_size=18, color=LOOP_COLOR)
        brace2_label.next_to(brace2, DOWN, buff=0.1)

        self.play(GrowFromCenter(brace2), Write(brace2_label), run_time=0.8)

        self.wait(0.5)

        # ===== Phase C: 高亮三个部分 (5-12s) =====
        # 淡化括号和标签
        self.play(
            brace1.animate.set_opacity(0.3),
            brace1_label.animate.set_opacity(0.3),
            brace2.animate.set_opacity(0.3),
            brace2_label.animate.set_opacity(0.3),
            run_time=0.4
        )

        # ===== 高亮 1: Exit Distribution =====
        exit_label = Tex(r"exit distribution", font_size=20, color=EXIT_COLOR)
        exit_label.next_to(kl_term[3], DOWN, buff=1.2)
        exit_arrow = Arrow(
            exit_label.get_top(), kl_term[3].get_bottom() + DOWN * 0.3,
            color=EXIT_COLOR, stroke_width=2, max_tip_length_to_length_ratio=0.15
        )

        self.play(kl_term[3].animate.set_color(EXIT_COLOR).scale(1.15), run_time=0.4)
        self.play(GrowArrow(exit_arrow), Write(exit_label), run_time=0.5)
        self.wait(0.6)
        self.play(
            kl_term[3].animate.scale(1/1.15),
            FadeOut(exit_arrow), FadeOut(exit_label),
            run_time=0.4
        )

        # ===== 高亮 2: Prior Distribution =====
        prior_label = Tex(r"prior distribution", font_size=20, color=SURVIVE_COLOR)
        prior_label.next_to(kl_term[5], DOWN, buff=1.2)
        prior_arrow = Arrow(
            prior_label.get_top(), kl_term[5].get_bottom() + DOWN * 0.3,
            color=SURVIVE_COLOR, stroke_width=2, max_tip_length_to_length_ratio=0.15
        )

        self.play(kl_term[5].animate.set_color(SURVIVE_COLOR).scale(1.15), run_time=0.4)
        self.play(GrowArrow(prior_arrow), Write(prior_label), run_time=0.5)
        self.wait(0.6)
        self.play(
            kl_term[5].animate.scale(1/1.15),
            FadeOut(prior_arrow), FadeOut(prior_label),
            run_time=0.4
        )

        # ===== 高亮 3: KL Divergence =====
        kl_highlight_label = Tex(r"KL Divergence", font_size=22, color=HIGHLIGHT_COLOR)
        kl_highlight_label.next_to(kl_term, DOWN, buff=1.0)
        kl_box = SurroundingRectangle(
            kl_term, color=HIGHLIGHT_COLOR,
            buff=0.12, stroke_width=2.5, corner_radius=0.1
        )

        self.play(Create(kl_box), Write(kl_highlight_label), run_time=0.6)
        self.wait(0.8)
        self.play(FadeOut(kl_box), FadeOut(kl_highlight_label), run_time=0.4)

        # ===== Phase D: Beta 调节作用 =====
        # 淡出括号，公式组上移
        formula_group = VGroup(term1, kl_term)

        self.play(
            FadeOut(brace1), FadeOut(brace1_label),
            FadeOut(brace2), FadeOut(brace2_label),
            formula_group.animate.shift(UP * 0.8),
            run_time=0.5
        )

        # 直接高亮已有的 beta（kl_term[1]）
        self.play(
            kl_term[1].animate.set_color(HIGHLIGHT_COLOR).scale(1.3),
            run_time=0.5
        )
        self.wait(0.3)

        # 在下半屏幕创建简洁的滑块可视化（无描述文字）
        slider_center = DOWN * 1.5

        # 滑块轨道
        slider_track = Line(
            slider_center + LEFT * 3.5,
            slider_center + RIGHT * 3.5,
            color=SECONDARY_TEXT,
            stroke_width=4
        )

        # 滑块
        slider_knob = Circle(
            radius=0.18,
            color=HIGHLIGHT_COLOR,
            fill_opacity=1
        )
        slider_knob.move_to(slider_center)

        # 只保留左右标签
        low_label = Tex(r"$\beta$ small", font_size=20, color=SECONDARY_TEXT)
        low_label.next_to(slider_track, LEFT, buff=0.3)

        high_label = Tex(r"$\beta$ large", font_size=20, color=SECONDARY_TEXT)
        high_label.next_to(slider_track, RIGHT, buff=0.3)

        self.play(
            Create(slider_track),
            FadeIn(slider_knob),
            Write(low_label),
            Write(high_label),
            run_time=0.6
        )

        # 滑块移动动画
        self.play(slider_knob.animate.move_to(slider_center + RIGHT * 2.8), run_time=0.5)
        self.play(slider_knob.animate.move_to(slider_center + LEFT * 2.8), run_time=0.5)
        self.play(slider_knob.animate.move_to(slider_center), run_time=0.4)

        self.wait(0.8)

        # 淡出
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


# ===== Scene 8: PonderNet and Geometric Prior =====
class Scene8PonderNetGeometric(Scene):
    """Scene 8: PonderNet and Geometric Prior
    左右对比: 左侧 prior distribution, 右侧 loss curves
    """
    def construct(self):
        import re
        from pathlib import Path

        # 设置纯黑色背景
        self.camera.background_color = BLACK

        # ===== 定义统一的颜色映射 (从大 λ 到小 λ) =====
        # 使用全部9个 lambda 值 (0.1-0.9)
        lambda_color_map = {
            0.9: "#FF69B4",  # 粉色
            0.8: "#f85149",  # 红色
            0.7: "#FF5722",  # 深橙
            0.6: "#FF9800",  # 橙色
            0.5: "#d29922",  # 黄色
            0.4: "#8BC34A",  # 浅绿
            0.3: "#3fb950",  # 绿色
            0.2: "#4ECDC4",  # 青色
            0.1: "#58a6ff",  # 蓝色
        }
        uniform_color = HIGHLIGHT_COLOR  # 高亮黄色

        # ===== Phase A: 引用 =====
        citation_title = Tex(r"\textbf{PonderNet}", font_size=24, color=WHITE)
        citation_author = Tex(r"Banino et al., 2021", font_size=16, color=SECONDARY_TEXT)
        citation_org = Tex(r"Google DeepMind", font_size=14, color=LOOP_COLOR)

        citation_content = VGroup(citation_title, citation_author, citation_org)
        citation_content.arrange(DOWN, buff=0.15)
        citation_content.to_corner(UL, buff=0.5)

        self.play(
            Write(citation_title),
            Write(citation_author),
            Write(citation_org),
            run_time=1
        )

        # ===== Phase B: 显示几何分布 =====
        axes = Axes(
            x_range=[0, 5, 1],
            y_range=[0, 1.0, 0.2],
            x_length=8,
            y_length=4,
            axis_config={"color": SECONDARY_TEXT, "include_tip": False},
            y_axis_config={"include_numbers": True, "font_size": 18},
        )
        axes.shift(DOWN * 0.3 + RIGHT * 0.5)

        x_label = Tex(r"Loop step $t$", font_size=18, color=SECONDARY_TEXT)
        x_label.next_to(axes.x_axis, DOWN, buff=0.4)

        y_label = MathTex(r"\pi(t)", font_size=22, color=SECONDARY_TEXT)
        y_label.next_to(axes.y_axis, UP, buff=0.2)

        self.play(Create(axes), Write(x_label), Write(y_label), run_time=0.8)

        # 几何分布曲线 (从大到小: 0.9 到 0.1)
        lambda_values = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]

        curves = VGroup()
        legend_items = VGroup()
        all_dots = VGroup()

        for lam in lambda_values:
            color = lambda_color_map[lam]

            def geometric_dist(t, l=lam):
                return l * ((1 - l) ** (t - 1))

            points = []
            dots = VGroup()
            for t in range(1, 5):
                prob = geometric_dist(t)
                point = axes.c2p(t, prob)
                points.append(point)
                dot = Dot(point, color=color, radius=0.04)
                dots.add(dot)

            curve = VMobject(color=color, stroke_width=2.5)
            curve.set_points_as_corners(points)
            curves.add(curve)
            all_dots.add(dots)

            legend_line = Line(ORIGIN, RIGHT * 0.35, color=color, stroke_width=2.5)
            legend_text = MathTex(rf"\lambda = {lam}", font_size=12, color=color)
            legend_item = VGroup(legend_line, legend_text)
            legend_text.next_to(legend_line, RIGHT, buff=0.06)
            legend_items.add(legend_item)

        legend_items.arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        legend_items.to_corner(UR, buff=0.4)

        formula = MathTex(r"\pi(t) = (1-\lambda)^{t-1} \cdot \lambda", font_size=28)
        formula.next_to(axes, UP, buff=0.3)

        self.play(Write(formula), run_time=0.6)

        # 一条条曲线出现 (从大 λ 到小 λ)
        for curve, dots, legend_item in zip(curves, all_dots, legend_items):
            self.play(
                Create(curve),
                FadeIn(dots),
                FadeIn(legend_item),
                run_time=0.3
            )

        self.wait(0.5)

        # ===== Phase C: 显示 Uniform Distribution =====
        T_max = 4
        uniform_prob = 1.0 / T_max

        uniform_points = []
        uniform_dots = VGroup()
        for t in range(1, 5):
            point = axes.c2p(t, uniform_prob)
            uniform_points.append(point)
            dot = Dot(point, color=uniform_color, radius=0.08)
            uniform_dots.add(dot)

        uniform_curve = VMobject(color=uniform_color, stroke_width=4)
        uniform_curve.set_points_as_corners(uniform_points)

        uniform_legend_line = Line(ORIGIN, RIGHT * 0.4, color=uniform_color, stroke_width=4)
        uniform_legend_text = Tex(r"Uniform", font_size=14, color=uniform_color)
        uniform_legend_item = VGroup(uniform_legend_line, uniform_legend_text)
        uniform_legend_text.next_to(uniform_legend_line, RIGHT, buff=0.08)
        uniform_legend_item.next_to(legend_items, DOWN, aligned_edge=LEFT, buff=0.15)

        # 淡化之前的曲线
        self.play(
            *[c.animate.set_stroke(opacity=0.3) for c in curves],
            *[d.animate.set_fill(opacity=0.3) for d in all_dots],
            *[item.animate.set_opacity(0.3) for item in legend_items],
            run_time=0.5
        )

        # 显示 uniform 分布
        self.play(
            Create(uniform_curve),
            LaggedStart(*[FadeIn(d, scale=1.5) for d in uniform_dots], lag_ratio=0.1),
            FadeIn(uniform_legend_item),
            run_time=0.8
        )

        self.wait(0.5)

        # ===== Phase D: 移动到左侧，右侧显示 Loss 曲线 =====
        # 恢复曲线透明度
        self.play(
            *[c.animate.set_stroke(opacity=1.0) for c in curves],
            *[d.animate.set_fill(opacity=1.0) for d in all_dots],
            *[item.animate.set_opacity(1.0) for item in legend_items],
            run_time=0.3
        )

        # 将 prior distribution 组合并移动到左边（不包含 citation）
        prior_group = VGroup(
            axes, x_label, y_label, formula,
            curves, all_dots, legend_items,
            uniform_curve, uniform_dots, uniform_legend_item
        )

        self.play(
            FadeOut(citation_content),
            prior_group.animate.scale(0.55).move_to(LEFT * 3.5),
            run_time=0.8
        )

        # ===== 读取 Loss 数据 =====
        base_dir = Path("/Users/ridgerchu/Documents/科研/Ouro/Podcast for Ouro/ouro-animation/geo_vs_uni")

        def extract_loss_from_log(log_file_path, start_step=20000, end_step=40960):
            steps_list = []
            losses_list = []
            with open(log_file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    match = re.search(r'step:\s*([0-9,]+).*?loss:\s*([0-9.]+)', line)
                    if match:
                        step = int(match.group(1).replace(',', ''))
                        loss = float(match.group(2))
                        if start_step <= step <= end_step:
                            steps_list.append(step)
                            losses_list.append(loss)
            return steps_list, losses_list

        def calculate_sliding_average(steps_in, losses_in, window_size=300):
            if len(losses_in) < window_size:
                return steps_in, losses_in
            smoothed_losses = []
            smoothed_steps = []
            for i in range(len(losses_in) - window_size + 1):
                avg_loss = np.mean(losses_in[i:i + window_size])
                avg_step = np.mean(steps_in[i:i + window_size])
                smoothed_losses.append(avg_loss)
                smoothed_steps.append(avg_step)
            return smoothed_steps, smoothed_losses

        # 定义模型配置 - 颜色与左侧对应 (全部9个lambda值)
        models = {
            'geometric_0.9': ('geo_0.9.log', "#FF69B4"),   # 粉色
            'geometric_0.8': ('geo_0.8.log', "#f85149"),   # 红色
            'geometric_0.7': ('geo_0.7.log', "#FF5722"),   # 深橙
            'geometric_0.6': ('geo_0.6.log', "#FF9800"),   # 橙色
            'geometric_0.5': ('geo_0.5.log', "#d29922"),   # 黄色
            'geometric_0.4': ('geo_0.4.log', "#8BC34A"),   # 浅绿
            'geometric_0.3': ('geo_0.3.log', "#3fb950"),   # 绿色
            'geometric_0.2': ('geo_0.2.log', "#4ECDC4"),   # 青色
            'geometric_0.1': ('geo_0.1.log', "#58a6ff"),   # 蓝色
            'uniform': ('uniform.log', uniform_color),     # 高亮黄色
        }

        all_data = {}
        for model_name, (log_file, color) in models.items():
            log_path = base_dir / log_file
            if log_path.exists():
                steps_raw, losses_raw = extract_loss_from_log(log_path, start_step=20000, end_step=40960)
                if steps_raw and losses_raw:
                    smoothed_steps, smoothed_losses = calculate_sliding_average(steps_raw, losses_raw, window_size=300)
                    all_data[model_name] = {
                        'steps': smoothed_steps,
                        'losses': smoothed_losses,
                        'color': color
                    }

        # 找到数据范围
        all_steps_data = []
        all_losses_data = []
        for data in all_data.values():
            all_steps_data.extend(data['steps'])
            all_losses_data.extend(data['losses'])

        min_step = min(all_steps_data)
        max_step = max(all_steps_data)
        min_loss = min(all_losses_data) - 0.02
        max_loss = max(all_losses_data) + 0.02

        # 创建 loss 坐标轴（右侧）
        loss_axes = Axes(
            x_range=[min_step, max_step, 10000],
            y_range=[min_loss, max_loss, 0.05],
            x_length=5.5,
            y_length=3.5,
            axis_config={"color": SECONDARY_TEXT, "include_tip": False},
            y_axis_config={"include_numbers": True, "font_size": 12, "decimal_number_config": {"num_decimal_places": 2}},
            x_axis_config={"include_numbers": True, "font_size": 12},
        )
        loss_axes.move_to(RIGHT * 3.2)

        loss_x_label = Tex(r"Steps", font_size=14, color=SECONDARY_TEXT)
        loss_x_label.next_to(loss_axes.x_axis, DOWN, buff=0.25)
        loss_y_label = Tex(r"Loss", font_size=14, color=SECONDARY_TEXT)
        loss_y_label.next_to(loss_axes.y_axis, LEFT, buff=0.1).shift(UP * 1.2)

        self.play(Create(loss_axes), Write(loss_x_label), Write(loss_y_label), run_time=0.6)

        # 准备 loss 曲线 (从大 λ 到小 λ)
        loss_curves = VGroup()
        geometric_models = ['geometric_0.9', 'geometric_0.8', 'geometric_0.7', 'geometric_0.6', 'geometric_0.5',
                           'geometric_0.4', 'geometric_0.3', 'geometric_0.2', 'geometric_0.1']

        # 一条条曲线出现 (从大 λ 到小 λ)
        for model_name in geometric_models:
            if model_name not in all_data:
                continue
            data = all_data[model_name]
            color = data['color']
            steps_data = data['steps']
            losses_data = data['losses']

            sample_rate = max(1, len(steps_data) // 150)
            sampled_steps = steps_data[::sample_rate]
            sampled_losses = losses_data[::sample_rate]

            points = [loss_axes.c2p(s, l) for s, l in zip(sampled_steps, sampled_losses)]
            loss_curve = VMobject(color=color, stroke_width=2)
            loss_curve.set_points_as_corners(points)
            loss_curves.add(loss_curve)

            self.play(Create(loss_curve), run_time=0.25)

        self.wait(0.3)

        # ===== Uniform loss 曲线出现并高亮 =====
        if 'uniform' in all_data:
            data = all_data['uniform']
            color = uniform_color
            steps_data = data['steps']
            losses_data = data['losses']

            sample_rate = max(1, len(steps_data) // 150)
            sampled_steps = steps_data[::sample_rate]
            sampled_losses = losses_data[::sample_rate]

            points = [loss_axes.c2p(s, l) for s, l in zip(sampled_steps, sampled_losses)]
            uniform_loss_curve = VMobject(color=color, stroke_width=3.5)
            uniform_loss_curve.set_points_as_corners(points)

            # 淡化之前的曲线
            self.play(
                *[c.animate.set_stroke(opacity=0.3) for c in loss_curves],
                run_time=0.4
            )

            # 显示 uniform 曲线
            self.play(Create(uniform_loss_curve), run_time=0.6)

        self.wait(1.0)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


# ===== 完整动画: EntropyRegularizer =====
class EntropyRegularizer(Scene):
    """完整的 Entropy Regularizer 动画"""
    def construct(self):
        # 设置纯黑色背景
        self.camera.background_color = BLACK

        # Scene 2: Distribution Spreading
        self.scene2_distribution_spreading()

        # Scene 3: Loss Function (includes Beta)
        self.scene3_loss_function()

        # Scene 8: PonderNet Geometric
        self.scene8_pondernet_geometric()

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
        """Scene 3: Loss Function with KL, Highlights, and Beta Control (~18 seconds)"""
        title = Tex(r"Adding KL regularization to the loss", font_size=28, color=SECONDARY_TEXT)
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

        # KL 项 - 分段（beta 单独分出来）
        kl_term = MathTex(
            r"-",
            r"\beta",  # [1] - beta coefficient
            r"\cdot \text{KL}\big(",
            r"p_\phi(\cdot \mid x)",  # [3] - exit distribution
            r"\,\|\,",
            r"\pi(\cdot)",  # [5] - prior distribution
            r"\big)",
            font_size=42, color=LOOP_COLOR
        )
        kl_term.next_to(term1, RIGHT, buff=0.15)

        # 计算偏移
        full_width = term1.get_width() + kl_term.get_width() + 0.15
        target_center = ORIGIN + UP * 1
        shift_amount = target_center + LEFT * (full_width / 2 - term1.get_width() / 2) - term1.get_center()

        # 左移
        self.play(
            term1.animate.shift(shift_amount),
            brace1.animate.shift(shift_amount),
            brace1_label.animate.shift(shift_amount),
            run_time=0.5
        )

        kl_term.next_to(term1, RIGHT, buff=0.15)
        self.play(Write(kl_term), run_time=1.2)

        # KL 项的括号
        brace2 = Brace(kl_term, DOWN, color=LOOP_COLOR)
        brace2.align_to(brace1, UP)
        brace2_label = Tex(r"KL regularization", font_size=18, color=LOOP_COLOR)
        brace2_label.next_to(brace2, DOWN, buff=0.1)
        self.play(GrowFromCenter(brace2), Write(brace2_label), run_time=0.6)

        self.wait(0.4)

        # 淡化括号
        self.play(
            brace1.animate.set_opacity(0.3),
            brace1_label.animate.set_opacity(0.3),
            brace2.animate.set_opacity(0.3),
            brace2_label.animate.set_opacity(0.3),
            run_time=0.3
        )

        # 高亮 1: Exit Distribution
        exit_label = Tex(r"exit distribution", font_size=18, color=EXIT_COLOR)
        exit_label.next_to(kl_term[3], DOWN, buff=1.0)
        exit_arrow = Arrow(
            exit_label.get_top(), kl_term[3].get_bottom() + DOWN * 0.25,
            color=EXIT_COLOR, stroke_width=2, max_tip_length_to_length_ratio=0.15
        )

        self.play(kl_term[3].animate.set_color(EXIT_COLOR).scale(1.12), run_time=0.3)
        self.play(GrowArrow(exit_arrow), Write(exit_label), run_time=0.4)
        self.wait(0.5)
        self.play(
            kl_term[3].animate.scale(1/1.12),
            FadeOut(exit_arrow), FadeOut(exit_label),
            run_time=0.3
        )

        # 高亮 2: Prior Distribution
        prior_label = Tex(r"prior distribution", font_size=18, color=SURVIVE_COLOR)
        prior_label.next_to(kl_term[5], DOWN, buff=1.0)
        prior_arrow = Arrow(
            prior_label.get_top(), kl_term[5].get_bottom() + DOWN * 0.25,
            color=SURVIVE_COLOR, stroke_width=2, max_tip_length_to_length_ratio=0.15
        )

        self.play(kl_term[5].animate.set_color(SURVIVE_COLOR).scale(1.12), run_time=0.3)
        self.play(GrowArrow(prior_arrow), Write(prior_label), run_time=0.4)
        self.wait(0.5)
        self.play(
            kl_term[5].animate.scale(1/1.12),
            FadeOut(prior_arrow), FadeOut(prior_label),
            run_time=0.3
        )

        # 高亮 3: KL Divergence
        kl_highlight_label = Tex(r"KL Divergence", font_size=20, color=HIGHLIGHT_COLOR)
        kl_highlight_label.next_to(kl_term, DOWN, buff=0.85)
        kl_box = SurroundingRectangle(
            kl_term, color=HIGHLIGHT_COLOR,
            buff=0.1, stroke_width=2, corner_radius=0.1
        )

        self.play(Create(kl_box), Write(kl_highlight_label), run_time=0.5)
        self.wait(0.6)
        self.play(FadeOut(kl_box), FadeOut(kl_highlight_label), run_time=0.3)

        # ===== Phase D: Beta 调节 =====
        # 淡出括号，公式组上移
        formula_group = VGroup(term1, kl_term)

        self.play(
            FadeOut(brace1), FadeOut(brace1_label),
            FadeOut(brace2), FadeOut(brace2_label),
            formula_group.animate.shift(UP * 0.6),
            run_time=0.4
        )

        # 直接高亮已有的 beta（kl_term[1]）
        self.play(
            kl_term[1].animate.set_color(HIGHLIGHT_COLOR).scale(1.25),
            run_time=0.4
        )
        self.wait(0.2)

        # 简洁的滑块可视化（无描述文字）
        slider_center = DOWN * 1.4
        slider_track = Line(slider_center + LEFT * 3, slider_center + RIGHT * 3, color=SECONDARY_TEXT, stroke_width=4)
        slider_knob = Circle(radius=0.15, color=HIGHLIGHT_COLOR, fill_opacity=1)
        slider_knob.move_to(slider_center)

        low_label = Tex(r"$\beta$ small", font_size=18, color=SECONDARY_TEXT)
        low_label.next_to(slider_track, LEFT, buff=0.25)
        high_label = Tex(r"$\beta$ large", font_size=18, color=SECONDARY_TEXT)
        high_label.next_to(slider_track, RIGHT, buff=0.25)

        self.play(
            Create(slider_track), FadeIn(slider_knob),
            Write(low_label), Write(high_label),
            run_time=0.5
        )

        # 滑块移动
        self.play(slider_knob.animate.move_to(slider_center + RIGHT * 2.5), run_time=0.5)
        self.play(slider_knob.animate.move_to(slider_center + LEFT * 2.5), run_time=0.5)
        self.play(slider_knob.animate.move_to(slider_center), run_time=0.3)

        self.wait(0.6)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.6)

    def scene8_pondernet_geometric(self):
        """Scene 8: PonderNet Geometric - 左右对比: 左侧 prior distribution, 右侧 loss curves"""
        import re
        from pathlib import Path

        # ===== 定义统一的颜色映射 (从大 λ 到小 λ) =====
        # 使用全部9个 lambda 值 (0.1-0.9)
        lambda_color_map = {
            0.9: "#FF69B4",  # 粉色
            0.8: "#f85149",  # 红色
            0.7: "#FF5722",  # 深橙
            0.6: "#FF9800",  # 橙色
            0.5: "#d29922",  # 黄色
            0.4: "#8BC34A",  # 浅绿
            0.3: "#3fb950",  # 绿色
            0.2: "#4ECDC4",  # 青色
            0.1: "#58a6ff",  # 蓝色
        }
        uniform_color = HIGHLIGHT_COLOR

        # ===== Phase A: 引用 =====
        citation_box = RoundedRectangle(width=3.5, height=1.2, corner_radius=0.1, color=SECONDARY_TEXT, fill_opacity=0.1, stroke_width=2)
        citation_box.to_corner(UL, buff=0.5)
        citation_title = Tex(r"\textbf{PonderNet}", font_size=22, color=WHITE)
        citation_author = Tex(r"Banino et al., 2021", font_size=14, color=SECONDARY_TEXT)
        citation_content = VGroup(citation_title, citation_author)
        citation_content.arrange(DOWN, buff=0.1)
        citation_content.move_to(citation_box.get_center())

        self.play(FadeIn(citation_box), Write(citation_title), Write(citation_author), run_time=0.8)

        # ===== Phase B: 显示几何分布 =====
        axes = Axes(
            x_range=[0, 5, 1], y_range=[0, 1.0, 0.2],
            x_length=7, y_length=3.5,
            axis_config={"color": SECONDARY_TEXT, "include_tip": False},
            y_axis_config={"include_numbers": True, "font_size": 16},
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

        # 几何分布曲线 (从大到小: 0.9 到 0.1)
        lambda_values = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]

        curves = VGroup()
        legend_items = VGroup()
        all_dots = VGroup()

        for lam in lambda_values:
            color = lambda_color_map[lam]
            points = []
            dots = VGroup()
            for t in range(1, 5):
                prob = lam * ((1 - lam) ** (t - 1))
                point = axes.c2p(t, prob)
                points.append(point)
                dot = Dot(point, color=color, radius=0.04)
                dots.add(dot)

            curve = VMobject(color=color, stroke_width=2)
            curve.set_points_as_corners(points)
            curves.add(curve)
            all_dots.add(dots)

            legend_line = Line(ORIGIN, RIGHT * 0.35, color=color, stroke_width=2.5)
            legend_text = MathTex(rf"\lambda = {lam}", font_size=10, color=color)
            legend_item = VGroup(legend_line, legend_text)
            legend_text.next_to(legend_line, RIGHT, buff=0.06)
            legend_items.add(legend_item)

        legend_items.arrange(DOWN, aligned_edge=LEFT, buff=0.04)
        legend_items.to_corner(UR, buff=0.4)

        # 一条条曲线出现 (从大 λ 到小 λ)
        for curve, dots, legend_item in zip(curves, all_dots, legend_items):
            self.play(Create(curve), FadeIn(dots), FadeIn(legend_item), run_time=0.25)

        self.wait(0.3)

        # ===== Phase C: 显示 Uniform Distribution =====
        T_max = 4
        uniform_prob = 1.0 / T_max

        uniform_points = []
        uniform_dots = VGroup()
        for t in range(1, 5):
            point = axes.c2p(t, uniform_prob)
            uniform_points.append(point)
            dot = Dot(point, color=uniform_color, radius=0.06)
            uniform_dots.add(dot)

        uniform_curve = VMobject(color=uniform_color, stroke_width=3.5)
        uniform_curve.set_points_as_corners(uniform_points)

        uniform_legend_line = Line(ORIGIN, RIGHT * 0.4, color=uniform_color, stroke_width=3.5)
        uniform_legend_text = Tex(r"Uniform", font_size=12, color=uniform_color)
        uniform_legend_item = VGroup(uniform_legend_line, uniform_legend_text)
        uniform_legend_text.next_to(uniform_legend_line, RIGHT, buff=0.08)
        uniform_legend_item.next_to(legend_items, DOWN, aligned_edge=LEFT, buff=0.12)

        # 淡化之前的曲线
        self.play(
            *[c.animate.set_stroke(opacity=0.3) for c in curves],
            *[d.animate.set_fill(opacity=0.3) for d in all_dots],
            *[item.animate.set_opacity(0.3) for item in legend_items],
            run_time=0.4
        )

        # 显示 uniform 分布
        self.play(
            Create(uniform_curve),
            LaggedStart(*[FadeIn(d, scale=1.5) for d in uniform_dots], lag_ratio=0.1),
            FadeIn(uniform_legend_item),
            run_time=0.6
        )

        self.wait(0.3)

        # ===== Phase D: 移动到左侧，右侧显示 Loss 曲线 =====
        # 恢复曲线透明度
        self.play(
            *[c.animate.set_stroke(opacity=1.0) for c in curves],
            *[d.animate.set_fill(opacity=1.0) for d in all_dots],
            *[item.animate.set_opacity(1.0) for item in legend_items],
            run_time=0.3
        )

        # 将 prior distribution 组合并移动到左边（不包含 citation）
        prior_group = VGroup(
            axes, x_label, y_label, formula,
            curves, all_dots, legend_items,
            uniform_curve, uniform_dots, uniform_legend_item
        )

        self.play(
            FadeOut(citation_box), FadeOut(citation_content),
            prior_group.animate.scale(0.55).move_to(LEFT * 3.5),
            run_time=0.8
        )

        # ===== 读取 Loss 数据 =====
        base_dir = Path("/Users/ridgerchu/Documents/科研/Ouro/Podcast for Ouro/ouro-animation/geo_vs_uni")

        def extract_loss_from_log(log_file_path, start_step=20000, end_step=40960):
            steps_list = []
            losses_list = []
            with open(log_file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    match = re.search(r'step:\s*([0-9,]+).*?loss:\s*([0-9.]+)', line)
                    if match:
                        step = int(match.group(1).replace(',', ''))
                        loss = float(match.group(2))
                        if start_step <= step <= end_step:
                            steps_list.append(step)
                            losses_list.append(loss)
            return steps_list, losses_list

        def calculate_sliding_average(steps_in, losses_in, window_size=300):
            if len(losses_in) < window_size:
                return steps_in, losses_in
            smoothed_losses = []
            smoothed_steps = []
            for i in range(len(losses_in) - window_size + 1):
                avg_loss = np.mean(losses_in[i:i + window_size])
                avg_step = np.mean(steps_in[i:i + window_size])
                smoothed_losses.append(avg_loss)
                smoothed_steps.append(avg_step)
            return smoothed_steps, smoothed_losses

        # 定义模型配置 - 颜色与左侧对应 (全部9个lambda值)
        models = {
            'geometric_0.9': ('geo_0.9.log', "#FF69B4"),
            'geometric_0.8': ('geo_0.8.log', "#f85149"),
            'geometric_0.7': ('geo_0.7.log', "#FF5722"),
            'geometric_0.6': ('geo_0.6.log', "#FF9800"),
            'geometric_0.5': ('geo_0.5.log', "#d29922"),
            'geometric_0.4': ('geo_0.4.log', "#8BC34A"),
            'geometric_0.3': ('geo_0.3.log', "#3fb950"),
            'geometric_0.2': ('geo_0.2.log', "#4ECDC4"),
            'geometric_0.1': ('geo_0.1.log', "#58a6ff"),
            'uniform': ('uniform.log', uniform_color),
        }

        all_data = {}
        for model_name, (log_file, color) in models.items():
            log_path = base_dir / log_file
            if log_path.exists():
                steps_raw, losses_raw = extract_loss_from_log(log_path, start_step=20000, end_step=40960)
                if steps_raw and losses_raw:
                    smoothed_steps, smoothed_losses = calculate_sliding_average(steps_raw, losses_raw, window_size=300)
                    all_data[model_name] = {
                        'steps': smoothed_steps,
                        'losses': smoothed_losses,
                        'color': color
                    }

        # 找到数据范围
        all_steps_data = []
        all_losses_data = []
        for data in all_data.values():
            all_steps_data.extend(data['steps'])
            all_losses_data.extend(data['losses'])

        min_step = min(all_steps_data)
        max_step = max(all_steps_data)
        min_loss = min(all_losses_data) - 0.02
        max_loss = max(all_losses_data) + 0.02

        # 创建 loss 坐标轴（右侧）
        loss_axes = Axes(
            x_range=[min_step, max_step, 10000],
            y_range=[min_loss, max_loss, 0.05],
            x_length=5.5,
            y_length=3.5,
            axis_config={"color": SECONDARY_TEXT, "include_tip": False},
            y_axis_config={"include_numbers": True, "font_size": 12, "decimal_number_config": {"num_decimal_places": 2}},
            x_axis_config={"include_numbers": True, "font_size": 12},
        )
        loss_axes.move_to(RIGHT * 3.2)

        loss_x_label = Tex(r"Steps", font_size=14, color=SECONDARY_TEXT)
        loss_x_label.next_to(loss_axes.x_axis, DOWN, buff=0.25)
        loss_y_label = Tex(r"Loss", font_size=14, color=SECONDARY_TEXT)
        loss_y_label.next_to(loss_axes.y_axis, LEFT, buff=0.1).shift(UP * 1.2)

        self.play(Create(loss_axes), Write(loss_x_label), Write(loss_y_label), run_time=0.6)

        # 准备 loss 曲线 (从大 λ 到小 λ)
        loss_curves = VGroup()
        geometric_models = ['geometric_0.9', 'geometric_0.8', 'geometric_0.7', 'geometric_0.6', 'geometric_0.5',
                           'geometric_0.4', 'geometric_0.3', 'geometric_0.2', 'geometric_0.1']

        # 一条条曲线出现 (从大 λ 到小 λ)
        for model_name in geometric_models:
            if model_name not in all_data:
                continue
            data = all_data[model_name]
            color = data['color']
            steps_data = data['steps']
            losses_data = data['losses']

            sample_rate = max(1, len(steps_data) // 150)
            sampled_steps = steps_data[::sample_rate]
            sampled_losses = losses_data[::sample_rate]

            points = [loss_axes.c2p(s, l) for s, l in zip(sampled_steps, sampled_losses)]
            loss_curve = VMobject(color=color, stroke_width=2)
            loss_curve.set_points_as_corners(points)
            loss_curves.add(loss_curve)

            self.play(Create(loss_curve), run_time=0.25)

        self.wait(0.3)

        # ===== Uniform loss 曲线出现并高亮 =====
        if 'uniform' in all_data:
            data = all_data['uniform']
            color = uniform_color
            steps_data = data['steps']
            losses_data = data['losses']

            sample_rate = max(1, len(steps_data) // 150)
            sampled_steps = steps_data[::sample_rate]
            sampled_losses = losses_data[::sample_rate]

            points = [loss_axes.c2p(s, l) for s, l in zip(sampled_steps, sampled_losses)]
            uniform_loss_curve = VMobject(color=color, stroke_width=3.5)
            uniform_loss_curve.set_points_as_corners(points)

            # 淡化之前的曲线
            self.play(
                *[c.animate.set_stroke(opacity=0.3) for c in loss_curves],
                run_time=0.4
            )

            # 显示 uniform 曲线
            self.play(Create(uniform_loss_curve), run_time=0.6)

        self.wait(1.0)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


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
    print("  manim -pql entropy_regularizer.py Scene8PonderNetGeometric")
    print("=" * 60)

