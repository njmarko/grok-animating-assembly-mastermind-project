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

    # Map animation names to class names
    animation_to_class = {
        'register_packing': 'RegisterPackingExecution',
        'register_packing_detailed': 'RegisterPackingDetailed',
        'register_packing_accurate': 'RegisterPackingAccurate',
        'register_packing_accurate_fixed': 'RegisterPackingAccurateFixed',
        'exact_match': 'ExactMatchExecution',
        'elimination_loop': 'EliminationLoopExecution',
        'entropy_reduction': 'EntropyReduction',
        'stack_overwrite': 'StackOverwriteExecution',
        'benchmark_chart': 'BenchmarkChart'
    }

    # Get the actual class name for manim
    class_name = animation_to_class[animation_name]

    # Build manim command
    cmd = [
        sys.executable, "-m", "manim",
        "--format", format_type,
        "--media_dir", output_dir,
        "--custom_folders",
        "-v", "WARNING"  # Reduce verbosity
    ]

    # Add quality settings
    if quality == "low":
        cmd.extend(["-ql"])
    elif quality == "medium":
        cmd.extend(["-qm"])
    else:  # high
        cmd.extend(["-qh"])

    # Add the animation class
    cmd.extend(["animations.py", class_name])

    print(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent, capture_output=True, text=True)

        if result.returncode == 0:
            print("Animation rendering completed successfully!")

            # Check for the output file (manim usually names it after the class)
            expected_files = [
                Path(output_dir) / f"{class_name}.{format_type}",
                Path(output_dir) / f"{animation_name}.{format_type}"
            ]

            found_file = None
            for expected_file in expected_files:
                if expected_file.exists():
                    found_file = expected_file
                    break

            if found_file:
                print(f"SUCCESS: Animation saved to: {found_file}")
            else:
                # Look for manim-generated files and rename them
                output_path = Path(output_dir)
                if output_path.exists():
                    # Look for files that match the class name pattern
                    for file in output_path.glob(f"{class_name}*.{format_type}"):
                        user_friendly_name = output_path / f"{animation_name}.{format_type}"
                        file.rename(user_friendly_name)
                        print(f"SUCCESS: Animation saved to: {user_friendly_name}")
                        found_file = user_friendly_name
                        break

                if not found_file:
                    print(f"Warning: Expected output file not found")
                    print("Files in output directory:")
                    for file in output_path.glob("*"):
                        if file.is_file():
                            print(f"  {file.name}")
        else:
            print(f"ERROR: Animation rendering failed with exit code: {result.returncode}")
            print("STDOUT:", result.stdout[-500:])  # Last 500 chars
            if result.stderr:
                print("STDERR:", result.stderr[-500:])  # Last 500 chars

    except Exception as e:
        print(f"ERROR: Animation rendering failed: {e}")

    return result.returncode if 'result' in locals() else 1

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nAvailable animations:")
        animations = [
            'register_packing - Register bit placement execution',
            'register_packing_detailed - Detailed register packing with visual bytes',
            'register_packing_accurate - Accurate register packing with bit rotation',
            'register_packing_accurate_fixed - Fixed accurate register packing with bit labels',
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

    # Validate animation name and map to class names
    animation_to_class = {
        'register_packing': 'RegisterPackingExecution',
        'register_packing_detailed': 'RegisterPackingDetailed',
        'register_packing_accurate': 'RegisterPackingAccurate',
        'register_packing_accurate_fixed': 'RegisterPackingAccurateFixed',
        'exact_match': 'ExactMatchExecution',
        'elimination_loop': 'EliminationLoopExecution',
        'entropy_reduction': 'EntropyReduction',
        'stack_overwrite': 'StackOverwriteExecution',
        'benchmark_chart': 'BenchmarkChart'
    }

    valid_animations = list(animation_to_class.keys())

    if animation_name not in valid_animations:
        print(f"ERROR: Unknown animation: {animation_name}")
        print(f"Available: {', '.join(valid_animations)}")
        return 1

    # Get the actual class name for manim
    class_name = animation_to_class[animation_name]

    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Run the animation
    return run_animation(animation_name, format_type, quality, output_dir, config_file)

if __name__ == "__main__":
    sys.exit(main())