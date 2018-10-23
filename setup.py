from setuptools import setup

setup(name='redishelpers',
      version='0.1.1',
      description='A set of tools we use to easily access redis',
      url='git@github.com:HCaptcha/redis-tools.git',
      author='Intuition Machines',
      author_email='contact@intuitionmachines.com',
      license='MIT',
      packages=['redishelpers'],
      install_requires=["redis"],
      zip_safe=False)

