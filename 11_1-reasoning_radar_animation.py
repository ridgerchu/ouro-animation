"""
推理能力雷达图模型性能对比动画
运行命令:
  完整动画: manim -pql reasoning_radar_animation.py ReasoningRadarAnimation
  高质量:   manim -pqh reasoning_radar_animation.py ReasoningRadarAnimation
  单独场景:
    manim -pql reasoning_radar_animation.py ReasoningIntroScene
    manim -pql reasoning_radar_animation.py ReasoningAxisScene
    manim -pql reasoning_radar_animation.py ReasoningModelsScene
    manim -pql reasoning_radar_animation.py ReasoningOuroHighlightScene
"""

from manim import *
import numpy as np

# 颜色配置
COLORS = {
    'Ouro-1.4B-Thinking-R4': '#E63946',      # 红色 - Ouro系列
    'Ouro-2.6B-Thinking-R4': '#D62828',       # 深红色 - Ouro系列主角
    'Qwen3-1.7B': '#2A9D8F',                 # 青色
    'Qwen3-4B': '#1ABC9C',                    # 青绿色
    'Qwen3-8B': '#16A085',                    # 深青绿色
    'Deepseek-Distill-Qwen-1.5B': '#E9C46A', # 金色
    'Deepseek-Distill-Qwen-7B': '#F4A261',   # 橙金色
}

# 模型名称（按表格顺序）
MODELS = [
    'Ouro-1.4B-Thinking-R4',
    'Ouro-2.6B-Thinking-R4',
    'Qwen3-1.7B',
    'Qwen3-4B',
    'Qwen3-8B',
    'Deepseek-Distill-Qwen-1.5B',
    'Deepseek-Distill-Qwen-7B'
]

# 基准测试名称（只使用pass@10的数据）
BENCHMARKS = [
    'AIME24',
    'AIME25',
    'Olympiad bench',
    'Beyond AIME',
    'HLE',
    'Super GPQA',
    'GPQA'
]

# 原始数据（按模型顺序，每行对应一个模型）
# 顺序：AIME24 pass@10, AIME25 pass@10, Olympiad bench, Beyond AIME, HLE, Super GPQA, GPQA
RAW_DATA = np.array([
    # Ouro-1.4B-Thinking-R4
    [83.3, 73.3, 71.6, 34.0, 5.21, 47.4, 45.5],
    # Ouro-2.6B-Thinking-R4
    [90.0, 76.7, 76.4, 39.0, 5.58, 53.7, 52.7],
    # Qwen3-1.7B
    [55.6, 33.3, 56.4, 15.0, 4.13, 35.9, 34.0],
    # Qwen3-4B
    [75.0, 63.3, 73.2, 31.0, 5.21, 51.9, 54.5],
    # Qwen3-8B
    [86.7, 81.3, 75.3, 38.0, 2.22, 48.0, 59.1],
    # Deepseek-Distill-Qwen-1.5B
    [66.7, 43.33, 56.44, 9.0, 4.2, 26.5, 33.2],
    # Deepseek-Distill-Qwen-7B
    [83.3, 73.3, 72.0, 30.0, 5.14, 46.6, 51.0],
])

# 归一化数据到 0-1 范围
def normalize_data(data):
    normalized = np.zeros_like(data)
    for i in range(data.shape[1]):
        col_min = data[:, i].min()
        col_max = data[:, i].max()
        if col_max - col_min > 0:
            normalized[:, i] = (data[:, i] - col_min) / (col_max - col_min) * 0.4 + 0.5
        else:
            normalized[:, i] = 0.7
    return normalized

NORMALIZED_DATA = normalize_data(RAW_DATA)


