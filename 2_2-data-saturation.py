"""
数据墙预测可视化动画 (Data Wall Projection)
展示训练数据需求与数据存量的交叉点

运行命令:
  完整动画: manim -pql 2_2-data-saturation.py DataWallProjection
  高质量渲染: manim -pqh 2_2-data-saturation.py DataWallProjection
  4K渲染: manim -pqk 2_2-data-saturation.py DataWallProjection
"""

from manim import *
import numpy as np

# ===== 颜色配置 =====
COLORS = {
    'background': '#000000',           # 纯黑背景
    'grid': '#2a2a35',                  # 网格线颜色
    'grid_fine': '#1a1a22',             # 细网格线
    'text': '#e8e8e8',                  # 文本颜色
    'axis_label': '#b0b0b0',            # 轴标签颜色

    # 数据存量 (Stock of data) - 青绿色系
    'stock_main': '#2dd4bf',            # 青绿色主线
    'stock_fill': '#14b8a6',            # 填充色

    # 数据集预测 (Dataset projection) - 蓝色系
    'projection_main': '#60a5fa',       # 蓝色主线
    'projection_fill': '#3b82f6',       # 填充色

    # 标注线
    'purple_line': '#a855f7',           # 紫色虚线 (5x overtraining)
    'pink_line': '#ec4899',             # 粉色虚线 (median)

    # 散点
    'dot_color': '#9ca3af',             # 灰色圆点
    'dot_outline': '#ffffff',           # 白色轮廓
}


