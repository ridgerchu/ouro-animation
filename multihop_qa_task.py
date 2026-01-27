"""
Multi-hop QA Task Visualization
展示多跳问答任务的架构和逻辑流程

运行命令:
  完整动画: manim -pql multihop_qa_task.py MultiHopQATask
  高质量:   manim -pqh multihop_qa_task.py MultiHopQATask
  1080p60:  manim -pqh --fps 60 multihop_qa_task.py MultiHopQATask
"""

from manim import *
import numpy as np

# ==================== 颜色配置 ====================
BACKGROUND_COLOR = BLACK          # 纯黑色背景
PRIMARY_COLOR = "#4361EE"         # 主色 - 蓝色
SECONDARY_COLOR = "#2A9D8F"       # 次色 - 青色
ACCENT_COLOR = "#E63946"          # 强调色 - 红色
GOLD_COLOR = "#F4A261"            # 金色
LAYER_COLOR = "#3D5A80"           # 层颜色
NODE_COLOR = "#48CAE4"            # 节点颜色
PROFILE_COLOR = "#7B2CBF"         # Profile 框颜色
ARROW_COLOR = "#90BE6D"           # 箭头颜色
TEXT_COLOR = WHITE                # 文字颜色
DIM_COLOR = GREY_B                # 弱化颜色


class LayerRectangle(VGroup):
    """带有节点的层矩形"""
    def __init__(self, width=5.5, height=0.9, color=LAYER_COLOR, num_nodes=4,
                 node_labels=None, label_font_size=18, **kwargs):
        super().__init__(**kwargs)

        # 创建圆角矩形
        self.rect = RoundedRectangle(
            corner_radius=0.15,
            width=width,
            height=height,
            color=color,
            stroke_width=2.5,
            fill_color=color,
            fill_opacity=0.15
        )
        self.add(self.rect)

        # 创建节点
        self.nodes = VGroup()
        node_spacing = (width - 1.0) / (num_nodes - 1) if num_nodes > 1 else 0
        start_x = -width / 2 + 0.5

        for i in range(num_nodes):
            node = Square(
                side_length=0.35,
                color=NODE_COLOR,
                fill_color=NODE_COLOR,
                fill_opacity=0.3,
                stroke_width=2
            )
            node.move_to(self.rect.get_center() + RIGHT * (start_x + i * node_spacing))
            self.nodes.add(node)

        self.add(self.nodes)

        # 添加节点标签
        self.node_labels = VGroup()
        if node_labels:
            for i, label_text in enumerate(node_labels):
                if i < len(self.nodes):
                    label = MathTex(label_text, font_size=label_font_size, color=TEXT_COLOR)
                    label.next_to(self.nodes[i], DOWN, buff=0.08)
                    self.node_labels.add(label)
            self.add(self.node_labels)

    def get_node(self, index):
        """获取指定索引的节点"""
        return self.nodes[index]

    def get_node_center(self, index):
        """获取指定节点的中心位置"""
        return self.nodes[index].get_center()


class ProfileBox(VGroup):
    """Profile 信息框"""
    def __init__(self, title, content_lines, color=PROFILE_COLOR, width=2.8, **kwargs):
        super().__init__(**kwargs)

        # 主框
        self.box = RoundedRectangle(
            corner_radius=0.12,
            width=width,
            height=0.35 * (len(content_lines) + 1) + 0.3,
            color=color,
            stroke_width=2,
            fill_color=BACKGROUND_COLOR,
            fill_opacity=0.95
        )

        # 标题
        self.title = Tex(r"\textbf{" + title + "}", font_size=16, color=color)
        self.title.next_to(self.box.get_top(), DOWN, buff=0.15)

        # 内容
        self.content = VGroup()
        for i, line in enumerate(content_lines):
            text = Tex(r"\text{" + line + "}", font_size=13, color=TEXT_COLOR)
            text.next_to(self.title, DOWN, buff=0.15 + i * 0.3)
            text.align_to(self.title, LEFT)
            self.content.add(text)

        self.add(self.box, self.title, self.content)


