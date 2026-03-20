from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, EnvironmentVariable
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    pkg_name = 'waver_description'
    pkg_path = get_package_share_directory(pkg_name)

    xacro_file = os.path.join(pkg_path, 'urdf', 'waver.xacro')
    world_file = os.path.join(pkg_path, 'worlds', 'empty.world')
    ros_gz_sim_pkg = get_package_share_directory('ros_gz_sim')

    # 핵심: GZ Sim이 model://waver_description/... 및 package mesh를 찾도록 resource path 추가
    gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=[
            EnvironmentVariable('GZ_SIM_RESOURCE_PATH', default_value=''),
            ':',
            os.path.dirname(pkg_path),   # .../install/waver_description/share
            ':',
            pkg_path                     # .../install/waver_description/share/waver_description
        ]
    )

    ign_resource_path = SetEnvironmentVariable(
        name='IGN_GAZEBO_RESOURCE_PATH',
        value=[
            EnvironmentVariable('IGN_GAZEBO_RESOURCE_PATH', default_value=''),
            ':',
            os.path.dirname(pkg_path),
            ':',
            pkg_path
        ]
    )

    robot_description = Command([
        'xacro ',
        xacro_file,
        ' sim_control:=gz',
        ' camera_type:=raspi'
    ])

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_pkg, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': ['-r ', world_file]
        }.items()
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True
        }]
    )

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        name='spawn_waver',
        output='screen',
        arguments=[
            '-name', 'waver',
            '-topic', 'robot_description',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.15'
        ]
    )

    return LaunchDescription([
        gz_resource_path,
        ign_resource_path,
        gz_sim,
        robot_state_publisher,
        TimerAction(period=2.0, actions=[spawn_robot]),
    ])
