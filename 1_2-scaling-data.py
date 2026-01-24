from manim import *
import numpy as np

class ScalingLawAnimation(Scene):
    def construct(self):
        # Data points
        data = [
            (21593764.377193023, 4.139454029388758),
            (42937407.70672256, 3.8312429660663856),
            (85966324.37803191, 3.5617837916355635),
            (172115861.71076524, 3.3349196678054143),
            (344598539.79763067, 3.1532027933826985),
            (680512051.7631154, 2.918424975119776),
            (1371871496.557008, 2.749603527943465),
        ]

        self.camera.background_color = BLACK

        # Axis ranges
        x_min_exp, x_max_exp = 7.2, 9.3
        y_min, y_max = 2.65, 4.25
        y_min_exp, y_max_exp = np.log(y_min), np.log(y_max)

        # Y-axis tick values
        y_tick_values = [2.7, 3.0, 3.3, 3.6, 3.9, 4.2]
        # X-axis tick values (as exponents)
        x_tick_exps = [8, 9]

        # Axes with log scaling (4:3 aspect ratio)
        axes = Axes(
            x_range=[x_min_exp, x_max_exp, 1],
            y_range=[y_min_exp, y_max_exp, (y_max_exp - y_min_exp) / 5],
            x_length=8,
            y_length=6,
            axis_config={
                "color": WHITE,
                "stroke_width": 2,
                "include_ticks": False,
            },
            x_axis_config={"scaling": LogBase(base=10)},
            y_axis_config={"scaling": LogBase(base=np.e)},
            tips=False,
        )
        axes.shift(UP * 0.7)

        # Create enclosing square as a single path (clockwise from bottom-left)
        square_path = VMobject(color=WHITE, stroke_width=2)
        square_path.set_points_as_corners([
            axes.c2p(10**x_min_exp, y_min),  # bottom-left
            axes.c2p(10**x_min_exp, y_max),  # top-left
            axes.c2p(10**x_max_exp, y_max),  # top-right
            axes.c2p(10**x_max_exp, y_min),  # bottom-right
            axes.c2p(10**x_min_exp, y_min),  # back to bottom-left
        ])

        # X-axis tick marks
        x_ticks = VGroup()
        for exp in x_tick_exps:
            tick = Line(
                axes.c2p(10**exp, y_min),
                axes.c2p(10**exp, y_min) + DOWN * 0.1,
                color=WHITE,
                stroke_width=2
            )
            x_ticks.add(tick)

        # Y-axis tick marks
        y_ticks = VGroup()
        for val in y_tick_values:
            tick = Line(
                axes.c2p(10**x_min_exp, val),
                axes.c2p(10**x_min_exp, val) + LEFT * 0.1,
                color=WHITE,
                stroke_width=2
            )
            y_ticks.add(tick)

        # X-axis labels
        x_labels = VGroup()
        for exp in x_tick_exps:
            label = MathTex(f"10^{{{exp}}}", font_size=30)
            label.next_to(axes.c2p(10**exp, y_min), DOWN, buff=0.25)
            x_labels.add(label)

        # Y-axis labels
        y_labels = VGroup()
        for val in y_tick_values:
            label = MathTex(f"{val:.1f}", font_size=30)
            label.next_to(axes.c2p(10**x_min_exp, val), LEFT, buff=0.25)
            y_labels.add(label)

        # Y-axis title
        y_title = MathTex(r"\text{Test Loss}", font_size=36)
        y_title.rotate(90 * DEGREES)
        y_title.next_to(y_labels, LEFT, buff=0.5)

        # X-axis titles (centered on the plot)
        x_title = MathTex(r"\text{Dataset Size}", font_size=36)
        x_subtitle = MathTex(r"\text{tokens}", font_size=30, color=GRAY)

        # Get center of x-axis for proper centering
        x_center = (axes.c2p(10**x_min_exp, y_min)[0] + axes.c2p(10**x_max_exp, y_min)[0]) / 2
        x_title.move_to([x_center, x_labels.get_bottom()[1] - 0.5, 0])
        x_subtitle.next_to(x_title, DOWN, buff=0.1)

        # Create dots
        dots = VGroup()
        dot_positions = []
        for x_val, y_val in data:
            pos = axes.c2p(x_val, y_val)
            dot_positions.append(pos)
            dot = Dot(pos, color=BLUE, radius=0.08)
            dots.add(dot)

        # Create connecting line through dots
        connecting_line = VMobject(color=BLUE, stroke_width=2)
        connecting_line.set_points_smoothly(dot_positions)

        # Animation sequence
        self.play(Create(square_path), run_time=2)
        self.play(
            FadeIn(x_labels),
            FadeIn(y_labels),
            FadeIn(x_ticks),
            FadeIn(y_ticks),
            run_time=1
        )
        self.play(
            Write(x_title),
            Write(x_subtitle),
            Write(y_title),
            run_time=1
        )
        self.wait(0.5)

        # Animate dots and line together
        self.play(
            Create(connecting_line),
            LaggedStart(
                *[GrowFromCenter(dot) for dot in dots],
                lag_ratio=0.15
            ),
            run_time=3
        )

        self.wait(2)