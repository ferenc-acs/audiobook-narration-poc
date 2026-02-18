from setuptools import setup, find_packages

setup(
    name="audiobook-narrator",
    version="0.1.0",
    description="Emotional audiobook narration using Piper TTS",
    author="Ferenc Acs",
    packages=find_packages(),
    install_requires=[
        "piper-tts>=1.2.0",
        "pydub>=0.25.1",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "audiobook-narrator=narrator_cli:main",
        ],
    },
)