class ReasoningRadarChart(VGroup):
    """推理能力雷达图组件"""
    def __init__(
        self,
        radius=3.5,
        num_vars=7,
        inner_radius_ratio=0.35,
        outer_radius_ratio=1.0,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.radius = radius
        self.num_vars = num_vars
        self.inner_radius = radius * inner_radius_ratio
        self.outer_radius = radius * outer_radius_ratio
        self.center_point = ORIGIN

        # 计算角度
        self.angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False)

        # 创建网格
        self.grid = self._create_grid()
        self.add(self.grid)

        # 创建轴线
        self.axes = self._create_axes()
        self.add(self.axes)

    def set_center(self, center_point):
        """设置雷达图的中心点"""
        self.center_point = center_point
        self.move_to(center_point)

    def _create_grid(self):
        """创建同心圆网格"""
        grid = VGroup()

        # 3个同心圆
        for r_ratio in [0.5, 0.7, 0.9]:
            r = self.radius * r_ratio
            circle = Circle(radius=r, color=GREY, stroke_width=1, stroke_opacity=0.3)
            grid.add(circle)

        return grid

    def _create_axes(self):
        """创建从中心出发的轴线"""
        axes = VGroup()

        for angle in self.angles:
            # 计算终点
            end_x = self.outer_radius * np.cos(angle)
            end_y = self.outer_radius * np.sin(angle)

            line = Line(
                ORIGIN,
                np.array([end_x, end_y, 0]),
                color=GREY,
                stroke_width=1,
                stroke_opacity=0.4
            )
            axes.add(line)

        return axes

    def get_point_at_angle_and_radius(self, angle, radius_ratio):
        """获取给定角度和半径比例的点（相对于雷达图中心）"""
        r = self.radius * radius_ratio
        x = r * np.cos(angle)
        y = r * np.sin(angle)
        return np.array([x, y, 0])

    def create_polygon_for_model(self, model_idx, color, fill_opacity=0.2, stroke_width=2.5, is_highlight=False):
        """为模型创建雷达图多边形（相对于雷达图中心）"""
        values = NORMALIZED_DATA[model_idx]

        # 获取雷达图的中心位置
        radar_center = self.get_center()

        points = []
        for i, angle in enumerate(self.angles):
            # 获取相对于雷达图中心的点
            point_rel = self.get_point_at_angle_and_radius(angle, values[i])
            # 转换为绝对坐标（相对于场景原点）
            point_abs = point_rel + radar_center
            points.append(point_abs)

        # 闭合多边形
        points.append(points[0])

        polygon = Polygon(
            *points,
            color=color,
            fill_opacity=fill_opacity,
            stroke_width=stroke_width if not is_highlight else 4,
            stroke_opacity=1 if is_highlight else 0.9
        )

        # 创建顶点标记
        dots = VGroup()
        for point in points[:-1]:
            dot = Dot(point, color=color, radius=0.08 if not is_highlight else 0.1)
            dots.add(dot)

        return VGroup(polygon, dots)


class ReasoningIntroScene(Scene):
    """引入场景 - 标题"""
    def construct(self):
        # 设置纯黑色背景
        self.camera.background_color = BLACK

        # 主标题
        title = MathTex(
            r"\text{Reasoning Performance Comparison}",
            font_size=48,
            color=WHITE
        )
        title.shift(UP * 0.5)

        # 副标题
        subtitle = MathTex(
            r"\text{Ouro Thinking Models vs Baselines}",
            font_size=32,
            color=GREY_B
        )
        subtitle.next_to(title, DOWN, buff=0.5)

        # 基准测试数量
        benchmark_text = MathTex(
            r"\text{7 Benchmarks: AIME24, AIME25, Olympiad bench, Beyond AIME,}",
            r"\text{HLE, Super GPQA, GPQA}",
            font_size=22,
            color=GREY
        )
        benchmark_text.arrange(DOWN, buff=0.2)
        benchmark_text.to_edge(DOWN, buff=1)

        # 动画
        self.play(Write(title), run_time=1.5)
        self.play(FadeIn(subtitle, shift=UP*0.3), run_time=1)
        self.play(Write(benchmark_text), run_time=1.5)

        self.wait(1)

        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=0.8
        )


class ReasoningAxisScene(Scene):
    """显示雷达图坐标轴"""
    def construct(self):
        # 设置纯黑色背景
        self.camera.background_color = BLACK

        # 标题
        title = MathTex(
            r"\text{Reasoning Radar Chart Framework}",
            font_size=36,
            color=WHITE
        )
        title.to_edge(UP, buff=0.5)

        # 创建雷达图骨架
        radar = ReasoningRadarChart(radius=3.2)
        radar_center = DOWN * 0.3
        radar.move_to(radar_center)

        # 创建基准测试标签
        labels = VGroup()
        angles = np.linspace(0, 2 * np.pi, len(BENCHMARKS), endpoint=False)

        for i, (benchmark, angle) in enumerate(zip(BENCHMARKS, angles)):
            # 计算标签位置（在外圈稍远处，相对于雷达图中心）
            r = 3.8
            x = r * np.cos(angle) + radar_center[0]
            y = r * np.sin(angle) + radar_center[1]
            
            # AIME24 标签向右偏移，避免重叠
            if i == 0:  # AIME24
                x += 0.4

            # 使用 MathTex 渲染标签
            label = MathTex(r"\text{" + benchmark.replace('-', r'{-}') + "}", font_size=30, color=WHITE)
            label.move_to(np.array([x, y, 0]))

            # 调整长标签的旋转
            if angle > np.pi/2 and angle < 3*np.pi/2:
                label.rotate(angle + np.pi)
            else:
                label.rotate(angle)

            labels.add(label)

        # 动画
        self.play(Write(title), run_time=1)
        self.play(Create(radar.grid), run_time=1.5)
        self.play(Create(radar.axes), run_time=1)
        self.play(
            LaggedStart(*[FadeIn(label, scale=0.8) for label in labels], lag_ratio=0.1),
            run_time=2
        )

        self.wait(1)

        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=0.8
        )


