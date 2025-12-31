from setuptools import setup, find_packages

setup(
    name="graph",
    version="0.1.0",
    description="Stock charting module with technical indicators",
    author="Trading Alpha",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "plotly>=5.18.0",
        "kaleido>=0.2.1",
    ],
    python_requires=">=3.11",
)