class MultiHopQATask(Scene):
    """Multi-hop QA Task 可视化动画"""

    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR

        # 布局参数
        self.left_center = LEFT * 2.8  # 左侧图表中心
        self.right_center = RIGHT * 4.0  # 右侧文字中心

        # 运行动画序列
        self.animate_sequence()

    def animate_sequence(self):
        """主动画序列"""

        # ==================== 1. 创建三层架构 ====================
        # 定义节点标签
        layer1_labels = [r"E_1^{(1)}", r"E_2^{(1)}", r"\cdots", r"E_n^{(1)}"]
        layer2_labels = [r"E_{n+1}^{(2)}", r"E_{n+2}^{(2)}", r"\cdots", r"E_{2n}^{(2)}"]
        layer3_labels = [r"E_{2n+1}^{(3)}", r"E_{2n+2}^{(3)}", r"\cdots", r"E_{3n}^{(3)}"]

        # 创建三层
        layer1 = LayerRectangle(
            width=5.0, height=0.8, color="#3D5A80",
            num_nodes=4, node_labels=layer1_labels, label_font_size=16
        )
        layer2 = LayerRectangle(
            width=5.0, height=0.8, color="#457B9D",
            num_nodes=4, node_labels=layer2_labels, label_font_size=16
        )
        layer3 = LayerRectangle(
            width=5.0, height=0.8, color="#1D3557",
            num_nodes=4, node_labels=layer3_labels, label_font_size=16
        )

        # 定位层 (垂直堆叠)
        layer1.move_to(self.left_center + DOWN * 1.8)
        layer2.move_to(self.left_center + UP * 0.0)
        layer3.move_to(self.left_center + UP * 1.8)

        layers = VGroup(layer1, layer2, layer3)

        # 动画：创建层
        self.play(
            FadeIn(layer1.rect, scale=0.9),
            run_time=0.6
        )
        self.play(
            FadeIn(layer2.rect, scale=0.9),
            run_time=0.6
        )
        self.play(
            FadeIn(layer3.rect, scale=0.9),
            run_time=0.6
        )

        # ==================== 3. 显示节点 ====================
        self.play(
            LaggedStart(
                *[FadeIn(node, scale=0.5) for node in layer1.nodes],
                lag_ratio=0.1
            ),
            run_time=0.8
        )
        self.play(
            LaggedStart(
                *[FadeIn(node, scale=0.5) for node in layer2.nodes],
                lag_ratio=0.1
            ),
            run_time=0.8
        )
        self.play(
            LaggedStart(
                *[FadeIn(node, scale=0.5) for node in layer3.nodes],
                lag_ratio=0.1
            ),
            run_time=0.8
        )

        # 显示节点标签
        self.play(
            FadeIn(layer1.node_labels),
            FadeIn(layer2.node_labels),
            FadeIn(layer3.node_labels),
            run_time=0.8
        )

        # ==================== 4. 创建层间连接箭头 ====================
        arrows_1_to_2 = VGroup()
        arrows_2_to_3 = VGroup()

        # Layer 1 到 Layer 2 的连接
        for i in range(4):
            for j in range(4):
                if (i == j) or (abs(i - j) == 1):  # 只连接相邻和对角节点
                    start = layer1.get_node_center(i) + UP * 0.2
                    end = layer2.get_node_center(j) + DOWN * 0.35
                    arrow = Arrow(
                        start, end,
                        color=ARROW_COLOR,
                        stroke_width=1.5,
                        buff=0.05,
                        max_tip_length_to_length_ratio=0.15,
                        tip_length=0.1
                    )
                    arrow.set_opacity(0.6)
                    arrows_1_to_2.add(arrow)

        # Layer 2 到 Layer 3 的连接
        for i in range(4):
            for j in range(4):
                if (i == j) or (abs(i - j) == 1):
                    start = layer2.get_node_center(i) + UP * 0.2
                    end = layer3.get_node_center(j) + DOWN * 0.35
                    arrow = Arrow(
                        start, end,
                        color=ARROW_COLOR,
                        stroke_width=1.5,
                        buff=0.05,
                        max_tip_length_to_length_ratio=0.15,
                        tip_length=0.1
                    )
                    arrow.set_opacity(0.6)
                    arrows_2_to_3.add(arrow)

        self.play(
            LaggedStart(*[Create(arr) for arr in arrows_1_to_2], lag_ratio=0.02),
            run_time=1.2
        )
        self.play(
            LaggedStart(*[Create(arr) for arr in arrows_2_to_3], lag_ratio=0.02),
            run_time=1.2
        )

        self.wait(0.5)

        # ==================== 5. 右侧文字区域 ====================
        # Example 标题
        example_header = Tex(r"\textbf{Example:}", font_size=26, color=GOLD_COLOR)
        example_header.move_to(self.right_center + UP * 2.5)
        example_header.align_to(self.right_center + LEFT * 1.8, LEFT)

        self.play(Write(example_header), run_time=0.6)

        # 问题文本
        question = Tex(
            r"\textit{``Who is the teacher of the instructor of Jennifer?''}",
            font_size=20,
            color=TEXT_COLOR
        )
        question.next_to(example_header, DOWN, buff=0.4)
        question.align_to(example_header, LEFT)

        self.play(Write(question), run_time=1)

        # Bullet points
        bullet1 = Tex(r"$\bullet$ Relation: \texttt{teacher}, \texttt{instructor}", font_size=18, color=DIM_COLOR)
        bullet2 = Tex(r"$\bullet$ Entity: \texttt{Jennifer}, \texttt{Robert}", font_size=18, color=DIM_COLOR)

        bullet1.next_to(question, DOWN, buff=0.4)
        bullet1.align_to(example_header, LEFT)
        bullet2.next_to(bullet1, DOWN, buff=0.2)
        bullet2.align_to(bullet1, LEFT)

        self.play(
            FadeIn(bullet1, shift=RIGHT * 0.2),
            run_time=0.5
        )
        self.play(
            FadeIn(bullet2, shift=RIGHT * 0.2),
            run_time=0.5
        )

        # ==================== 6. 高亮 Jennifer 节点并显示 Profile ====================
        # Jennifer 是 E_n^{(1)} (layer1 的最后一个节点, index 3)
        jennifer_node = layer1.get_node(3)

        # 高亮效果
        highlight_jennifer = Circle(
            radius=0.3,
            color=ACCENT_COLOR,
            stroke_width=3
        )
        highlight_jennifer.move_to(jennifer_node.get_center())

        self.play(
            Create(highlight_jennifer),
            jennifer_node.animate.set_fill(ACCENT_COLOR, opacity=0.5),
            run_time=0.6
        )

        # Jennifer 的 Profile 框
        jennifer_profile = ProfileBox(
            "Profile: Jennifer",
            ["instructor: Robert", "teacher: Williams", "ruler: John", "..."],
            color=ACCENT_COLOR,
            width=2.2
        )
        jennifer_profile.next_to(jennifer_node, DOWN + RIGHT, buff=0.4)
        jennifer_profile.shift(UP * 0.5 + RIGHT * 0.3)

        # 虚线连接
        dashed_line_jennifer = DashedLine(
            jennifer_node.get_center(),
            jennifer_profile.get_left() + UP * 0.3,
            color=ACCENT_COLOR,
            stroke_width=2,
            dash_length=0.1
        )

        self.play(
            Create(dashed_line_jennifer),
            FadeIn(jennifer_profile, shift=UP * 0.2),
            run_time=0.8
        )

        self.wait(0.5)

        # ==================== 7. 显示 "instructor" 关系箭头 ====================
        # Robert 是 E_{2n}^{(2)} (layer2 的最后一个节点, index 3)
        robert_node = layer2.get_node(3)

        # 高亮的逻辑箭头 (从 Jennifer 到 Robert)
        logic_arrow = CurvedArrow(
            jennifer_node.get_center() + UP * 0.2,
            robert_node.get_center() + DOWN * 0.2,
            color=GOLD_COLOR,
            stroke_width=4,
            angle=-TAU / 6
        )

        # "instructor" 标签
        instructor_label = Tex(r"\texttt{instructor}", font_size=16, color=GOLD_COLOR)
        instructor_label.next_to(logic_arrow.point_from_proportion(0.5), LEFT, buff=0.1)

        self.play(
            Create(logic_arrow),
            FadeIn(instructor_label),
            run_time=1
        )

        # Glow 效果
        glow_arrow = logic_arrow.copy()
        glow_arrow.set_stroke(width=10, opacity=0.4)

        self.play(
            glow_arrow.animate.set_stroke(width=20, opacity=0),
            run_time=0.6
        )
        self.remove(glow_arrow)

        # ==================== 8. 高亮 Robert 节点并显示 Profile ====================
        highlight_robert = Circle(
            radius=0.3,
            color=PRIMARY_COLOR,
            stroke_width=3
        )
        highlight_robert.move_to(robert_node.get_center())

        self.play(
            Create(highlight_robert),
            robert_node.animate.set_fill(PRIMARY_COLOR, opacity=0.5),
            run_time=0.6
        )

        # Robert 的 Profile 框
        robert_profile = ProfileBox(
            "Profile: Robert",
            ["instructor: Frank", "teacher: Alice", "ruler: ...", "..."],
            color=PRIMARY_COLOR,
            width=2.2
        )
        robert_profile.next_to(robert_node, UP + LEFT, buff=0.4)
        robert_profile.shift(UP * 0.2 + LEFT * 0.2)

        # 虚线连接
        dashed_line_robert = DashedLine(
            robert_node.get_center(),
            robert_profile.get_right() + DOWN * 0.3,
            color=PRIMARY_COLOR,
            stroke_width=2,
            dash_length=0.1
        )

        self.play(
            Create(dashed_line_robert),
            FadeIn(robert_profile, shift=DOWN * 0.2),
            run_time=0.8
        )

        # 高亮 "teacher: Alice" 表示答案
        answer_highlight = SurroundingRectangle(
            robert_profile.content[1],
            color=GOLD_COLOR,
            buff=0.05,
            stroke_width=2
        )

        self.play(Create(answer_highlight), run_time=0.5)

        self.wait(0.8)

        # ==================== 9. 最终展示 ====================
        self.wait(2)

        # 最终等待
        self.wait(2)

        # 淡出所有元素
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=1.5
        )


