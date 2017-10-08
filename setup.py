from setuptools import setup, find_packages

setup(
    name='modules',
    packages=find_packages(),  # Allows absolute imports to work correctly (See #3 @ https://stackoverflow.com/a/28154841)
    install_requires=[
        'SocketServer',
        'opencv-python',
        'numpy',
    ]
)
