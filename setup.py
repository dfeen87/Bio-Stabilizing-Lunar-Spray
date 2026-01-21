from setuptools import setup, find_packages

setup(
    name="bio-stabilizing-lunar-spray",
    version="0.1.0",
    author="Don Michael Feeney Jr",
    author_email="dfeen87@gmail.com.com",
    description="Dual-purpose regolith stabilization and agricultural substrate",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/dfeen87/bio-stabilizing-lunar-spray",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Chemistry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "matplotlib>=3.4.0",
    ],
)
