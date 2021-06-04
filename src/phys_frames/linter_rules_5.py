#Copyright 2021 Purdue University, University of Virginia.
#All rights reserved.


def get_sig_implication_rules():
    sig_pairs = [
        
    ]

    return sig_pairs


def get_name_implication_rules():
    name_pairs = [
        
    ]

    return name_pairs


def get_sig_null_disp_rules():
    null_sigs = {
        
    }

    return null_sigs


def get_name_null_disp_rules():
    null_names = {
        
    }

    return null_names


def get_sig_null_rot_rules():
    null_rot_sigs = {

        ('map','odom'),
        
        ('base_footprint','base_link'),
        
        ('world','map'),
        
        ('odom','map'),
        
        ('base_link','base_footprint'),
        
        ('base_link','laser'),
        
        ('link1_parent','link1'),
        
        ('map','odom_wheel'),
        
        ('base_link','base_stabilized'),
        
        ('base_stabilized','base_frame'),
        
        ('base_frame','nav'),
        
        ('odom_combined','base_footprint'),
        
        ('map','base_link'),
        
        ('base_frame','laser'),
        
        ('odom','base_footprint'),
        
        ('odom','base_link'),
        
        ('base_link','left_wheel_link'),
        
        ('base_link','right_wheel_link'),
        
        ('world','base'),
        
        ('base_link','anemometer_frame'),
        
        ('base_link','mox_frame'),
        
        ('map','anemometer_frame'),
        
        ('map','mox0_frame'),
        
        ('map','mox1_frame'),
        
        ('map','mox2_frame'),
        
        ('base_link','gps'),
        
        ('base_laser_link','laserscan'),
        
        ('world','lps'),
        
        ('world','odom_second'),
        
        ('world','stage_link'),
        
        ('map','world'),
        
        ('Astro/base_link','Astro/hokuyo_link'),
        
        ('base_link','pancake'),
        
        ('link_base','table'),
        
        ('pancake','table'),
        
        ('world','gps'),
        
        ('scan','camera_link'),
        
        ('base_link','base_laser'),
        
        ('odom_combined','root_link'),
        
        ('base_link_second','base_link_second_offset'),
        
        ('top_plate','velodyne'),
        
        ('world','gazebo_world'),
        
        ('world','odom_first'),
        
        ('scanmatcher_frame','base_link'),
        
        ('world','torso_base_link'),
        
        ('base_link','laser_scan'),
        
        ('base_link','odom'),
        
        ('base_link','fcu'),
        
        ('base_link','map'),
        
        ('world','odom'),
        
        ('base_link','zed_center'),
        
        ('top_plate','imu'),
        
        ('world','pelvis'),
        
        ('world','petit_map'),
        
        ('base_link','ar_marker_link'),
        
        ('world','poses'),
        
        ('zed_center','zed_right_camera'),
        
        ('zed_left_camera','zed_depth_camera'),
        
        ('odom_combined','base_link'),
        
        ('elikos_fcu','elikos_base_link'),
        
        ('ground_truth','odom'),
        
        ('base_footprint','laser_frame'),
        
        ('base_link','base_imu'),
        
        ('world_link','base_link'),
        
        ('base_link','base_gps'),
        
        ('map','base_footprint'),
        
        ('base_link','gps_link'),
        
        ('base_link','camera_depth_frame'),
        
        ('base_link_first','base_link_first_offset'),
        
        ('ee_link','camera_1_link'),
        
        ('ee_link','robotiq_85_adapter_link'),
        
        ('HEAD_RANGE','head_hokuyo_frame'),
        
        ('map','radar_frame'),
        
        ('radar_frame','camera_color_frame'),
        
        ('world','laser'),
        
        ('zed_center','zed_left_camera'),

    }

    return null_rot_sigs


def get_name_null_rot_rules():
    null_rot_names = {
        
        'offset_publisher',
        
        'map_broadcaster',
        
        'virtual_joint_broadcaster_0',
        
        'tf_footprint_base',
        
        'world2map',
        
        'base_link_to_laser',
        
        'anemometer_broadcaster',
        
        'base_2_nav_link',
        
        'base_link_2_base_stabilized_link',
        
        'base_stablized_2_base_frame',
        
        'map_odom_broadcaster',
        
        'base_link_to_left_wheel',
        
        'base_link_to_right_wheel',
        
        'footprint_broadcaster',
        
        'odom_to_rgbd_cam',
        
        'table_transform',
        
        'base_frame_2_laser_link',
        
        '',
        
        'odom_map_broadcaster',
        
        'stp_laser',
        
        'world_to_map',
        
        'top_plate_to_imu',
        
        'world_map_frame',
        
        'mox_broadcaster',
        
        'mox0_broadcaster',
        
        'mox1_broadcaster',
        
        'mox2_broadcaster',
        
        'stage_pose_broadcaster',
        
        'world_to_second',
        
        'fake_localization',
        
        'map_to_odom',
        
        'odom_2_base_footprint',
        
        'pancake_transform',
        
        'map_odom_tf',
        
        'map_2_odom',
        
        'world_base_broadcaster',
        
        'base_footprint_2_base_link',
        
        'scanmatch_to_base',
        
        'gps_2_world_broadcaster',
        
        'map_2_world_broadcaster',
        
        'per_slam_tf_1',
        
        'per_slam_tf_2',
        
        'table_tf_bc',
        
        'world_to_pelvis_tf_pub',
        
        'world',
        
        'base_link2laser_link2',
        
        'odom_to_map',
        
        'base_footprint_broadcaster',
        
        'base_to_laser_broadcaster',
        
        'map_tf',
        
        'top_plate_to_velodyne',
        
        'world_to_first',
        
        'base_footprint_to_base_link',
        
        'laser_scan_frame',
        
        'static_tf0',
        
        'laser_in_base_link',
        
        'laser_link',
        
        'static_tf',
        
        'base_link_footprint_tf',
        
        'link_nav_broadcaster',
        
        'link0_broadcaster',
        
        'tf_publisher_gps',
        
        'world_link_broadcaster',
        
        'base_link2laser_link',
        
        'base_link_to_imu_frame',
        
        'base_to_xtion_broadcaster',
        
        'base2camera',
        
        'dummy_tf_publisher',
        
        'localization',
        
        'map_world_tf',
        
        'per_zed_1',
        
        'per_zed_2',
        
        'per_zed_3',
        
        'static_marker_link_publisher',
        
        'static_Publisher',
        
        'world_to_arm_base',
        
        'map_to_base_broadcaster',
        
        'static_tf_pub_world_to_gazebo_world',
        
        'base_to_world',
        
        'base_link_broadcaster',
        
        'footprint_static_tf',
        
        'velodyne_broadcaster',
        
        'world2petit_broadcaster',
        
        'base_footprint2base_link',
        
        'static_tf_map_to_base_radar_link',
        
        'ee_to_robotiq_c',
        
        'ee_to_wrist_camera',
        
        'gmapping_link_publisher',
        
        'gps_broadcaster',
        
        'map_base_broadcaster',
        
        'base_link_tf',
        
        'camera_imu_tf',
        
        'fixed_frame_pos_pub_arm',
        
        'head_range_frame_id',
        
        'radar_tf',
        
        'radar_to_camera_tf',
        
        'world_map',

    }

    return null_rot_names



