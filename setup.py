"""
setup configuration for doctor appointment system
"""

from setuptools import setup, find_packages
import os

# read requirements
def read_requirements():
    with open('requirements.txt', 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# read readme
def read_readme():
    if os.path.exists('README.md'):
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    return "Doctor Appointment System with Multi-Agent AI"

setup(
    name="agentic-doctor-appointment-system",
    version="1.0.0",
    description="AI-powered doctor appointment system with memory-enabled chat",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Oladimeji Balogun",
    author_email="oladimejib.tech@gmail.com",
    url="https://github.com/OlaTheTechie/agentic-doctor-appointment-system",
    
    # package configuration
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # dependencies
    install_requires=read_requirements(),
    
    # python version requirement
    python_requires=">=3.8",
    
    # entry points
    entry_points={
        "console_scripts": [
            "appointment-server=main:main",
            "appointment-ui=ui.run_enhanced_app:main",
        ],
    },
    
    # package data
    package_data={
        "": ["*.json", "*.csv", "*.conf", "*.md"],
    },
    
    # include additional files
    include_package_data=True,
    
    # classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    
    # keywords
    keywords="healthcare, ai, appointments, chatbot, multi-agent",
    
    # project urls
    project_urls={
        # "Bug Reports": "https://github.com/OlaTheTechie/doctor-appointment-system/issues",
        "Source": "https://github.com/OlaTheTechie/agentic-doctor-appointment-system/",
        "Documentation": "https://github.com/OlaTheTechie/doctor-appointment-system/docs",
    },
)