class DataWallProjection(Scene):
    """数据墙预测图 - 展示训练数据需求与存量的交叉"""

    def construct(self):
        # 设置背景
        self.camera.background_color = COLORS['background']

        # ===== 坐标系参数 =====
        # X轴: 2020-2034年，映射到 0-14
        # Y轴: 10^11 到 10^15.5，使用对数坐标，映射到 11-15.5

        x_min, x_max = 0, 14      # 对应 2020-2034
        y_min, y_max = 11, 15.5   # 对应 10^11 到 10^15.5

        # 创建坐标轴（不显示任何数字标签，我们手动添加）
        axes = Axes(
            x_range=[x_min, x_max, 2],  # 每2年一个刻度
            y_range=[y_min, y_max, 1],  # 每个数量级一个刻度
            x_length=10,
            y_length=6,
            axis_config={
                "color": COLORS['axis_label'],
                "stroke_width": 1.5,
                "include_ticks": True,
                "tick_size": 0.1,
                "include_numbers": False,  # 不自动添加数字
            },
            tips=False,
        )
        axes.shift(DOWN * 0.3 + LEFT * 0.3)

        # ===== 添加网格 =====
        grid = self._create_grid(axes, x_min, x_max, y_min, y_max)

        # ===== X轴标签 (年份) - 使用 Tex 渲染 =====
        x_labels = VGroup()
        years = [2020, 2022, 2024, 2026, 2028, 2030, 2032, 2034]
        for i, year in enumerate(years):
            label = Tex(str(year), font_size=28, color=COLORS['axis_label'])
            label.next_to(axes.c2p(i * 2, y_min), DOWN, buff=0.15)
            x_labels.add(label)

        x_axis_label = Tex(r"Year", font_size=32, color=COLORS['text'])
        x_axis_label.next_to(axes, DOWN, buff=0.6)

        # ===== Y轴标签 (对数刻度) - 使用 MathTex 渲染 =====
        y_labels = VGroup()
        for exp in [11, 12, 13, 14, 15]:
            label = MathTex(f"10^{{{exp}}}", font_size=28, color=COLORS['axis_label'])
            label.next_to(axes.c2p(x_min, exp), LEFT, buff=0.2)
            y_labels.add(label)

        y_axis_label = Tex(r"Effective data stock", font_size=28, color=COLORS['text'])
        y_axis_label.rotate(PI/2)
        y_axis_label.next_to(axes, LEFT, buff=0.9)

        # ===== 数据存量带 (Stock of data) - 青绿色 =====
        stock_band = self._create_stock_band(axes)

        # ===== 数据集预测带 (Dataset projection) - 蓝色 =====
        projection_band = self._create_projection_band(axes)

        # ===== 散点数据 (Model Data Points) =====
        model_dots = self._create_model_dots(axes)

        # ===== 图例 =====
        legend = self._create_legend(axes, x_max, y_min)

        # ===== 动画序列 =====

        # 1. 绘制坐标轴和网格
        self.play(
            Create(grid),
            Create(axes),
            run_time=1.5
        )

        # 2. 添加轴标签
        self.play(
            FadeIn(x_labels),
            FadeIn(y_labels),
            Write(x_axis_label),
            Write(y_axis_label),
            run_time=1
        )

        # 3. 绘制数据存量带
        self.play(
            Create(stock_band['lower_line']),
            Create(stock_band['upper_line']),
            Create(stock_band['main_line']),
            FadeIn(stock_band['fill']),
            run_time=1.5
        )

        # 4. 绘制数据集预测带
        self.play(
            Create(projection_band['lower_line']),
            Create(projection_band['upper_line']),
            Create(projection_band['main_line']),
            FadeIn(projection_band['fill']),
            run_time=1.5
        )

        # 5. 添加模型散点
        self.play(
            *[FadeIn(dot, scale=0.5) for dot in model_dots['dots']],
            run_time=1
        )
        self.play(
            *[Write(label) for label in model_dots['labels']],
            run_time=1
        )

        # 6. 添加图例
        self.play(
            FadeIn(legend),
            run_time=0.8
        )

        # 8. 保持展示
        self.wait(3)

        # 9. 淡出
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=1
        )

    def _create_grid(self, axes, x_min, x_max, y_min, y_max):
        """创建背景网格"""
        grid = VGroup()

        # 垂直线 (每2年)
        for x in np.arange(x_min, x_max + 0.1, 2):
            line = Line(
                axes.c2p(x, y_min),
                axes.c2p(x, y_max),
                stroke_width=0.5,
                stroke_color=COLORS['grid'],
                stroke_opacity=0.6
            )
            grid.add(line)

        # 水平线 (每个数量级)
        for y in np.arange(11, 16, 1):
            line = Line(
                axes.c2p(x_min, y),
                axes.c2p(x_max, y),
                stroke_width=0.5,
                stroke_color=COLORS['grid'],
                stroke_opacity=0.6
            )
            grid.add(line)

        # 细网格线 (半个数量级)
        for y in np.arange(11.5, 15.5, 1):
            line = Line(
                axes.c2p(x_min, y),
                axes.c2p(x_max, y),
                stroke_width=0.3,
                stroke_color=COLORS['grid_fine'],
                stroke_opacity=0.3
            )
            grid.add(line)

        return grid

    def _create_stock_band(self, axes):
        """创建数据存量带 (青绿色)"""
        # 数据存量几乎是平缓增长
        # 下界: ~6×10^13 到 ~1×10^14
        # 上界: ~10^15 到 ~2×10^15
        # 中线: ~2-3×10^14

        def stock_lower(x):
            # log10(6×10^13) ≈ 13.78, 缓慢增长到 ~14
            return 13.78 + 0.015 * x

        def stock_upper(x):
            # log10(10^15) = 15, 缓慢增长
            return 15.0 + 0.02 * x

        def stock_mid(x):
            # log10(2.5×10^14) ≈ 14.4
            return 14.4 + 0.018 * x

        # 创建曲线
        x_range = np.linspace(0, 14, 100)

        lower_points = [axes.c2p(x, stock_lower(x)) for x in x_range]
        upper_points = [axes.c2p(x, stock_upper(x)) for x in x_range]
        mid_points = [axes.c2p(x, stock_mid(x)) for x in x_range]

        # 创建实线版本，然后转为虚线
        lower_line_solid = VMobject(stroke_color=COLORS['stock_main'], stroke_width=1.5)
        lower_line_solid.set_points_smoothly(lower_points)
        lower_line = DashedVMobject(lower_line_solid, num_dashes=60, dashed_ratio=0.5)

        upper_line_solid = VMobject(stroke_color=COLORS['stock_main'], stroke_width=1.5)
        upper_line_solid.set_points_smoothly(upper_points)
        upper_line = DashedVMobject(upper_line_solid, num_dashes=60, dashed_ratio=0.5)

        main_line = VMobject(stroke_color=COLORS['stock_main'], stroke_width=2.5)
        main_line.set_points_smoothly(mid_points)

        # 填充区域
        fill_points = lower_points + upper_points[::-1]
        fill = Polygon(*fill_points,
                       fill_color=COLORS['stock_fill'],
                       fill_opacity=0.25,
                       stroke_width=0)

        return {
            'lower_line': lower_line,
            'upper_line': upper_line,
            'main_line': main_line,
            'fill': fill
        }

    def _create_projection_band(self, axes):
        """创建数据集预测带 (蓝色) - S型曲线，与数据存量带交叉"""

        def projection_lower(x):
            # 早期指数增长，后期变缓，最终接近绿线下界
            # 起点: ~10^11, 最终趋近于数据存量下界 (~13.9)
            base = 10.8
            # 使用 S 型曲线 (Logistic function)
            L = 3.5  # 最大增长量
            k = 0.55  # 增长速率
            x0 = 5.5   # 拐点位置 (2025.5年)
            sigmoid = L / (1 + np.exp(-k * (x - x0)))
            return base + sigmoid

        def projection_upper(x):
            # 上界需要超过绿线下界，在2027-2028年左右交叉
            base = 11.5
            L = 4.2  # 更大的增长量，确保能超过绿线
            k = 0.5
            x0 = 5
            sigmoid = L / (1 + np.exp(-k * (x - x0)))
            return base + sigmoid

        def projection_mid(x):
            # 中线在2028-2029年与绿线中线交叉
            base = 11.1
            L = 3.9
            k = 0.52
            x0 = 5.2
            sigmoid = L / (1 + np.exp(-k * (x - x0)))
            return base + sigmoid

        # 创建曲线
        x_range = np.linspace(0, 14, 100)

        lower_points = [axes.c2p(x, projection_lower(x)) for x in x_range]
        upper_points = [axes.c2p(x, projection_upper(x)) for x in x_range]
        mid_points = [axes.c2p(x, projection_mid(x)) for x in x_range]

        # 创建实线版本，然后转为虚线
        lower_line_solid = VMobject(stroke_color=COLORS['projection_main'], stroke_width=1.5)
        lower_line_solid.set_points_smoothly(lower_points)
        lower_line = DashedVMobject(lower_line_solid, num_dashes=60, dashed_ratio=0.5)

        upper_line_solid = VMobject(stroke_color=COLORS['projection_main'], stroke_width=1.5)
        upper_line_solid.set_points_smoothly(upper_points)
        upper_line = DashedVMobject(upper_line_solid, num_dashes=60, dashed_ratio=0.5)

        main_line = VMobject(stroke_color=COLORS['projection_main'], stroke_width=2.5)
        main_line.set_points_smoothly(mid_points)

        # 填充区域
        fill_points = lower_points + upper_points[::-1]
        fill = Polygon(*fill_points,
                       fill_color=COLORS['projection_fill'],
                       fill_opacity=0.25,
                       stroke_width=0)

        return {
            'lower_line': lower_line,
            'upper_line': upper_line,
            'main_line': main_line,
            'fill': fill
        }

    def _create_model_dots(self, axes):
        """创建模型散点和标签"""
        # 模型数据: (年份偏移, log10值, 名称)
        models = [
            (0.5, 11.48, "GPT-3"),        # 2020年中, ~3×10^11
            (1.9, 12.3, "FLAN"),          # 2021年末, ~2×10^12
            (2.1, 11.9, "PaLM"),          # 2022年初, ~8×10^11
            (3.9, 12.48, "Falcon-180B"),  # 2023年末, ~3×10^12
            (4.1, 13.0, "DBRX"),          # 2024年初, ~10^13
            (4.5, 13.18, "Llama 3"),      # 2024年中, ~1.5×10^13
        ]

        dots = VGroup()
        labels = VGroup()

        for x, y, name in models:
            # 创建圆点
            dot = Dot(
                axes.c2p(x, y),
                radius=0.08,
                color=COLORS['dot_color'],
                stroke_color=COLORS['dot_outline'],
                stroke_width=1
            )
            dots.add(dot)

            # 创建标签 (使用 Tex 渲染)
            # 处理特殊字符
            tex_name = name.replace("-", "{-}")
            label = Tex(tex_name, font_size=20, color=COLORS['text'])

            # 根据位置调整标签位置，避免重叠
            if name == "FLAN":
                label.next_to(dot, UP + LEFT, buff=0.1)
            elif name == "PaLM":
                label.next_to(dot, DOWN + RIGHT, buff=0.1)
            elif name == "Falcon-180B":
                label.next_to(dot, DOWN, buff=0.1)
            elif name == "DBRX":
                label.next_to(dot, LEFT, buff=0.12)
            elif name == "Llama 3":
                label.next_to(dot, RIGHT, buff=0.1)
            else:
                label.next_to(dot, UP + RIGHT, buff=0.1)

            labels.add(label)

        return {'dots': dots, 'labels': labels}

    def _create_vertical_lines(self, axes, y_min, y_max):
        """创建垂直标注线"""
        # 紫色虚线: 2027.6 -> x=7.6
        purple_x = 7.6
        purple_line = DashedLine(
            axes.c2p(purple_x, y_min),
            axes.c2p(purple_x, y_max),
            stroke_color=COLORS['purple_line'],
            stroke_width=2,
            dash_length=0.15
        )

        # 粉色虚线: 2028.6 -> x=8.6
        pink_x = 8.6
        pink_line = DashedLine(
            axes.c2p(pink_x, y_min),
            axes.c2p(pink_x, y_max),
            stroke_color=COLORS['pink_line'],
            stroke_width=2,
            dash_length=0.15
        )

        return {'purple': purple_line, 'pink': pink_line}

    def _create_legend(self, axes, x_max, y_min):
        """创建图例，放置在坐标轴内部的右下角"""
        legend_items = VGroup()

        # 图例项（只保留两条实线）
        items_data = [
            (COLORS['stock_main'], "Stock of data", "solid"),
            (COLORS['projection_main'], "Dataset size projection", "solid"),
        ]

        for i, (color, text, style) in enumerate(items_data):
            item = VGroup()

            # 线条示例
            if style == "solid":
                line = Line(ORIGIN, RIGHT * 0.4, stroke_color=color, stroke_width=2.5)
            else:
                line = DashedLine(ORIGIN, RIGHT * 0.4, stroke_color=color,
                                  stroke_width=2, dash_length=0.08)

            # 标签 (使用 Tex 渲染)
            label = Tex(text, font_size=18, color=COLORS['text'])
            label.next_to(line, RIGHT, buff=0.15)

            item.add(line, label)
            item.shift(DOWN * i * 0.35)
            legend_items.add(item)

        # 对齐所有项
        legend_items.arrange(DOWN, aligned_edge=LEFT, buff=0.15)

        # 创建背景框
        legend_bg = RoundedRectangle(
            corner_radius=0.1,
            width=legend_items.width + 0.4,
            height=legend_items.height + 0.3,
            fill_color=COLORS['background'],
            fill_opacity=0.85,
            stroke_color=COLORS['grid'],
            stroke_width=1
        )
        legend_bg.move_to(legend_items.get_center())

        legend = VGroup(legend_bg, legend_items)

        # 将图例放置在坐标轴内部的右下角
        # 获取坐标轴右下角的位置（留一点边距）
        bottom_right = axes.c2p(x_max - 0.3, y_min + 0.3)
        # 移动图例使其右下角对齐到该位置
        legend.shift(bottom_right - legend.get_corner(DR))

        return legend


