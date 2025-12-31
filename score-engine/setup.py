from setuptools import setup, find_packages

setup(
    name="score-engine",
    version="0.1.0",
    description="Stock scoring engine for long entry opportunities",
    author="Trading Alpha",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.0.0,<3.0.0",
        "numpy>=1.24.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
        ]
    },
    python_requires=">=3.11",
)