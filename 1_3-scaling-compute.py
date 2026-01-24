from manim import *
import numpy as np

def generate_scaling_line(line_idx, num_points=40):
    """
    Generates (compute, loss) tuples for scaling laws.
    - Lines 1-3: Shifted DOWN by 0.5 (below Pareto).
    - Lines >18: Smooth glide down (no bend at start).
    - Variable spacing and noise profiles.
    
    Args:
        line_idx (int): 1 to 35
        num_points (int): Number of points to generate
    
    Returns:
        list of tuples: [(compute, loss), ...]
    """
    
    # --- 1. Global Parameters ---
    def frontier_loss(c):
        return (c / (2.3 * 10**8))**(-0.050)
    # --- 2. Parameter Interpolation (With Jitter) ---
    t = (line_idx - 1) / 34.0 
    
    # Spacing jitter for non-uniform gaps
    spacing_jitter = np.sin(line_idx * 12.5) * 0.04 
    t_varied = np.clip(t + spacing_jitter, 0, 1)
    
    # Saturation Point (C_sat)
    log_sat = -7.5 + (t_varied**1.1) * (2.5 - (-7.5))
    if line_idx > 10 and line_idx < 30:
        log_sat -= 0.5 # Early saturation for mid-range
    C_sat = 10**log_sat
    
    # Start Point (C_start)
    log_start = -9.0 + t_varied * (-2.5 - (-9.0))
    start_jitter = np.cos(line_idx * 23.1) * 0.15
    C_start = 10**(log_start + start_jitter)
    
    # --- 3. Regime Configuration ---
    
    global_frontier_shift = -0.05 
    bend_sharpness = 10
    noise_level = 0.02
    vertical_bias = 0.0 # Moves curves straight down
    
    if line_idx <= 3:
        # REGIME: Hyper-Small (Moved Down)
        vertical_bias = -0.5 # The requested drop
        frontier_bias = global_frontier_shift - 0.05
        drop_steepness = 0.60
        noise_level = 0.035
        C_sat *= 0.5 
        
    elif line_idx <= 10:
        # REGIME: Small
        frontier_bias = global_frontier_shift - 0.02
        drop_steepness = 0.45
        
    elif line_idx <= 18:
        # REGIME: Medium
        frontier_bias = global_frontier_shift
        drop_steepness = 0.40
        bend_sharpness = 12 
        noise_level = 0.025
        
    else:
        # REGIME: Large/Giant (Smooth Glide)
        frontier_bias = global_frontier_shift
        drop_steepness = 0.28 # Shallow slope = smooth glide (no bend)
        bend_sharpness = 15
        noise_level = 0.015
    
    # --- 4. Generate Trajectory ---
    
    log_end_viz = min(1.0, np.log10(C_sat) + 0.8) 
    if log_end_viz <= np.log10(C_start): log_end_viz = np.log10(C_start) + 0.5
    if log_end_viz > 1.0: log_end_viz = 1.0
        
    c_values = np.logspace(np.log10(C_start), log_end_viz, num_points)
    data_points = []
    
    # Seed per line for consistent noise
    np.random.seed(line_idx * 100)
    current_brownian = 0.0
    
    for c in c_values:
        # A. Ideal Components
        val_frontier = frontier_loss(c) + frontier_bias
        val_floor = frontier_loss(C_sat) + frontier_bias
        
        # B. Drop Logic (Simple Power Law for smoothness)
        # 7.0 is the initialization loss roughly
        val_drop = 7.0 * (c / C_start)**(-drop_steepness)
            
        # C. Synthesis
        # Smooth Max to create the knee at saturation
        val_curve = (val_frontier**bend_sharpness + val_floor**bend_sharpness)**(1/bend_sharpness)
        
        # Smooth Max to blend initialization glide into the curve
        val_ideal = (val_curve**6 + val_drop**6)**(1/6)
        
        # D. Noise
        ratio = c / C_sat
        damping = 1.0 / (1.0 + 5.0 * ratio**4) 
        
        current_brownian += np.random.normal(0, noise_level * 0.5)
        white = np.random.normal(0, noise_level)
        total_noise = (white + current_brownian) * damping
        
        # Final Sum with Vertical Bias
        final_loss = val_ideal + total_noise + vertical_bias
        
        final_loss = max(2.0, min(7.5, final_loss))
        
        data_points.append((c, final_loss))
        
    return data_points