class DataWallStatic(Scene):
    """静态版本 - 直接显示完整图表"""

    def construct(self):
        # 设置背景
        self.camera.background_color = COLORS['background']

        # 复用 DataWallProjection 的所有元素创建方法
        main_scene = DataWallProjection()
        main_scene.camera = self.camera

        # 坐标系参数
        x_min, x_max = 0, 14
        y_min, y_max = 11, 15.5

        # 创建坐标轴
        axes = Axes(
            x_range=[x_min, x_max, 2],
            y_range=[y_min, y_max, 1],
            x_length=10,
            y_length=6,
            axis_config={
                "color": COLORS['axis_label'],
                "stroke_width": 1.5,
                "include_ticks": True,
                "tick_size": 0.1,
                "include_numbers": False,
            },
            tips=False,
        )
        axes.shift(DOWN * 0.3 + LEFT * 0.3)

        # 创建所有元素
        grid = main_scene._create_grid(axes, x_min, x_max, y_min, y_max)

        # X轴标签
        x_labels = VGroup()
        years = [2020, 2022, 2024, 2026, 2028, 2030, 2032, 2034]
        for i, year in enumerate(years):
            label = Tex(str(year), font_size=28, color=COLORS['axis_label'])
            label.next_to(axes.c2p(i * 2, y_min), DOWN, buff=0.15)
            x_labels.add(label)

        x_axis_label = Tex(r"Year", font_size=32, color=COLORS['text'])
        x_axis_label.next_to(axes, DOWN, buff=0.6)

        # Y轴标签
        y_labels = VGroup()
        for exp in [11, 12, 13, 14, 15]:
            label = MathTex(f"10^{{{exp}}}", font_size=28, color=COLORS['axis_label'])
            label.next_to(axes.c2p(x_min, exp), LEFT, buff=0.2)
            y_labels.add(label)

        y_axis_label = Tex(r"Effective data stock", font_size=28, color=COLORS['text'])
        y_axis_label.rotate(PI/2)
        y_axis_label.next_to(axes, LEFT, buff=0.9)

        # 数据带
        stock_band = main_scene._create_stock_band(axes)
        projection_band = main_scene._create_projection_band(axes)

        # 散点
        model_dots = main_scene._create_model_dots(axes)

        # 图例
        legend = main_scene._create_legend(axes, x_max, y_min)

        # 添加所有元素
        self.add(grid, axes, x_labels, y_labels, x_axis_label, y_axis_label)
        self.add(stock_band['fill'], stock_band['lower_line'],
                stock_band['upper_line'], stock_band['main_line'])
        self.add(projection_band['fill'], projection_band['lower_line'],
                projection_band['upper_line'], projection_band['main_line'])
        self.add(model_dots['dots'], model_dots['labels'])
        self.add(legend)

        self.wait(5)


