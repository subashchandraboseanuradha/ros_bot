import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import re
import xacro

def generate_launch_description():

    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_bot_description = get_package_share_directory('bot_description')
    pkg_warehouse = get_package_share_directory('aws_robomaker_small_warehouse_world')

    warehouse_world = os.path.join(
        pkg_warehouse, 'worlds', 'small_warehouse', 'small_warehouse.world')

    declare_world = DeclareLaunchArgument(
        'world',
        default_value=warehouse_world,
        description='Full path to world file to load (pass empty string for default empty world)')

    robot_description_file = os.path.join(pkg_bot_description, 'urdf', 'bot.xacro')
    robot_description_config = xacro.process_file(robot_description_file)
    # gazebo_ros2_control passes robot_description as --param to rcl_parse_arguments,
    # which treats the value as YAML. XML comments containing ': ' (e.g. "Root link: KDL...")
    # cause YAML parse failures. Strip declaration and comments to fix this.
    robot_description_str = robot_description_config.toxml()
    if '?>' in robot_description_str:
        robot_description_str = robot_description_str.split('?>', 1)[1].strip()
    robot_description_str = re.sub(r'<!--.*?-->', '', robot_description_str, flags=re.DOTALL).strip()
    robot_description = {'robot_description': robot_description_str}

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': True}],
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'world': LaunchConfiguration('world')}.items()
    )

    spawn_robot = TimerAction(
        period=5.0,
        actions=[Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=[
                '-topic', '/robot_description',
                '-entity', 'bot',
                '-x', '0.0',
                '-y', '0.0',
                '-z', '0.05',
                '-Y', '0.0',
            ],
            output='screen'
        )]
    )

    joint_state_broadcaster = TimerAction(
        period=8.0,
        actions=[Node(
            package='controller_manager',
            executable='spawner',
            arguments=['joint_broad'],
            output='screen',
        )]
    )

    diff_drive_controller = TimerAction(
        period=8.0,
        actions=[Node(
            package='controller_manager',
            executable='spawner',
            arguments=['diff_cont'],
            output='screen',
        )]
    )

    return LaunchDescription([
        declare_world,
        gazebo,
        robot_state_publisher,
        spawn_robot,
        joint_state_broadcaster,
        diff_drive_controller,
    ])
