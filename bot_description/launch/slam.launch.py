import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():

    pkg_bot_description = get_package_share_directory('bot_description')
    pkg_slam_toolbox = get_package_share_directory('slam_toolbox')

    slam_params_file = os.path.join(pkg_bot_description, 'config', 'slam_params.yaml')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_bot_description, 'launch', 'gazebo.launch.py')
        )
    )

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_slam_toolbox, 'launch', 'online_async_launch.py')
        ),
        launch_arguments={
            'slam_params_file': slam_params_file,
            'use_sim_time': 'true',
        }.items()
    )

    return LaunchDescription([
        gazebo,
        slam,
    ])
