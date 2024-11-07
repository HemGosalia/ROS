from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'turtle_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name), glob('launch/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='heisenberg_31',
    maintainer_email='heisenberg_31@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'control = turtle_control.turtle_controller:main',
            'control1 = turtle_control.turtle_straight:main',
            'control2 = turtle_control.turtle_turn:main',
            'control3 = turtle_control.turtle_controller_PID:main',
        ],
    },
)
