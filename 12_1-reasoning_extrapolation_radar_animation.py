"""
Reasoning Extrapolation Radar Animation - Ouro 2.6B Thinking Model
展示不同循环深度（T=1到T=8）的推理性能变化
运行命令:
  完整动画: manim -pql 12_1-reasoning_extrapolation_radar_animation.py ReasoningExtrapolationRadarAnimation
  高质量:   manim -pqh 12_1-reasoning_extrapolation_radar_animation.py ReasoningExtrapolationRadarAnimation
"""

from manim import *
import numpy as np

# 颜色配置 - T=1-4 使用蓝色系（训练阶段），T=5-8 使用红色系（外推阶段）
# T越大颜色越浅
COLORS = {
    'T=1': '#1E3A5F',      # 最深蓝色
    'T=2': '#2E5C8A',      # 深蓝色
    'T=3': '#357ABD',      # 中蓝色
    'T=4': '#4A90E2',      # 浅蓝色
    'T=5': '#780000',      # 最深红色
    'T=6': '#A4161A',      # 深红色
    'T=7': '#C1121F',      # 中红色
    'T=8': '#E63946',      # 浅红色
}

# 步骤名称
STEPS = ['T=1', 'T=2', 'T=3', 'T=4', 'T=5', 'T=6', 'T=7', 'T=8']

# 基准测试名称（4个reasoning benchmarks）
BENCHMARKS = [
    'OlympiadBench', 'SuperGPQA', 'AIME 2024', 'AIME 2025'
]

# 原始数据（按表格顺序：T=1到T=8）
# 每行对应一个步骤，列对应：OlympiadBench, SuperGPQA, AIME 2024, AIME 2025
RAW_DATA = np.array([
    # T=1
    [18.96, 15.66, 3.00, 2.00],
    # T=2
    [68.59, 48.58, 52.00, 40.67],
    # T=3 (Best for SuperGPQA, AIME 2024, AIME 2025)
    [75.56, 56.70, 70.33, 50.67],
    # T=4 (Best for OlympiadBench)
    [76.44, 53.68, 64.70, 50.30],
    # T=5 (外推)
    [71.85, 56.45, 57.00, 49.33],
    # T=6 (外推)
    [69.19, 55.44, 56.33, 46.00],
    # T=7 (外推)
    [57.63, 53.32, 49.67, 38.00],
    # T=8 (外推)
    [39.26, 46.84, 39.00, 24.33],
])

