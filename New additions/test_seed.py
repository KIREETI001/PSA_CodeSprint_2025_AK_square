"""
Quick Seed Tester
Usage: python test_seed.py <seed_number>
Example: python test_seed.py 42
"""

import sys
import re
from pathlib import Path

def update_seed(seed_value):
    """Update the random seed in job_planner.py"""
    file_path = Path("src/plan/job_planner.py")
    content = file_path.read_text()
    
    # Replace the seed value
    new_content = re.sub(
        r'random\.seed\(\d+\)',
        f'random.seed({seed_value})',
        content
    )
    
    file_path.write_text(new_content)
    print(f"✅ Updated random seed to {seed_value} in job_planner.py")
    print(f"Now run: python cli.py")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_seed.py <seed_number>")
        print("Example: python test_seed.py 42")
        sys.exit(1)
    
    try:
        seed = int(sys.argv[1])
        update_seed(seed)
    except ValueError:
        print("Error: Seed must be an integer")
        sys.exit(1)