class ReasoningModelsScene(Scene):
    """模型依次出现的场景"""
    def construct(self):
        # 设置纯黑色背景
        self.camera.background_color = BLACK

        # 标题
        title = MathTex(
            r"\text{Reasoning Performance Comparison}",
            font_size=32,
            color=WHITE
        )
        title.to_edge(UP, buff=0.4)

        # 创建雷达图
        radar = ReasoningRadarChart(radius=2.8)
        radar_center = LEFT * 1.5 + DOWN * 0.2
        radar.move_to(radar_center)

        # 创建基准测试标签
        labels = VGroup()
        angles = np.linspace(0, 2 * np.pi, len(BENCHMARKS), endpoint=False)

        for i, (benchmark, angle) in enumerate(zip(BENCHMARKS, angles)):
            r = 3.3
            x = r * np.cos(angle) + radar_center[0]
            y = r * np.sin(angle) + radar_center[1]
            
            # AIME24 标签向右偏移，避免重叠
            if i == 0:  # AIME24
                x += 0.4

            # 使用 MathTex 渲染标签
            label = MathTex(r"\text{" + benchmark.replace('-', r'{-}') + "}", font_size=26, color=GREY_B)
            label.move_to(np.array([x, y, 0]))
            labels.add(label)

        # 图例位置（左对齐）
        legend_left_x = 3.8
        legend_start_y = 2

        # 显示基础结构
        self.play(Write(title), run_time=0.8)
        self.play(FadeIn(radar), run_time=1)
        self.play(
            LaggedStart(*[FadeIn(label) for label in labels], lag_ratio=0.05),
            run_time=1
        )

        # 存储所有模型的多边形
        all_polygons = VGroup()
        legend_items = VGroup()

        # 非Ouro模型先出现
        non_ouro_indices = [2, 3, 4, 5, 6]  # Qwen和Deepseek模型
        for idx in non_ouro_indices:
            model = MODELS[idx]
            color = COLORS[model]

            # 创建多边形
            polygon_group = radar.create_polygon_for_model(
                idx, color,
                fill_opacity=0.15,
                stroke_width=2
            )

            # 图例项（左对齐）
            legend_dot = Dot(color=color, radius=0.08)
            # 简化模型名称显示
            model_display = model.replace('-', r'{-}')
            legend_text = MathTex(r"\text{" + model_display + "}", font_size=18, color=color)
            legend_text.next_to(legend_dot, RIGHT, buff=0.15)
            legend_item = VGroup(legend_dot, legend_text)
            # 左对齐：将 dot 放在固定的 x 位置
            legend_item.move_to(np.array([legend_left_x, legend_start_y - len(all_polygons) * 0.5, 0]))
            legend_item.align_to(np.array([legend_left_x, 0, 0]), LEFT)

            # 动画：模型出现
            self.play(
                Create(polygon_group[0]),
                LaggedStart(*[FadeIn(dot, scale=1.5) for dot in polygon_group[1]], lag_ratio=0.05),
                FadeIn(legend_item),
                run_time=1.2
            )

            all_polygons.add(polygon_group)
            legend_items.add(legend_item)

            self.wait(0.5)

        self.wait(1)

        # 将所有内容淡出，准备展示 Ouro
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=0.8
        )


