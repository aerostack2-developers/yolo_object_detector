from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration, EnvironmentVariable, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

import yaml, os

def get_yolo_params(context, *args, **kwargs):

    config = LaunchConfiguration('config').perform(context)
    tmp_filename = '/tmp/yolo_params.yaml'

    path_dict = {}
    with open(config, "r") as f:
        config_params = yaml.safe_load(f)
    try:
        path_dict = {   'config_path' : config_params["/**"]["ros__parameters"]["network"]['config'],
                        'weight_path' : config_params["/**"]["ros__parameters"]["network"]['weights'],
                        'class_name_path' : config_params["/**"]["ros__parameters"]["network"]['class_names']}
    except:
        raise Exception("Error in yolo_object_detector_launch.py: yolo_params.yaml is not properly formatted")

    for key, value in path_dict.items():
        if value is None:
            raise ValueError("No value found for {}".format(value))
        if not value.startswith('/'):
            print("Warning: {} is not an absolute path".format(value))
            path_dict[key] = os.path.join(os.path.dirname(config), value)

    with open( tmp_filename , 'w') as f:
        config_params["/**"]["ros__parameters"]["network"]['config'] = path_dict['config_path']
        config_params["/**"]["ros__parameters"]["network"]['weights'] = path_dict['weight_path']
        config_params["/**"]["ros__parameters"]["network"]['class_names'] = path_dict['class_name_path']
        yaml.dump(config_params, f)

    node = Node(
        package='openrobotics_darknet_ros',
        executable='detector_node',
        namespace=LaunchConfiguration('drone_id'),
        parameters=[tmp_filename],
        remappings=[('detector_node/images', 'sensor_measurements/front_camera')],
        output='screen',
        emulate_tty=True
    )

    return [node]


def generate_launch_description():
    config = PathJoinSubstitution([
        FindPackageShare('yolo_object_detector'),
        'config', 'darknet_params.yaml'
    ])

    ld = LaunchDescription([
        DeclareLaunchArgument('drone_id', default_value=EnvironmentVariable('AEROSTACK2_SIMULATION_DRONE_ID')),
        DeclareLaunchArgument('config', default_value=config),
        OpaqueFunction(function=get_yolo_params)
    ])

    return ld

