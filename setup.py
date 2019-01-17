from setuptools import setup

setup(
    name='redistools',
    version='1.0.2',
    description='A set of tools we use to easily access redis',
    url='https://github.com/IntuitionMachines/redis-tools',
    author='Intuition Machines',
    author_email='dev@intuitionmachines.com',
    license='MIT',
    packages=['redistools'],
    install_requires=["redis"],
    zip_safe=False)