class ReasoningOuroHighlightScene(Scene):
    """Ouro 模型高亮展示场景"""
    def construct(self):
        # 设置纯黑色背景
        self.camera.background_color = BLACK

        # 标题
        title = MathTex(
            r"\text{Ouro Thinking Models - Superior Reasoning}",
            font_size=36,
            color='#E63946'
        )
        title.to_edge(UP, buff=0.4)

        # 副标题
        subtitle = MathTex(
            r"\text{1.4B and 2.6B models outperforming larger baselines}",
            font_size=24,
            color=GREY_B
        )
        subtitle.next_to(title, DOWN, buff=0.3)

        # 创建雷达图
        radar = ReasoningRadarChart(radius=2.8)
        radar_center = LEFT * 1 + DOWN * 0.3
        radar.move_to(radar_center)

        # 基准测试标签
        labels = VGroup()
        angles = np.linspace(0, 2 * np.pi, len(BENCHMARKS), endpoint=False)

        for i, (benchmark, angle) in enumerate(zip(BENCHMARKS, angles)):
            r = 3.3
            x = r * np.cos(angle) + radar_center[0]
            y = r * np.sin(angle) + radar_center[1]
            
            # AIME24 标签向右偏移，避免重叠
            if i == 0:  # AIME24
                x += 0.4

            # 使用 MathTex 渲染标签
            label = MathTex(r"\text{" + benchmark.replace('-', r'{-}') + "}", font_size=26, color=GREY_B)
            label.move_to(np.array([x, y, 0]))
            labels.add(label)

        # 显示基础结构
        self.play(Write(title), run_time=1)
        self.play(FadeIn(subtitle), run_time=0.8)
        self.play(FadeIn(radar), run_time=0.8)
        self.play(
            LaggedStart(*[FadeIn(label) for label in labels], lag_ratio=0.03),
            run_time=0.8
        )

        # 先显示其他模型（淡化）
        other_polygons = VGroup()
        other_indices = [2, 3, 4, 5, 6]  # 非Ouro模型
        for idx in other_indices:
            color = COLORS[MODELS[idx]]
            polygon_group = radar.create_polygon_for_model(
                idx, color,
                fill_opacity=0.08,
                stroke_width=1.5
            )
            polygon_group[0].set_stroke(opacity=0.4)
            for dot in polygon_group[1]:
                dot.set_opacity(0.4)
            other_polygons.add(polygon_group)

        self.play(
            LaggedStart(*[FadeIn(p) for p in other_polygons], lag_ratio=0.15),
            run_time=1.5
        )

        # 图例（其他模型淡化显示，左对齐）
        legend_left_x = 3.8
        legend_start_y = 1.5
        legend_items = VGroup()

        for idx in other_indices:
            model = MODELS[idx]
            color = COLORS[model]
            legend_dot = Dot(color=color, radius=0.08)
            legend_dot.set_opacity(0.5)
            model_display = model.replace('-', r'{-}')
            legend_text = MathTex(r"\text{" + model_display + "}", font_size=16, color=color)
            legend_text.set_opacity(0.5)
            legend_text.next_to(legend_dot, RIGHT, buff=0.15)
            legend_item = VGroup(legend_dot, legend_text)
            legend_item.move_to(np.array([legend_left_x, legend_start_y - len(legend_items) * 0.4, 0]))
            legend_item.align_to(np.array([legend_left_x, 0, 0]), LEFT)
            legend_items.add(legend_item)

        self.play(
            LaggedStart(*[FadeIn(item) for item in legend_items], lag_ratio=0.1),
            run_time=0.8
        )

        self.wait(0.5)

        # ===== Ouro 1.4B 登场 =====
        ouro_14b_color = COLORS['Ouro-1.4B-Thinking-R4']

        # 创建 Ouro 1.4B 多边形
        ouro_14b_polygon = radar.create_polygon_for_model(
            0, ouro_14b_color,
            fill_opacity=0.25,
            stroke_width=3,
            is_highlight=False
        )

        # Ouro 1.4B 图例（左对齐，统一 dot 大小）
        ouro_14b_legend_dot = Dot(color=ouro_14b_color, radius=0.08)
        ouro_14b_legend_text = MathTex(r"\text{Ouro{-}1.4B{-}Thinking{-}R4}", font_size=18, color=ouro_14b_color)
        ouro_14b_legend_text.next_to(ouro_14b_legend_dot, RIGHT, buff=0.15)
        ouro_14b_legend = VGroup(ouro_14b_legend_dot, ouro_14b_legend_text)
        ouro_14b_legend.move_to(np.array([legend_left_x, legend_start_y - len(legend_items) * 0.4, 0]))
        ouro_14b_legend.align_to(np.array([legend_left_x, 0, 0]), LEFT)

        # Ouro 1.4B 登场动画
        self.play(
            Create(ouro_14b_polygon[0]),
            run_time=1.2
        )
        self.play(
            LaggedStart(*[GrowFromCenter(dot) for dot in ouro_14b_polygon[1]], lag_ratio=0.08),
            FadeIn(ouro_14b_legend, scale=1.2),
            run_time=1
        )

        self.wait(0.5)

        # ===== Ouro 2.6B 登场（主角） =====
        ouro_26b_color = COLORS['Ouro-2.6B-Thinking-R4']

        # 创建 Ouro 2.6B 多边形（高亮效果）
        ouro_26b_polygon = radar.create_polygon_for_model(
            1, ouro_26b_color,
            fill_opacity=0.35,
            stroke_width=4,
            is_highlight=True
        )

        # Ouro 2.6B 图例（左对齐，统一 dot 大小）
        ouro_26b_legend_dot = Dot(color=ouro_26b_color, radius=0.08)
        ouro_26b_legend_text = MathTex(r"\textbf{Ouro{-}2.6B{-}Thinking{-}R4}", font_size=18, color=ouro_26b_color)
        ouro_26b_legend_text.next_to(ouro_26b_legend_dot, RIGHT, buff=0.15)
        ouro_26b_legend = VGroup(ouro_26b_legend_dot, ouro_26b_legend_text)
        ouro_26b_legend.move_to(np.array([legend_left_x, legend_start_y - (len(legend_items) + 1) * 0.4, 0]))
        ouro_26b_legend.align_to(np.array([legend_left_x, 0, 0]), LEFT)

        # 高亮圆圈效果
        highlight_circle = Circle(radius=0.3, color=ouro_26b_color, stroke_width=3)
        highlight_circle.move_to(ouro_26b_legend_dot.get_center())

        # Ouro 2.6B 登场动画
        self.play(
            Create(ouro_26b_polygon[0]),
            run_time=1.5
        )
        self.play(
            LaggedStart(*[GrowFromCenter(dot) for dot in ouro_26b_polygon[1]], lag_ratio=0.08),
            run_time=1
        )
        self.play(
            FadeIn(ouro_26b_legend, scale=1.2),
            Create(highlight_circle),
            run_time=0.8
        )
        self.play(
            highlight_circle.animate.scale(1.5).set_opacity(0),
            run_time=0.6
        )
        self.remove(highlight_circle)

        # ===== 显示 Ouro 2.6B 的数值 =====
        self.wait(0.5)

        # 显示 Ouro 2.6B 在各项指标上的数值
        value_labels = VGroup()
        ouro_26b_values = RAW_DATA[1]  # Ouro 2.6B 的原始数据

        for i, (angle, value) in enumerate(zip(angles, ouro_26b_values)):
            # 计算标签位置（在数据点外侧，相对于雷达图中心）
            norm_value = NORMALIZED_DATA[1, i]
            r = radar.radius * norm_value + 0.4
            x = r * np.cos(angle) + radar_center[0]
            y = r * np.sin(angle) + radar_center[1]
            
            # Beyond AIME 数值向下偏移，避免重叠
            if i == 3:  # Beyond AIME
                y -= 0.3

            # 使用 MathTex 渲染数值
            value_label = MathTex(f'{value:.2f}', font_size=14, color=ouro_26b_color)
            value_label.move_to(np.array([x, y, 0]))
            value_labels.add(value_label)

        self.play(
            LaggedStart(*[FadeIn(vl, scale=1.3) for vl in value_labels], lag_ratio=0.08),
            run_time=1.5
        )

        self.wait(2)

        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=1
        )


