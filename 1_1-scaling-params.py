from manim import *
import numpy as np

class ScalingLawAnimation(Scene):
    def construct(self):
        # Data points (actual values, not log-transformed)
        data = [
            (3944.647122853531, 5.922871549947717),
            (37928.24118257773, 4.901966568753884),
            (66414.21935917267, 4.678250138321234),
            (232022.60744056228, 4.331218009821517),
            (406555.69276655855, 4.114285714285715),
            (555218.4245597814, 4.066518208432137),
            (829846.3134424438, 3.9726405226914543),
            (1086387.7214381418, 3.8718762655795484),
            (1738173.9629082645, 3.7385766618201397),
            (2325680.848426479, 3.6522696770762737),
            (3474867.3340370893, 3.576298247668914),
            (6956102.412622677, 3.3892514307540327),
            (7952347.289112029, 3.3655864627250347),
            (14236692.045908362, 3.2119874980661014),
            (18625369.407101993, 3.1451744467193583),
            (29809793.965647276, 3.0298087381103307),
            (58308821.75540442, 2.891534030138178),
            (65265747.23819919, 2.8512955484841798),
            (116724495.26834969, 2.7403016107808327),
            (238893937.26206523, 2.5969789183802834),
            (558956000.0227363, 2.44396761298644),
            (1193776641.7144358, 2.3433503880032265),
        ]
        
        self.camera.background_color = BLACK
        
        # Axis ranges
        x_min_exp, x_max_exp = 3.5, 9.3
        y_min, y_max = 2.2, 6.1
        y_min_exp, y_max_exp = np.log(y_min), np.log(y_max)
        
        # Y-axis tick values
        y_tick_values = [2.4, 3.2, 4.0, 4.8, 5.6]
        # X-axis tick values (as exponents) - removed 10^3
        x_tick_exps = [5, 7, 9]
        
        # Square axes with log scaling (4:3 aspect ratio)
        axes = Axes(
            x_range=[x_min_exp, x_max_exp, 2],
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
        x_title = MathTex(r"\text{Parameters}", font_size=36)
        x_subtitle = MathTex(r"\text{non-embedding}", font_size=30, color=GRAY)
        
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