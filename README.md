# Manim Test Animations

This folder contains Manim animation test examples.

## ⚠️ Important Note

It is recommended to use Manim in a **separate virtual environment** to avoid affecting the main environment:

```bash
# Create virtual environment
conda create -n manim_env python=3.11
conda activate manim_env

# Install system dependencies (macOS)
brew install cairo pkg-config

# Install manim
pip install manim
```

## 🎬 Available Scenes

`manim_test.py` contains 4 test scenes:

1. **BasicShapes** - Basic shape animations (circle, square, triangle)
2. **EquationScene** - Mathematical equation animations (Einstein's equation, etc.)
3. **GraphScene** - Function graph animations (sin/cos functions)
4. **DataVisualization** - Data visualization (bar chart)

## 🚀 Usage

### Basic Commands

```bash
# Low quality preview (fast)
manim -pql manim_test.py BasicShapes

# Medium quality
manim -pqm manim_test.py BasicShapes

# High quality rendering
manim -pqh manim_test.py BasicShapes

# Render all scenes
manim -pql manim_test.py
```

### Parameter Description

- `-p`: Automatically play after rendering completes
- `-q`: Quality settings
  - `l`: low (480p)
  - `m`: medium (720p)
  - `h`: high (1080p)
  - `k`: 4k (2160p)

### Example Commands

```bash
# Run basic shape animation
manim -pql manim_test.py BasicShapes

# Run mathematical equation animation
manim -pql manim_test.py EquationScene

# Run function graph animation
manim -pql manim_test.py GraphScene

# Run data visualization
manim -pql manim_test.py DataVisualization
```

## 📁 Output Location

Rendered videos will be saved in:
```
media/videos/manim_test/480p15/
```

## 📚 Learning Resources

- [Manim Official Documentation](https://docs.manim.community/)
- [Manim Example Library](https://docs.manim.community/en/stable/examples.html)
- [3Blue1Brown Channel](https://www.youtube.com/c/3blue1brown) - Channel of Manim's creator