# 归一化数据到 0-1 范围（用于雷达图显示）
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
    """推理性能雷达图组件"""
    def __init__(
        self,
        radius=3.5,
        num_vars=4,  # 4 benchmarks
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

        # 计算角度（从顶部开始，顺时针）
        self.angles = np.linspace(np.pi/2, np.pi/2 + 2 * np.pi, num_vars, endpoint=False)

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

    def create_polygon_for_step(self, step_idx, color, fill_opacity=0.2, stroke_width=2.5, is_highlight=False):
        """为步骤创建雷达图多边形（相对于雷达图中心）"""
        values = NORMALIZED_DATA[step_idx]

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
            dot = Dot(point, color=color, radius=0.08 if not is_highlight else 0.12)
            dots.add(dot)

        return VGroup(polygon, dots)


class ReasoningExtrapolationRadarAnimation(Scene):
    """完整的推理外推性能雷达图动画"""
    def construct(self):
        # 设置纯黑色背景
        self.camera.background_color = BLACK

        # Scene 1: 显示坐标轴
        self.show_axis()

        # Scene 2: T=1-4 依次出现（训练阶段）
        self.show_training_steps()

        # Scene 3: T=5-8 依次出现（外推阶段）
        self.show_extrapolation_steps()

        # Scene 4: 高亮 T=3/T=4（最佳推理性能）
        self.highlight_best_reasoning()

    def show_axis(self):
        """显示雷达图坐标轴"""
        # 创建雷达图（整体下移避免与标题重叠）
        self.radar = ReasoningRadarChart(radius=2.8, num_vars=4)
        self.radar_center = LEFT * 1 + DOWN * 0.5
        self.radar.move_to(self.radar_center)

        # 创建基准测试标签
        self.labels = VGroup()
        angles = np.linspace(np.pi/2, np.pi/2 + 2 * np.pi, len(BENCHMARKS), endpoint=False)

        for i, (benchmark, angle) in enumerate(zip(BENCHMARKS, angles)):
            # 顶部标签（OlympiadBench）使用较小的半径，避免与标题重叠
            # 底部标签（AIME 2024）也需要较小的半径，避免超出视频边缘
            if i == 0:  # OlympiadBench 在顶部
                r = 3.1
            elif i == 2:  # AIME 2024 在底部
                r = 3.1
            else:
                r = 3.5
            x = r * np.cos(angle) + self.radar_center[0]
            y = r * np.sin(angle) + self.radar_center[1]

            # 使用 MathTex 渲染标签
            # 处理特殊字符
            if benchmark == 'AIME 2024':
                label = MathTex(r"\text{AIME 2024}", font_size=24, color=GREY_B)
            elif benchmark == 'AIME 2025':
                label = MathTex(r"\text{AIME 2025}", font_size=24, color=GREY_B)
            else:
                label = MathTex(r"\text{" + benchmark + "}", font_size=24, color=GREY_B)
            label.move_to(np.array([x, y, 0]))
            self.labels.add(label)

        # 标题
        self.title = MathTex(
            r"\text{Reasoning Performance by Recurrent Depth (Ouro 2.6B Thinking)}",
            font_size=26,
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
            LaggedStart(*[FadeIn(label) for label in self.labels], lag_ratio=0.08),
            run_time=1.2
        )

        self.wait(0.5)

    def show_training_steps(self):
        """T=1-4 依次出现（训练阶段）"""
        # 图例位置 - 使用更紧凑的间距
        self.legend_start = RIGHT * 4.5 + UP * 2.8
        legend_spacing = 0.38

        self.all_polygons = VGroup()
        self.legend_items = VGroup()

        # T=1-4 依次出现（蓝色系）
        for idx in range(4):
            step = STEPS[idx]
            color = COLORS[step]

            # 创建多边形
            polygon_group = self.radar.create_polygon_for_step(
                idx, color,
                fill_opacity=0.15,
                stroke_width=2
            )

            # 图例项
            legend_dot = Dot(color=color, radius=0.06)
            legend_text = MathTex(r"\text{" + step + "}", font_size=18, color=color)
            legend_text.next_to(legend_dot, RIGHT, buff=0.1)
            legend_item = VGroup(legend_dot, legend_text)
            legend_item.move_to(self.legend_start + DOWN * (idx * legend_spacing))

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

        # 添加训练阶段说明 - 放在 T=4 下方
        training_label = MathTex(
            r"\text{Training (T=1-4)}",
            font_size=18,
            color='#357ABD'
        )
        training_label.move_to(self.legend_start + DOWN * (4 * legend_spacing + 0.2))
        self.training_label = training_label
        self.play(FadeIn(training_label), run_time=0.8)

        self.wait(0.5)

        # 保存间距供后续使用
        self.legend_spacing = legend_spacing

    def show_extrapolation_steps(self):
        """T=5-8 依次出现（外推阶段）"""
        # 更新标题
        new_title = MathTex(
            r"\text{Extrapolation Performance (Trained on T=4)}",
            font_size=26,
            color='#E63946'
        )
        new_title.to_edge(UP, buff=0.4)

        self.play(Transform(self.title, new_title), run_time=0.8)

        # 淡化训练阶段的线条
        self.play(
            *[p[0].animate.set_stroke(opacity=0.4).set_fill(opacity=0.08) for p in self.all_polygons],
            *[p[1].animate.set_opacity(0.4) for p in self.all_polygons],
            *[item.animate.set_opacity(0.5) for item in self.legend_items],
            self.training_label.animate.set_opacity(0.5),
            run_time=0.8
        )

        # T=5-8 依次出现（红色系）
        # 计算外推阶段图例起始位置：训练阶段图例底部 + 间距
        extrapolation_legend_start = self.legend_start + DOWN * (4 * self.legend_spacing + 0.5)

        for idx in range(4, 8):
            step = STEPS[idx]
            color = COLORS[step]

            # 创建多边形
            polygon_group = self.radar.create_polygon_for_step(
                idx, color,
                fill_opacity=0.15,
                stroke_width=2
            )

            # 图例项
            legend_dot = Dot(color=color, radius=0.06)
            legend_text = MathTex(r"\text{" + step + "}", font_size=18, color=color)
            legend_text.next_to(legend_dot, RIGHT, buff=0.1)
            legend_item = VGroup(legend_dot, legend_text)
            legend_item.move_to(extrapolation_legend_start + DOWN * ((idx - 4) * self.legend_spacing))

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

        # 添加外推阶段说明 - 放在 T=8 下方
        extrapolation_label = MathTex(
            r"\text{Extrapolation (T=5-8)}",
            font_size=18,
            color='#E63946'
        )
        extrapolation_label.move_to(extrapolation_legend_start + DOWN * (4 * self.legend_spacing + 0.2))
        self.extrapolation_label = extrapolation_label
        self.play(FadeIn(extrapolation_label), run_time=0.8)

    def highlight_best_reasoning(self):
        """高亮 T=3（最佳推理性能）"""
        # 更新标题
        final_title = MathTex(
            r"\text{Performance Around Trained Depth}",
            font_size=26,
            color='#2E5C8A'
        )
        final_title.to_edge(UP, buff=0.4)

        self.play(Transform(self.title, final_title), run_time=0.8)

        # 淡化其他所有步骤（除了 T=3，即 index 2）
        self.play(
            *[p[0].animate.set_stroke(opacity=0.3).set_fill(opacity=0.05) for i, p in enumerate(self.all_polygons) if i != 2],
            *[p[1].animate.set_opacity(0.3) for i, p in enumerate(self.all_polygons) if i != 2],
            *[item.animate.set_opacity(0.4) for i, item in enumerate(self.legend_items) if i != 2],
            self.training_label.animate.set_opacity(0.4),
            self.extrapolation_label.animate.set_opacity(0.4),
            run_time=0.8
        )

        # 高亮 T=3
        t3_color = COLORS['T=3']
        t3_polygon = self.radar.create_polygon_for_step(
            2, t3_color,  # index 2 = T=3
            fill_opacity=0.35,
            stroke_width=4,
            is_highlight=True
        )

        # 替换 T=3 的多边形
        self.play(
            FadeOut(self.all_polygons[2]),
            Create(t3_polygon[0]),
            run_time=1.2
        )
        self.play(
            LaggedStart(*[GrowFromCenter(dot) for dot in t3_polygon[1]], lag_ratio=0.1),
            run_time=1
        )

        # 高亮 T=3 图例
        self.play(
            self.legend_items[2].animate.scale(1.15).set_opacity(1),
            run_time=0.8
        )

        # 显示 T=3 的数值
        angles = np.linspace(np.pi/2, np.pi/2 + 2 * np.pi, len(BENCHMARKS), endpoint=False)
        value_labels = VGroup()
        t3_values = RAW_DATA[2]  # T=3 data

        for i, (angle, value) in enumerate(zip(angles, t3_values)):
            norm_value = NORMALIZED_DATA[2, i]
            r = self.radar.radius * norm_value + 0.4
            x = r * np.cos(angle) + self.radar_center[0]
            y = r * np.sin(angle) + self.radar_center[1]

            # 使用 MathTex 渲染数值
            value_label = MathTex(f'{value:.2f}', font_size=16, color=t3_color)
            value_label.move_to(np.array([x, y, 0]))
            value_labels.add(value_label)

        self.play(
            LaggedStart(*[FadeIn(vl, scale=1.3) for vl in value_labels], lag_ratio=0.08),
            run_time=1.2
        )

        # 添加说明文本 - 放在雷达图下方
        note_text = MathTex(
            r"\text{Performance strongest around trained depth}",
            font_size=18,
            color='#FFD700'
        )
        note_text.move_to(self.radar_center + DOWN * 3.3)
        self.play(Write(note_text), run_time=1)

        self.wait(2)

        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=1
        )


if __name__ == "__main__":
    print("=" * 60)
    print("推理外推性能雷达图动画 - Ouro 2.6B Thinking Model")
    print("=" * 60)
    print("\n运行命令:")
    print("  完整动画: manim -pql 12_1-reasoning_extrapolation_radar_animation.py ReasoningExtrapolationRadarAnimation")
    print("  高质量:   manim -pqh 12_1-reasoning_extrapolation_radar_animation.py ReasoningExtrapolationRadarAnimation")
    print("=" * 60)

