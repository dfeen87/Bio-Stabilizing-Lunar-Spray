"""
Setup configuration for Bio-Stabilizing Lunar Spray

Installation:
    pip install -e .              # Development install
    pip install .                 # Regular install
    python setup.py sdist         # Create source distribution
    python setup.py bdist_wheel   # Create wheel distribution
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file) as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
else:
    requirements = [
        "numpy>=1.21.0,<2.0.0",
        "scipy>=1.7.0,<2.0.0",
        "matplotlib>=3.4.0,<4.0.0",
        "pandas>=1.3.0,<2.0.0",
    ]

setup(
    # ========================================================================
    # Package Metadata
    # ========================================================================
    name="bio-stabilizing-lunar-spray",
    version="0.1.0",
    author="Don Michael Feeney Jr",
    author_email="dfeen87@gmail.com",  
    description="A dual-purpose surface and agricultural solution for lunar habitats",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dfeen87/bio-stabilizing-lunar-spray", 
    project_urls={
        "Bug Reports": "https://github.com/dfeen87/bio-stabilizing-lunar-spray/issues",
        "Source": "https://github.com/dfeen87/bio-stabilizing-lunar-spray",
        "Documentation": "https://github.com/dfeen87/bio-stabilizing-lunar-spray/tree/main/docs",
    },
    
    # ========================================================================
    # Package Configuration
    # ========================================================================
    packages=find_packages(exclude=["tests", "tests.*", "docs", "examples"]),
    include_package_data=True,
    python_requires=">=3.8",
    
    # ========================================================================
    # Dependencies
    # ========================================================================
    install_requires=requirements,
    
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "notebooks": [
            "jupyter>=1.0.0",
            "ipython>=8.0.0",
            "notebook>=6.4.0",
        ],
        "viz": [
            "seaborn>=0.11.0",
            "plotly>=5.0.0",
        ],
    },
    
    # ========================================================================
    # Package Classification
    # ========================================================================
    classifiers=[
        # Development Status
        "Development Status :: 3 - Alpha",
        
        # Intended Audience
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        
        # Topic
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        
        # License
        "License :: OSI Approved :: MIT License",
        
        # Python Versions
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        
        # Operating Systems
        "Operating System :: OS Independent",
        
        # Natural Language
        "Natural Language :: English",
    ],
    
    # ========================================================================
    # Keywords
    # ========================================================================
    keywords=[
        "lunar",
        "space",
        "agriculture",
        "geopolymer",
        "regolith",
        "ISRU",
        "habitat",
        "simulation",
        "chemistry",
        "environmental-control",
    ],
    
    # ========================================================================
    # Entry Points (Command Line Tools)
    # ========================================================================
    entry_points={
        "console_scripts": [
            "lunar-spray=integrated_simulation:main",
        ],
    },
    
    # ========================================================================
    # Package Data
    # ========================================================================
    package_data={
        "": ["*.md", "*.txt"],
    },
    
    # ========================================================================
    # Additional Options
    # ========================================================================
    zip_safe=False,
    platforms=["any"],
)


# Optional: Add main() function for command-line usage
def main():
    """
    Main entry point for command-line interface.
    
    Usage:
        lunar-spray
    """
    from integrated_simulation import run_example_mission
    print("Running example lunar spray mission...")
    run_example_mission()


if __name__ == "__main__":
    # Allow running setup.py directly
    pass