class ComputeScalingAnimation(Scene):
    def construct(self):
        self.camera.background_color = BLACK
        
        # Generate data using scaling line function
        raw_data = {}
        for line_id in range(1, 36):
            raw_data[line_id] = generate_scaling_line(line_id)
        
        # Interpolate each curve for smoother rendering
        from scipy import interpolate
        
        curves_data = []
        for line_id in sorted(raw_data.keys()):
            points = raw_data[line_id]
            x_vals = np.array([p[0] for p in points])
            y_vals = np.array([p[1] for p in points])
            
            sort_idx = np.argsort(x_vals)
            x_vals = x_vals[sort_idx]
            y_vals = y_vals[sort_idx]
            
            log_x = np.log10(x_vals)
            
            if len(x_vals) > 3:
                try:
                    f = interpolate.interp1d(log_x, y_vals, kind='cubic', fill_value='extrapolate')
                    log_x_smooth = np.linspace(log_x.min(), log_x.max(), 50)
                    y_smooth = f(log_x_smooth)
                    x_smooth = 10 ** log_x_smooth
                    curves_data.append(list(zip(x_smooth, y_smooth)))
                except:
                    curves_data.append(points)
            else:
                curves_data.append(points)
        
        # Axis ranges
        x_min_exp, x_max_exp = -9, 1
        y_min, y_max = 2, 7
        y_min_exp, y_max_exp = np.log(y_min), np.log(y_max)
        
        y_tick_values = [2, 3, 4, 5, 6, 7]
        x_tick_exps = [-9, -7, -5, -3, -1, 1]
        
        axes = Axes(
            x_range=[x_min_exp, x_max_exp, 2],
            y_range=[y_min_exp, y_max_exp, (y_max_exp - y_min_exp) / 5],
            x_length=8,
            y_length=6,
            axis_config={"color": WHITE, "stroke_width": 2, "include_ticks": False},
            x_axis_config={"scaling": LogBase(base=10)},
            y_axis_config={"scaling": LogBase(base=np.e)},
            tips=False,
        )
        axes.shift(UP * 0.7)
        
        square_path = VMobject(color=WHITE, stroke_width=2)
        square_path.set_points_as_corners([
            axes.c2p(10**x_min_exp, y_min),
            axes.c2p(10**x_min_exp, y_max),
            axes.c2p(10**x_max_exp, y_max),
            axes.c2p(10**x_max_exp, y_min),
            axes.c2p(10**x_min_exp, y_min),
        ])
        
        x_ticks = VGroup(*[Line(axes.c2p(10**exp, y_min), axes.c2p(10**exp, y_min) + DOWN * 0.1, color=WHITE, stroke_width=2) for exp in x_tick_exps])
        y_ticks = VGroup(*[Line(axes.c2p(10**x_min_exp, val), axes.c2p(10**x_min_exp, val) + LEFT * 0.1, color=WHITE, stroke_width=2) for val in y_tick_values])
        
        x_labels = VGroup(*[MathTex(f"10^{{{exp}}}", font_size=30).next_to(axes.c2p(10**exp, y_min), DOWN, buff=0.25) for exp in x_tick_exps])
        y_labels = VGroup(*[MathTex(f"{val}", font_size=30).next_to(axes.c2p(10**x_min_exp, val), LEFT, buff=0.25) for val in y_tick_values])
        
        y_title = MathTex(r"\text{Test Loss}", font_size=36).rotate(90 * DEGREES).next_to(y_labels, LEFT, buff=0.5)
        
        x_title = MathTex(r"\text{Compute}", font_size=36)
        x_subtitle = MathTex(r"\text{PF-days, non-embedding}", font_size=30, color=GRAY)
        x_center = (axes.c2p(10**x_min_exp, y_min)[0] + axes.c2p(10**x_max_exp, y_min)[0]) / 2
        x_title.move_to([x_center, x_labels.get_bottom()[1] - 0.5, 0])
        x_subtitle.next_to(x_title, DOWN, buff=0.1)
        
        blue_curves = VGroup()
        for curve_data in curves_data:
            # Filter points to stay within axis bounds (y <= 7)
            clipped_data = [(x, min(y, y_max)) for x, y in curve_data if y <= y_max or True]
            # Only include points where y <= y_max, and clip the first point if needed
            filtered_data = []
            for x, y in curve_data:
                if y <= y_max:
                    filtered_data.append((x, y))
                elif not filtered_data:  # First points above y_max, clip to y_max
                    filtered_data.append((x, y_max))
            if filtered_data:
                curve_points = [axes.c2p(x, y) for x, y in filtered_data]
                curve = VMobject(color=BLUE, stroke_width=1.5, stroke_opacity=0.7)
                curve.set_points_smoothly(curve_points)
                blue_curves.add(curve)
        
        def best_fit(x):
            return (x / 2.3e8) ** (-0.050)
        
        # Limit pareto frontier to axis bounds
        x_fit_values = np.logspace(x_min_exp, x_max_exp, 100)
        fit_points = [axes.c2p(x, best_fit(x)) for x in x_fit_values if y_min <= best_fit(x) <= y_max]
        best_fit_line = DashedVMobject(VMobject(color=ORANGE, stroke_width=3).set_points_smoothly(fit_points), num_dashes=60)
        
        eq_box = Rectangle(width=4.5, height=0.7, stroke_color=GRAY, stroke_width=1, fill_color=BLACK, fill_opacity=0.8)
        eq_box.move_to(axes.c2p(10**-5.5, 2.35))
        equation = MathTex(r"L = (C_{\min}/2.3 \cdot 10^{8})^{-0.050}", font_size=28, color=WHITE)
        eq_line = DashedLine(LEFT * 0.4, RIGHT * 0.4, color=ORANGE, stroke_width=2)
        eq_line.move_to(eq_box.get_left() + RIGHT * 0.6)
        equation.next_to(eq_line, RIGHT, buff=0.2)
        eq_group = VGroup(eq_box, eq_line, equation)
        
        # Animation
        self.play(Create(square_path), run_time=2)
        self.play(FadeIn(x_labels), FadeIn(y_labels), FadeIn(x_ticks), FadeIn(y_ticks), run_time=1)
        self.play(Write(x_title), Write(x_subtitle), Write(y_title), run_time=1)
        self.wait(0.5)
        
        # First 3 curves slowly
        for i in range(3):
            self.play(Create(blue_curves[i]), run_time=1.5)
        
        # Remaining curves fast
        self.play(LaggedStart(*[Create(curve) for curve in blue_curves[3:]], lag_ratio=0.05), run_time=3)
        
        self.wait(0.5)
        self.play(Create(best_fit_line), run_time=2)
        self.play(FadeIn(eq_box), Write(eq_line), Write(equation), run_time=1)
        self.wait(2)