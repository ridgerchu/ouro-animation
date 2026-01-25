from manim import *

class ScalingAnimation(Scene):
    def construct(self):
        # Set transparent background
        self.camera.background_color = None
        
        # 3Blue1Brown inspired color scheme
        BLUE = "#1E90FF"      # Dodger blue
        YELLOW = "#FFFF00"    # Yellow
        GREEN = "#83C167"     # Soft green
        RED = "#FF6B6B"       # Soft red
        TEAL = "#5CD1E5"      # Teal/cyan
        PINK = "#FF69B4"      # Pink
        ORANGE = "#FFA500"    # Orange
        
        model_color = BLUE
        data_color = GREEN
        compute_color = YELLOW
        
        # Create titles
        model_title = Text("Model Size", font_size=36, color=model_color)
        data_title = Text("Dataset Size", font_size=36, color=data_color)
        compute_title = Text("Compute", font_size=36, color=compute_color)
        
        # Position titles
        model_title.move_to(LEFT * 4 + UP * 2.5)
        data_title.move_to(UP * 2.5)
        compute_title.move_to(RIGHT * 4 + UP * 2.5)
        
        # Create neural network
        def create_network(layers, node_radius=0.15, spacing=0.8):
            network = VGroup()
            layer_groups = []
            
            for i, num_nodes in enumerate(layers):
                layer = VGroup()
                for j in range(num_nodes):
                    node = Circle(
                        radius=node_radius, 
                        color=model_color, 
                        fill_opacity=0.8,
                        stroke_width=2
                    )
                    node.move_to(UP * (j - (num_nodes - 1) / 2) * spacing * 0.6)
                    layer.add(node)
                layer.move_to(RIGHT * i * spacing)
                layer_groups.append(layer)
                network.add(layer)
            
            # Add edges
            edges = VGroup()
            for i in range(len(layer_groups) - 1):
                for node1 in layer_groups[i]:
                    for node2 in layer_groups[i + 1]:
                        edge = Line(
                            node1.get_center(), 
                            node2.get_center(),
                            stroke_width=1.5,
                            color=TEAL,
                            stroke_opacity=0.4
                        )
                        edges.add(edge)
            
            return VGroup(edges, network)
        
        # Dataset: Vocabulary token boxes
        def create_dataset(tokens, cols=3):
            token_boxes = VGroup()
            
            # Calculate box size based on longest token
            max_len = max(len(t) for t in tokens)
            box_width = max(0.45, min(0.8, max_len * 0.09 + 0.15))
            box_height = 0.32
            
            for i, token in enumerate(tokens):
                row = i // cols
                col = i % cols
                
                # Create rounded rectangle box
                box = RoundedRectangle(
                    corner_radius=0.06,
                    width=box_width,
                    height=box_height,
                    color=data_color,
                    fill_opacity=0.15,
                    stroke_width=2
                )
                
                # Add token text - scale to fit inside box
                text = Text(token, font_size=18, color=data_color)
                # Scale down if text is too wide
                max_text_width = box_width * 0.85
                if text.width > max_text_width:
                    text.scale(max_text_width / text.width)
                text.move_to(box.get_center())
                
                token_group = VGroup(box, text)
                
                # Position in grid
                total_rows = (len(tokens) + cols - 1) // cols
                x_offset = (col - (cols - 1) / 2) * (box_width + 0.1)
                y_offset = (row - (total_rows - 1) / 2) * (box_height + 0.1)
                token_group.move_to([x_offset, -y_offset, 0])
                
                token_boxes.add(token_group)
            
            return token_boxes
        
        # Compute: GPU/chip representation
        def create_compute(num_units, unit_size=0.3):
            compute = VGroup()
            cols = int(num_units ** 0.5)
            if cols * cols < num_units:
                cols += 1
            
            for i in range(num_units):
                row = i // cols
                col = i % cols
                
                # Create chip-like square with inner detail
                unit = RoundedRectangle(
                    corner_radius=0.03,
                    width=unit_size,
                    height=unit_size,
                    color=compute_color,
                    fill_opacity=0.2,
                    stroke_width=2
                )
                
                # Add inner circuit-like detail
                inner = Square(
                    side_length=unit_size * 0.5,
                    color=compute_color,
                    fill_opacity=0.5,
                    stroke_width=1
                )
                inner.move_to(unit.get_center())
                
                chip = VGroup(unit, inner)
                chip.move_to(
                    RIGHT * (col - (cols - 1) / 2) * (unit_size + 0.08) + 
                    DOWN * (row - (num_units // cols - 1) / 2) * (unit_size + 0.08)
                )
                compute.add(chip)
            
            compute.move_to(ORIGIN)
            return compute
        
        # Small vocabulary tokens
        small_tokens = ["not", "many", "tokens"]
        
        # Large vocabulary tokens  
        large_tokens = [
            "a", "much", "larger",
            "number", "of", "tokens",
            "in", "my", "dataset"
        ]
        
        # Initial states (small)
        small_network = create_network([2, 3, 2], node_radius=0.12, spacing=0.6)
        small_network.move_to(LEFT * 4 + DOWN * 0.3)
        
        small_dataset = create_dataset(small_tokens, cols=3)
        small_dataset.move_to(DOWN * 0.3)
        
        small_compute = create_compute(4, unit_size=0.28)
        small_compute.move_to(RIGHT * 4 + DOWN * 0.3)
        
        # Large states
        large_network = create_network([4, 6, 6, 4], node_radius=0.12, spacing=0.6)
        large_network.move_to(LEFT * 4 + DOWN * 0.3)
        
        large_dataset = create_dataset(large_tokens, cols=3)
        large_dataset.move_to(DOWN * 0.3)
        
        large_compute = create_compute(16, unit_size=0.28)
        large_compute.move_to(RIGHT * 4 + DOWN * 0.3)
        
        # Animation sequence
        # Fade in titles
        self.play(
            FadeIn(model_title),
            FadeIn(data_title),
            FadeIn(compute_title),
            run_time=1
        )
        
        # Fade in initial small states
        self.play(
            FadeIn(small_network),
            FadeIn(small_dataset),
            FadeIn(small_compute),
            run_time=1
        )
        
        self.wait(0.5)
        
        # Grow/transform to larger states
        self.play(
            ReplacementTransform(small_network, large_network),
            ReplacementTransform(small_dataset, large_dataset),
            ReplacementTransform(small_compute, large_compute),
            run_time=2
        )
        
        # Add scaling indicators
        scale_text_model = Text("↑", font_size=48, color=model_color).move_to(LEFT * 4 + DOWN * 2.3)
        scale_text_data = Text("↑", font_size=48, color=data_color).move_to(DOWN * 2.3)
        scale_text_compute = Text("↑", font_size=48, color=compute_color).move_to(RIGHT * 4 + DOWN * 2.3)
        
        self.play(
            FadeIn(scale_text_model),
            FadeIn(scale_text_data),
            FadeIn(scale_text_compute),
            run_time=0.5
        )
        
        self.wait(1)
        
        # Final pulse effect
        self.play(
            large_network.animate.scale(1.1),
            large_dataset.animate.scale(1.1),
            large_compute.animate.scale(1.1),
            run_time=0.3
        )
        self.play(
            large_network.animate.scale(1/1.1),
            large_dataset.animate.scale(1/1.1),
            large_compute.animate.scale(1/1.1),
            run_time=0.3
        )
        
        self.wait(1)