class ReasoningRadarAnimation(Scene):
    """完整的推理能力雷达图动画"""
    def construct(self):
        # 设置纯黑色背景
        self.camera.background_color = BLACK

        # Scene 1: 显示坐标轴
        self.show_axis()

        # Scene 2: 模型依次出现
        self.show_models_one_by_one()

        # Scene 3: Ouro 高亮展示
        self.highlight_ouro()

    def show_axis(self):
        """显示雷达图坐标轴"""
        # 创建雷达图
        self.radar = ReasoningRadarChart(radius=2.8)
        self.radar_center = LEFT * 1 + DOWN * 0.2
        self.radar.move_to(self.radar_center)

        # 创建基准测试标签
        self.labels = VGroup()
        angles = np.linspace(0, 2 * np.pi, len(BENCHMARKS), endpoint=False)

        for i, (benchmark, angle) in enumerate(zip(BENCHMARKS, angles)):
            r = 3.3
            x = r * np.cos(angle) + self.radar_center[0]
            y = r * np.sin(angle) + self.radar_center[1]
            
            # AIME24 标签向右偏移，避免重叠
            if i == 0:  # AIME24
                x += 0.4

            # 使用 MathTex 渲染标签
            label = MathTex(r"\text{" + benchmark.replace('-', r'{-}') + "}", font_size=26, color=GREY_B)
            label.move_to(np.array([x, y, 0]))
            self.labels.add(label)

        # 标题
        self.title = MathTex(
            r"\text{7 Reasoning Benchmarks Evaluation}",
            font_size=28,
            color=WHITE
        )
        self.title.to_edge(UP, buff=0.4)

        # 动画
        self.play(Write(self.title), run_time=0.8)
        self.play(
            Create(self.radar.grid),
            Create(self.radar.axes),
            run_time=1.5
        )
        self.play(
            LaggedStart(*[FadeIn(label) for label in self.labels], lag_ratio=0.05),
            run_time=1.2
        )

        self.wait(0.5)

    def show_models_one_by_one(self):
        """模型依次出现"""
        # 图例位置（左对齐）
        self.legend_left_x = 3.8
        self.legend_start_y = 2

        self.all_polygons = VGroup()
        self.legend_items = VGroup()

        # 非Ouro模型先出现
        non_ouro_indices = [2, 3, 4, 5, 6]
        for idx in non_ouro_indices:
            model = MODELS[idx]
            color = COLORS[model]

            # 创建多边形
            polygon_group = self.radar.create_polygon_for_model(
                idx, color,
                fill_opacity=0.12,
                stroke_width=2
            )

            # 图例项（左对齐，统一 dot 大小）
            legend_dot = Dot(color=color, radius=0.08)
            model_display = model.replace('-', r'{-}')
            legend_text = MathTex(r"\text{" + model_display + "}", font_size=18, color=color)
            legend_text.next_to(legend_dot, RIGHT, buff=0.15)
            legend_item = VGroup(legend_dot, legend_text)
            legend_item.move_to(np.array([self.legend_left_x, self.legend_start_y - len(self.all_polygons) * 0.45, 0]))
            legend_item.align_to(np.array([self.legend_left_x, 0, 0]), LEFT)

            # 动画
            self.play(
                Create(polygon_group[0]),
                LaggedStart(*[FadeIn(dot, scale=1.3) for dot in polygon_group[1]], lag_ratio=0.05),
                FadeIn(legend_item),
                run_time=1
            )

            self.all_polygons.add(polygon_group)
            self.legend_items.add(legend_item)

            self.wait(0.3)

        self.wait(0.5)

    def highlight_ouro(self):
        """Ouro 高亮展示"""
        ouro_26b_color = COLORS['Ouro-2.6B-Thinking-R4']
        ouro_14b_color = COLORS['Ouro-1.4B-Thinking-R4']

        # 淡化其他模型
        self.play(
            *[p[0].animate.set_stroke(opacity=0.3).set_fill(opacity=0.05) for p in self.all_polygons],
            *[p[1].animate.set_opacity(0.3) for p in self.all_polygons],
            *[item.animate.set_opacity(0.4) for item in self.legend_items],
            run_time=0.8
        )

        # 更新标题
        new_title = MathTex(
            r"\text{Ouro Thinking Models - Superior Reasoning}",
            font_size=26,
            color=ouro_26b_color
        )
        new_title.to_edge(UP, buff=0.4)

        self.play(Transform(self.title, new_title), run_time=0.8)

        # 创建 Ouro 1.4B 多边形
        ouro_14b_polygon = self.radar.create_polygon_for_model(
            0, ouro_14b_color,
            fill_opacity=0.25,
            stroke_width=3,
            is_highlight=False
        )

        # Ouro 1.4B 图例（左对齐，统一 dot 大小）
        ouro_14b_legend_dot = Dot(color=ouro_14b_color, radius=0.08)
        ouro_14b_legend_text = MathTex(r"\text{Ouro{-}1.4B{-}Thinking{-}R4}", font_size=18, color=ouro_14b_color)
        ouro_14b_legend_text.next_to(ouro_14b_legend_dot, RIGHT, buff=0.15)
        ouro_14b_legend = VGroup(ouro_14b_legend_dot, ouro_14b_legend_text)
        ouro_14b_legend.move_to(np.array([self.legend_left_x, self.legend_start_y - len(self.all_polygons) * 0.45, 0]))
        ouro_14b_legend.align_to(np.array([self.legend_left_x, 0, 0]), LEFT)

        # Ouro 1.4B 登场
        self.play(
            Create(ouro_14b_polygon[0]),
            run_time=1.2
        )
        self.play(
            LaggedStart(*[GrowFromCenter(dot) for dot in ouro_14b_polygon[1]], lag_ratio=0.08),
            FadeIn(ouro_14b_legend, scale=1.2),
            run_time=1
        )

        self.wait(0.3)

        # 创建 Ouro 2.6B 多边形
        ouro_26b_polygon = self.radar.create_polygon_for_model(
            1, ouro_26b_color,
            fill_opacity=0.35,
            stroke_width=4,
            is_highlight=True
        )

        # Ouro 2.6B 图例（左对齐，统一 dot 大小）
        ouro_26b_legend_dot = Dot(color=ouro_26b_color, radius=0.08)
        ouro_26b_legend_text = MathTex(r"\textbf{Ouro{-}2.6B{-}Thinking{-}R4}", font_size=18, color=ouro_26b_color)
        ouro_26b_legend_text.next_to(ouro_26b_legend_dot, RIGHT, buff=0.15)
        ouro_26b_legend = VGroup(ouro_26b_legend_dot, ouro_26b_legend_text)
        ouro_26b_legend.move_to(np.array([self.legend_left_x, self.legend_start_y - (len(self.all_polygons) + 1) * 0.45, 0]))
        ouro_26b_legend.align_to(np.array([self.legend_left_x, 0, 0]), LEFT)

        # Ouro 2.6B 登场
        self.play(
            Create(ouro_26b_polygon[0]),
            run_time=1.5
        )
        self.play(
            LaggedStart(*[GrowFromCenter(dot) for dot in ouro_26b_polygon[1]], lag_ratio=0.08),
            FadeIn(ouro_26b_legend, scale=1.2),
            run_time=1
        )

        # 脉冲效果
        pulse = Circle(radius=0.2, color=ouro_26b_color, stroke_width=3)
        pulse.move_to(ouro_26b_legend_dot.get_center())
        self.play(
            Create(pulse),
            pulse.animate.scale(2).set_opacity(0),
            run_time=0.8
        )
        self.remove(pulse)

        # 显示数值
        angles = np.linspace(0, 2 * np.pi, len(BENCHMARKS), endpoint=False)
        value_labels = VGroup()
        ouro_26b_values = RAW_DATA[1]

        for i, (angle, value) in enumerate(zip(angles, ouro_26b_values)):
            norm_value = NORMALIZED_DATA[1, i]
            r = self.radar.radius * norm_value + 0.35
            x = r * np.cos(angle) + self.radar_center[0]
            y = r * np.sin(angle) + self.radar_center[1]
            
            # Beyond AIME 数值向下偏移，避免重叠
            if i == 3:  # Beyond AIME
                y -= 0.3

            # 使用 MathTex 渲染数值
            value_label = MathTex(f'{value:.2f}', font_size=14, color=ouro_26b_color)
            value_label.move_to(np.array([x, y, 0]))
            value_labels.add(value_label)

        self.play(
            LaggedStart(*[FadeIn(vl, scale=1.3) for vl in value_labels], lag_ratio=0.06),
            run_time=1.2
        )

        self.wait(2)

        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=1
        )


if __name__ == "__main__":
    print("=" * 60)
    print("推理能力雷达图模型性能对比 - Manim 动画")
    print("=" * 60)
    print("\n运行命令:")
    print("  完整动画: manim -pql reasoning_radar_animation.py ReasoningRadarAnimation")
    print("  高质量:   manim -pqh reasoning_radar_animation.py ReasoningRadarAnimation")
    print("\n单独场景:")
    print("  manim -pql reasoning_radar_animation.py ReasoningIntroScene")
    print("  manim -pql reasoning_radar_animation.py ReasoningAxisScene")
    print("  manim -pql reasoning_radar_animation.py ReasoningModelsScene")
    print("  manim -pql reasoning_radar_animation.py ReasoningOuroHighlightScene")
    print("=" * 60)

