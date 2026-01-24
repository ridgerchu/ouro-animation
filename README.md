# Manim 测试动画

这个文件夹包含 Manim 动画测试示例。

## ⚠️ 重要提示

建议在**独立的虚拟环境**中使用 Manim，避免影响主环境：

```bash
# 创建虚拟环境
conda create -n manim_env python=3.11
conda activate manim_env

# 安装系统依赖 (macOS)
brew install cairo pkg-config

# 安装 manim
pip install manim
```

## 🎬 可用场景

`manim_test.py` 包含 4 个测试场景：

1. **BasicShapes** - 基础图形动画（圆形、方形、三角形）
2. **EquationScene** - 数学公式动画（爱因斯坦方程等）
3. **GraphScene** - 函数图像动画（sin/cos 函数）
4. **DataVisualization** - 数据可视化（柱状图）

## 🚀 使用方法

### 基本命令

```bash
# 低质量预览（快速）
manim -pql manim_test.py BasicShapes

# 中等质量
manim -pqm manim_test.py BasicShapes

# 高质量渲染
manim -pqh manim_test.py BasicShapes

# 渲染所有场景
manim -pql manim_test.py
```

### 参数说明

- `-p`: 渲染完成后自动播放
- `-q`: 质量设置
  - `l`: low (480p)
  - `m`: medium (720p)
  - `h`: high (1080p)
  - `k`: 4k (2160p)

### 示例命令

```bash
# 运行基础图形动画
manim -pql manim_test.py BasicShapes

# 运行数学公式动画
manim -pql manim_test.py EquationScene

# 运行函数图像动画
manim -pql manim_test.py GraphScene

# 运行数据可视化
manim -pql manim_test.py DataVisualization
```

## 📁 输出位置

渲染的视频会保存在：
```
media/videos/manim_test/480p15/
```

## 📚 学习资源

- [Manim 官方文档](https://docs.manim.community/)
- [Manim 示例库](https://docs.manim.community/en/stable/examples.html)
- [3Blue1Brown 频道](https://www.youtube.com/c/3blue1brown) - Manim 创始人的频道

