from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='android-mobile-mcp',
    version='2.1.0',
    author='erichung0906',
    author_email='rthung96@gmail.com',
    description='Android Mobile MCP',
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        "Bug Tracker": "https://github.com/erichung9060/Android-Mobile-MCP/issues",
        "Repository": "https://github.com/erichung9060/Android-Mobile-MCP",
    },
    keywords=['android', "mobile", "mcp", "mobile-mcp", "android-mcp"],
    py_modules=['main'],
    install_requires=[
        'uiautomator2',
        'fastmcp',
    ],
    entry_points={
        'console_scripts': [
            'android-mobile-mcp=main:main',
        ],
    },
)