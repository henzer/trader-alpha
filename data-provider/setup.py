from setuptools import setup, find_packages

setup(
    name="data-provider",
    version="0.1.0",
    description="Data provider for stock market data with caching",
    author="Trading Alpha",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.0.0,<3.0.0",
        "numpy>=1.24.0",
        "pydantic>=2.0.0",
        "yfinance>=0.2.0",
        "pyarrow>=14.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
        ]
    },
    python_requires=">=3.11",
)