class MultiHopQATaskCompact(Scene):
    """紧凑版 Multi-hop QA Task (适合嵌入演示)"""

    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR

        # 标题
        title = Tex(r"\textbf{Multi-hop QA Task}", font_size=36, color=TEXT_COLOR)
        title.to_edge(UP, buff=0.4)

        # 简化的三层结构
        layer1 = RoundedRectangle(width=6, height=0.6, corner_radius=0.1,
                                   color="#3D5A80", fill_opacity=0.2)
        layer2 = RoundedRectangle(width=6, height=0.6, corner_radius=0.1,
                                   color="#457B9D", fill_opacity=0.2)
        layer3 = RoundedRectangle(width=6, height=0.6, corner_radius=0.1,
                                   color="#1D3557", fill_opacity=0.2)

        layer1.move_to(DOWN * 1.5)
        layer2.move_to(ORIGIN)
        layer3.move_to(UP * 1.5)

        layers = VGroup(layer1, layer2, layer3)
        layers.shift(LEFT * 2.5)

        # 层标签
        label1 = MathTex(r"E_1^{(1)}, E_2^{(1)}, \ldots, E_n^{(1)}", font_size=20)
        label2 = MathTex(r"E_{n+1}^{(2)}, E_{n+2}^{(2)}, \ldots, E_{2n}^{(2)}", font_size=20)
        label3 = MathTex(r"E_{2n+1}^{(3)}, \ldots, E_{3n}^{(3)}", font_size=20)

        label1.move_to(layer1)
        label2.move_to(layer2)
        label3.move_to(layer3)

        # 右侧问题
        question = Tex(
            r"\textit{``Who is the teacher of}",
            font_size=18,
            color=TEXT_COLOR
        )
        question2 = Tex(
            r"\textit{the instructor of Jennifer?''}",
            font_size=18,
            color=TEXT_COLOR
        )
        question.move_to(RIGHT * 3.5 + UP * 1)
        question2.next_to(question, DOWN, buff=0.15)

        # 答案
        answer = Tex(r"\textbf{Answer: Alice}", font_size=22, color=GOLD_COLOR)
        answer.move_to(RIGHT * 3.5 + DOWN * 0.5)

        # 动画
        self.play(Write(title), run_time=0.8)
        self.play(
            LaggedStart(
                FadeIn(layer1), FadeIn(layer2), FadeIn(layer3),
                lag_ratio=0.2
            ),
            run_time=1
        )
        self.play(
            Write(label1), Write(label2), Write(label3),
            run_time=1
        )

        # 箭头
        arr1 = Arrow(layer1.get_top(), layer2.get_bottom(), buff=0.1,
                     color=ARROW_COLOR, stroke_width=2)
        arr2 = Arrow(layer2.get_top(), layer3.get_bottom(), buff=0.1,
                     color=ARROW_COLOR, stroke_width=2)

        self.play(Create(arr1), Create(arr2), run_time=0.8)

        self.play(Write(question), Write(question2), run_time=1)
        self.play(FadeIn(answer, scale=1.2), run_time=0.8)

        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1)


if __name__ == "__main__":
    print("=" * 60)
    print("Multi-hop QA Task Visualization - Manim")
    print("=" * 60)
    print("\n运行命令:")
    print("  完整版: manim -pql multihop_qa_task.py MultiHopQATask")
    print("  紧凑版: manim -pql multihop_qa_task.py MultiHopQATaskCompact")
    print("  高质量: manim -pqh multihop_qa_task.py MultiHopQATask")
    print("  1080p60: manim -pqh --fps 60 multihop_qa_task.py MultiHopQATask")
    print("=" * 60)