# ===== 分段动画版本 =====

class DataWallAnimated(Scene):
    """带有更多动画效果的版本"""

    def construct(self):
        self.camera.background_color = COLORS['background']

        # 标题
        title = Tex(r"\textbf{The Data Wall: When Will We Run Out?}",
                   font_size=48, color=COLORS['text'])
        title.to_edge(UP, buff=0.3)

        # 坐标系
        x_min, x_max = 0, 14
        y_min, y_max = 11, 15.5

        axes = Axes(
            x_range=[x_min, x_max, 2],
            y_range=[y_min, y_max, 1],
            x_length=10,
            y_length=5.5,
            axis_config={
                "color": COLORS['axis_label'],
                "stroke_width": 1.5,
                "include_numbers": False,
            },
            tips=False,
        )
        axes.shift(DOWN * 0.5 + LEFT * 0.3)

        # 创建辅助对象
        main_scene = DataWallProjection()
        grid = main_scene._create_grid(axes, x_min, x_max, y_min, y_max)

        # 标签
        x_labels = VGroup()
        for i, year in enumerate([2020, 2022, 2024, 2026, 2028, 2030, 2032, 2034]):
            label = Tex(str(year), font_size=24, color=COLORS['axis_label'])
            label.next_to(axes.c2p(i * 2, y_min), DOWN, buff=0.12)
            x_labels.add(label)

        y_labels = VGroup()
        for exp in [11, 12, 13, 14, 15]:
            label = MathTex(f"10^{{{exp}}}", font_size=24, color=COLORS['axis_label'])
            label.next_to(axes.c2p(x_min, exp), LEFT, buff=0.15)
            y_labels.add(label)

        # 数据带
        stock_band = main_scene._create_stock_band(axes)
        projection_band = main_scene._create_projection_band(axes)
        model_dots = main_scene._create_model_dots(axes)
        legend = main_scene._create_legend(axes, x_max, y_min)
        legend.scale(0.9)

        # ===== 动画序列 =====

        # 1. 标题
        self.play(Write(title), run_time=1)
        self.wait(0.5)

        # 2. 坐标系
        self.play(
            FadeIn(grid),
            Create(axes),
            run_time=1
        )
        self.play(
            FadeIn(x_labels),
            FadeIn(y_labels),
            run_time=0.8
        )

        # 3. 数据存量带 + 解释文字
        stock_label = Tex("Human-generated text data",
                         font_size=28, color=COLORS['stock_main'])
        stock_label.next_to(axes.c2p(10, 14.8), UP, buff=0.1)

        self.play(
            FadeIn(stock_band['fill']),
            Create(stock_band['main_line']),
            Create(stock_band['lower_line']),
            Create(stock_band['upper_line']),
            run_time=1.5
        )
        self.play(Write(stock_label), run_time=0.5)
        self.wait(0.5)

        # 4. 预测带 + 解释文字
        proj_label = Tex("Training data requirements",
                        font_size=28, color=COLORS['projection_main'])
        proj_label.next_to(axes.c2p(2, 12.5), DOWN, buff=0.1)

        self.play(
            FadeIn(projection_band['fill']),
            Create(projection_band['main_line']),
            Create(projection_band['lower_line']),
            Create(projection_band['upper_line']),
            run_time=1.5
        )
        self.play(Write(proj_label), run_time=0.5)

        # 5. 模型散点
        self.play(
            *[FadeIn(dot, scale=0.3) for dot in model_dots['dots']],
            run_time=1
        )
        self.play(
            *[FadeIn(label) for label in model_dots['labels']],
            run_time=0.8
        )

        # 6. 移除临时标签
        self.play(
            FadeOut(stock_label),
            FadeOut(proj_label),
            run_time=0.5
        )

        # 7. 图例
        self.play(FadeIn(legend), run_time=0.8)

        # 8. 最终展示
        self.wait(3)

        # 9. 淡出
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=1
        )


if __name__ == "__main__":
    # 可以直接运行测试
    print("Run with: manim -pql data_wall_projection.py DataWallProjection")
    print("Or static: manim -pql data_wall_projection.py DataWallStatic")
    print("Or animated: manim -pql data_wall_projection.py DataWallAnimated")

