from setuptools import find_packages, setup
import os 
 
from glob import glob 

package_name = 'urdf_tutorial'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),glob('launch/*')), 
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        (os.path.join('share', package_name, 'meshes'), glob('meshes/*')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
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
            "controller_fk = urdf_tutorial.controller_fk:main",
            'control=urdf_tutorial.control:main',
            "inv_controller_fk = urdf_tutorial.inv_controller_fk:main",
            'inv_control=urdf_tutorial.inv_control:main',
            "ur5_controller_fk = urdf_tutorial.ur5_controller_fk:main",
            'ur5_control=urdf_tutorial.ur5_control:main',
        ],
    },
)
