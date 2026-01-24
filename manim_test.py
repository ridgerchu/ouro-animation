"""
Manim 测试动画 - 展示基本功能
运行命令: manim -pql manim_test.py BasicShapes
         manim -pql manim_test.py EquationScene
         manim -pql manim_test.py GraphScene
"""

from manim import *


class BasicShapes(Scene):
    """基础图形动画"""
    def construct(self):
        # 创建标题
        title = Text("Manim 基础测试", font_size=48)
        title.to_edge(UP)

        # 创建几何图形
        circle = Circle(color=BLUE, fill_opacity=0.5)
        square = Square(color=RED, fill_opacity=0.5)
        triangle = Triangle(color=GREEN, fill_opacity=0.5)

        # 排列图形
        shapes = VGroup(circle, square, triangle)
        shapes.arrange(RIGHT, buff=1)

        # 动画序列
        self.play(Write(title))
        self.wait(0.5)

        self.play(
            Create(circle),
            Create(square),
            Create(triangle),
            run_time=2
        )
        self.wait(0.5)

        # 旋转和缩放
        self.play(
            Rotate(circle, PI),
            square.animate.scale(1.5),
            triangle.animate.shift(UP * 0.5),
            run_time=2
        )
        self.wait(0.5)

        # 变换颜色
        self.play(
            circle.animate.set_color(YELLOW),
            square.animate.set_color(PURPLE),
            triangle.animate.set_color(ORANGE),
            run_time=1.5
        )
        self.wait(1)

        # 淡出
        self.play(
            FadeOut(title),
            FadeOut(shapes),
            run_time=1
        )


class EquationScene(Scene):
    """数学公式动画"""
    def construct(self):
        # 标题
        title = Text("数学公式演示", font_size=40)
        title.to_edge(UP)

        # 创建数学公式
        equation1 = MathTex(r"E = mc^2")
        equation1.scale(1.5)

        equation2 = MathTex(r"\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}")
        equation2.scale(1.2)

        equation3 = MathTex(
            r"\nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t}"
        )
        equation3.scale(1.2)

        # 动画
        self.play(Write(title))
        self.wait(0.5)

        self.play(Write(equation1))
        self.wait(1)

        self.play(Transform(equation1, equation2))
        self.wait(1)

        self.play(Transform(equation1, equation3))
        self.wait(1)

        self.play(
            FadeOut(title),
            FadeOut(equation1),
            run_time=1
        )


class GraphScene(Scene):
    """图表和函数动画"""
    def construct(self):
        # 创建坐标轴
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1],
            x_length=6,
            y_length=6,
            axis_config={"color": BLUE},
        )

        # 添加标签
        labels = axes.get_axis_labels(x_label="x", y_label="f(x)")

        # 创建函数图像
        sine_graph = axes.plot(lambda x: np.sin(x), color=GREEN)
        cosine_graph = axes.plot(lambda x: np.cos(x), color=RED)

        # 添加标题
        title = Text("函数图像", font_size=40)
        title.to_edge(UP)

        # 动画序列
        self.play(Write(title))
        self.play(Create(axes), Write(labels))
        self.wait(0.5)

        # 绘制 sin 函数
        sine_label = MathTex(r"y = \sin(x)", color=GREEN).next_to(axes, RIGHT)
        self.play(Create(sine_graph), Write(sine_label))
        self.wait(1)

        # 切换到 cos 函数
        cosine_label = MathTex(r"y = \cos(x)", color=RED).next_to(axes, RIGHT)
        self.play(
            Transform(sine_graph, cosine_graph),
            Transform(sine_label, cosine_label)
        )
        self.wait(1)

        # 淡出
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=1
        )


class DataVisualization(Scene):
    """数据可视化 - 柱状图"""
    def construct(self):
        # 标题
        title = Text("数据可视化示例", font_size=40)
        title.to_edge(UP)

        # 创建数据
        data = [3, 5, 7, 4, 6]
        colors = [BLUE, RED, GREEN, YELLOW, PURPLE]

        # 创建柱状图
        bars = VGroup()
        labels = VGroup()

        for i, (value, color) in enumerate(zip(data, colors)):
            bar = Rectangle(
                height=value * 0.5,
                width=0.8,
                color=color,
                fill_opacity=0.7
            )
            bar.shift(RIGHT * (i - 2) * 1.2 + DOWN * (3 - value * 0.25))

            label = Text(str(value), font_size=24)
            label.next_to(bar, UP)

            bars.add(bar)
            labels.add(label)

        # 动画
        self.play(Write(title))
        self.wait(0.5)

        # 逐个显示柱子
        for bar, label in zip(bars, labels):
            self.play(
                GrowFromEdge(bar, DOWN),
                FadeIn(label),
                run_time=0.5
            )

        self.wait(1)

        # 数值变化动画
        for i in range(len(bars)):
            new_value = np.random.randint(2, 8)
            new_height = new_value * 0.5
            new_bar = Rectangle(
                height=new_height,
                width=0.8,
                color=colors[i],
                fill_opacity=0.7
            )
            new_bar.shift(RIGHT * (i - 2) * 1.2 + DOWN * (3 - new_height * 0.5))

            new_label = Text(str(new_value), font_size=24)
            new_label.next_to(new_bar, UP)

            self.play(
                Transform(bars[i], new_bar),
                Transform(labels[i], new_label),
                run_time=0.5
            )

        self.wait(1)
        self.play(*[FadeOut(mob) for mob in self.mobjects])


if __name__ == "__main__":
    # 使用说明
    print("=" * 50)
    print("Manim 测试脚本")
    print("=" * 50)
    print("\n运行示例:")
    print("  低质量预览: manim -pql manim_test.py BasicShapes")
    print("  高质量渲染: manim -pqh manim_test.py BasicShapes")
    print("\n可用场景:")
    print("  1. BasicShapes - 基础图形动画")
    print("  2. EquationScene - 数学公式动画")
    print("  3. GraphScene - 函数图像动画")
    print("  4. DataVisualization - 数据可视化")
    print("=" * 50)

