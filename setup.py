from setuptools import setup, find_packages

setup(
    name="youtube-analytics-framework",
    version="0.1.0",
    description="YouTube Analytics Framework with MCP Integration",
    author="Ahmed Yaqub",
    author_email="mseexteen@gmail.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.116.1",
        "uvicorn>=0.35.0",
        "pandas>=2.3.1",
        "numpy>=2.3.2",
        "sqlalchemy>=2.0.23",
        "python-dotenv>=1.1.1",
        "pydantic>=2.11.7",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "black>=23.11.0",
            "flake8>=6.1.0",
        ]
    },
)
