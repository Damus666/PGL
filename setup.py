from setuptools import setup

setup(
   name='pgl',
   version='0.1',
   description='A python library of an entity-based engine/framework',
   author='Damus',
   author_email='ricciardi.damiano06@gmail.com',
   packages=['pgl'],
   install_requires=['pygame-ce', 'moderngl==5.9.0', 'PyGLM', 'noise', 'numpy'],
)