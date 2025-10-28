from setuptools import setup, find_packages

setup(
    name="crypto-screener",
    version="1.0.0",
    description="Crypto Futures Screener with EMA Crossover",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.28.0",
        "pandas>=2.1.3",
        "ccxt>=4.1.56",
        "plotly>=5.17.0",
        "ta>=0.10.2",
    ],
    python_requires=">=3.8",
)