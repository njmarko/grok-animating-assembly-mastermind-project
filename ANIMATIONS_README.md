# Mastermind Assembly Blog Animations

This repository contains a parameterized animation system for generating GIFs and videos for the Mastermind Assembly blog post. Each animation demonstrates different aspects of the assembly implementation.

## 🚀 Quick Start

### Generate a Single Animation

```bash
# Activate your virtual environment first
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac

# Run any animation
python run_animation.py register_packing
python run_animation.py exact_match --format mp4
python run_animation.py benchmark_chart --quality low
```

### Advanced Usage

```bash
# High quality GIF for blog
python run_animation.py entropy_reduction --format gif --quality high

# MP4 video for presentation
python run_animation.py stack_overwrite --format mp4 --quality medium

# Custom output directory
python run_animation.py elimination_loop --output ./blog_gifs

# Use custom configuration
python animations.py register_packing --config my_config.json
```

## 📚 Available Animations

| Animation | Description | Use Case |
|-----------|-------------|----------|
| `register_packing` | Shows bit placement in registers using rorb/rorl | Demonstrates core optimization |
| `exact_match` | Bit operations for exact match calculation | Feedback computation |
| `elimination_loop` | Candidate filtering and elimination | Main game loop |
| `entropy_reduction` | Possibility reduction visualization | Algorithm efficiency |
| `stack_overwrite` | Stack manipulation for printf display | Display optimization |
| `benchmark_chart` | Performance comparison: Assembly vs C | Results presentation |

## ⚙️ Configuration

### Default Parameters

Each animation has sensible defaults, but you can customize:

```json
{
  "background_color": "#1a1a1a",
  "text_color": "WHITE",
  "highlight_color": "YELLOW",
  "success_color": "GREEN",
  "font_size": 36,
  "animation_speed": 1.0,
  "fps": 30
}
```

### Animation-Specific Parameters

- **Register Packing**: `symbols`, `symbol_bits`, `initial_mask`
- **Exact Match**: `guess_value`, `secret_value`, `bit_operations`
- **Elimination Loop**: `num_candidates`, `candidates_to_keep`
- **Entropy Reduction**: `initial_possibilities`, `remaining_counts`, `entropy_bits`
- **Stack Overwrite**: `stack_slots`, `symbols_to_push`, `skip_slots`
- **Benchmark Chart**: `assembly_time`, `c_time`, `max_time`

## 🏗️ Architecture

### BaseAnimation Class

All animations inherit from `BaseAnimation` which provides:
- Common scene setup and cleanup
- Register visualization helpers
- Code highlighting utilities
- Bit manipulation animations
- Configuration management

### Factory Pattern

```python
from animations import create_animation

# Create any animation by name
anim = create_animation('register_packing', custom_config)
```

### Easy Extension

To add a new animation:
1. Create a class inheriting from `BaseAnimation`
2. Implement `get_default_config()` class method
3. Implement `construct()` method
4. Add to the `animations` dictionary in `create_animation()`
5. Update the argument parser choices

## 🎨 Output Formats

- **GIF**: Optimized for web, smaller file size
- **MP4**: Better quality, supports higher resolutions
- **Quality Levels**: low (480p), medium (720p), high (1080p)

## 📁 File Structure

```
project/
├── animations.py          # Main animation classes and factory
├── run_animation.py       # Simple command-line runner
├── blog.md               # Original blog post
├── requirements.txt      # Python dependencies
├── .gitignore           # Git ignore rules
└── media/               # Output directory (auto-created)
    ├── register_packing.gif
    ├── exact_match.mp4
    └── ...
```

## 🔧 Dependencies

All dependencies are listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

Key packages:
- `manim`: Mathematical animation engine
- `numpy`, `scipy`: Mathematical computations
- `pillow`: Image processing
- `rich`: Terminal formatting

## 🎯 Use Cases

### Blog Integration
Generate specific GIFs for embedding in blog posts:
```bash
python run_animation.py register_packing --quality high --output ./blog-assets
```

### Presentations
Create MP4 videos for talks or demos:
```bash
python run_animation.py entropy_reduction --format mp4 --quality medium
```

### Development
Quick low-quality previews during development:
```bash
python run_animation.py benchmark_chart --quality low
```

## 🚦 Troubleshooting

### Common Issues

1. **Virtual environment not activated**
   ```bash
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

2. **Output directory doesn't exist**
   - The script creates it automatically

3. **Animation fails to render**
   - Check available disk space
   - Try lower quality setting
   - Ensure all dependencies are installed

4. **Memory issues with high quality**
   - Use `--quality low` or `medium`
   - Close other applications

### Performance Tips

- **GIF rendering**: Use `--quality medium` for faster rendering
- **MP4 rendering**: Better for high-quality output
- **Batch processing**: Run multiple animations sequentially
- **Caching**: Manim caches intermediate results

## 🤝 Contributing

To add new animations:

1. Study existing animation implementations
2. Follow the BaseAnimation pattern
3. Test with different quality settings
4. Update documentation
5. Add to the animations dictionary

## 📄 License

Same as the main project - see repository license file.