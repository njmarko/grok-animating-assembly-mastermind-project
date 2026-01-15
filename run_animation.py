#!/usr/bin/env python3
"""
Simple script to run individual animations for the Mastermind Assembly Blog.

Usage:
    python run_animation.py register_packing
    python run_animation.py exact_match --format gif --quality high
    python run_animation.py benchmark_chart --output ./gifs
"""

import subprocess
import sys
import os
from pathlib import Path

def run_animation(animation_name: str, format_type: str = 'gif', quality: str = 'high',
                 output_dir: str = 'media', config_file: str = None):
    """Run a specific animation with given parameters."""

    cmd = [
        sys.executable, 'animations.py',
        animation_name,
        '--format', format_type,
        '--quality', quality,
        '--output', output_dir
    ]

    if config_file:
        cmd.extend(['--config', config_file])

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=Path(__file__).parent)

    if result.returncode == 0:
        output_file = Path(output_dir) / f"{animation_name}.{format_type}"
        if output_file.exists():
            print(f"✅ Animation saved to: {output_file}")
        else:
            print(f"⚠️  Animation completed but file not found at: {output_file}")
    else:
        print(f"❌ Animation failed with exit code: {result.returncode}")

    return result.returncode

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nAvailable animations:")
        animations = [
            'register_packing - Register bit placement execution',
            'exact_match - Exact match calculation with bit operations',
            'elimination_loop - Candidate elimination loop execution',
            'entropy_reduction - Entropy reduction visualization',
            'stack_overwrite - Stack overwrite execution for printf',
            'benchmark_chart - Performance comparison chart'
        ]
        for anim in animations:
            print(f"  {anim}")
        print("\nExamples:")
        print("  python run_animation.py register_packing")
        print("  python run_animation.py exact_match --format mp4 --quality low")
        print("  python run_animation.py benchmark_chart --output ./exports")
        return

    animation_name = sys.argv[1]

    # Parse additional arguments
    format_type = 'gif'
    quality = 'high'
    output_dir = 'media'
    config_file = None

    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--format' and i + 1 < len(sys.argv):
            format_type = sys.argv[i + 1]
            i += 2
        elif arg == '--quality' and i + 1 < len(sys.argv):
            quality = sys.argv[i + 1]
            i += 2
        elif arg == '--output' and i + 1 < len(sys.argv):
            output_dir = sys.argv[i + 1]
            i += 2
        elif arg == '--config' and i + 1 < len(sys.argv):
            config_file = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    # Validate animation name
    valid_animations = [
        'register_packing', 'exact_match', 'elimination_loop',
        'entropy_reduction', 'stack_overwrite', 'benchmark_chart'
    ]

    if animation_name not in valid_animations:
        print(f"❌ Unknown animation: {animation_name}")
        print(f"Available: {', '.join(valid_animations)}")
        return 1

    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Run the animation
    return run_animation(animation_name, format_type, quality, output_dir, config_file)

if __name__ == "__main__":
    sys.exit(main())