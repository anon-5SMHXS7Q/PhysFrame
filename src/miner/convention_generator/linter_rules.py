
def get_sig_implication_rules():
    sig_pairs = [
        
        (('base_link','base_stabilized'),('base_frame','nav')),
        
        (('base_stabilized','base_frame'),('base_frame','nav')),
        
        (('base_stabilized','base_frame'),('base_link','base_stabilized')),
        
        (('base_link','base_stabilized'),('base_stabilized','base_frame')),
        
        (('base_frame','nav'),('base_link','base_stabilized')),
        
        (('base_frame','nav'),('base_stabilized','base_frame')),
        
        (('base_link','right_wheel_link'),('base_link','left_wheel_link')),
        
        (('base_link','left_wheel_link'),('base_link','right_wheel_link')),
        
        (('base_link','velodyne_i'),('base_link','velodyne_d')),
        
        (('base_link','velodyne_d'),('base_link','velodyne_i')),
        
        (('sandwich_center','front_link'),('sandwich_center','back_link')),
        
        (('sandwich_center','back_link'),('sandwich_center','front_link')),
        
        (('base_link','camera2_link'),('base_link','camera1_link')),
        
        (('base_link','camera1_link'),('base_link','camera2_link')),
        
        (('camera_rotated','world'),('camera_link','camera_rotated')),
        
        (('camera_link','camera_rotated'),('camera_rotated','world')),
        
        (('sandwich_center','up_link'),('sandwich_center','back_link')),
        
        (('sandwich_center','up_link'),('sandwich_center','front_link')),
        
        (('base_laser_link','laserscan'),('world','map')),
        
        (('head','camera_link'),('base_footprint','base_link')),
        
        (('base_frame','laser_rear'),('base_frame','laser')),
        
        (('ee_link','camera_1_link'),('world','base_link')),
        
        (('ee_link','robotiq_85_adapter_link'),('world','base_link')),
        
        (('base_frame','laser_rear'),('base_frame','nav')),
        
        (('base_frame','laser_rear'),('base_link','base_stabilized')),
        
        (('base_frame','laser_rear'),('base_stabilized','base_frame')),
        
        (('elikos_arena_origin','elikos_local_origin'),('elikos_fcu','elikos_base_link')),
        
        (('map','robot_2/odom'),('map','robot_1/odom')),
        
        (('base_link_second','base_link_second_offset'),('base_link_first','base_link_first_offset')),
        
        (('base_link_first','base_link_first_offset'),('base_link_second','base_link_second_offset')),
        
        (('ee_link','robotiq_85_adapter_link'),('ee_link','camera_1_link')),
        
        (('ee_link','camera_1_link'),('ee_link','robotiq_85_adapter_link')),
        
        (('world','odom_second'),('world','odom_first')),
        
        (('world','odom_first'),('world','odom_second')),
        
        (('scan','camera_link'),('base_link','imu')),
        
        (('base_frame','merged_lrf'),('base_frame','laser')),
        
        (('base_frame','merged_lrf'),('base_frame','nav')),
        
        (('base_frame','merged_lrf'),('base_link','base_stabilized')),
        
        (('base_frame','merged_lrf'),('base_stabilized','base_frame')),
        
        (('scan','camera_link'),('base_link','scan')),
        
        (('camera_link','camera_depth_frame'),('camera_link','camera_rgb_frame')),
        
        (('map','robot_3/odom'),('map','robot_1/odom')),
        
        (('openni_depth_frame','openni_depth_optical_frame'),('openni_camera','openni_depth_frame')),
        
        (('openni_rgb_frame','openni_rgb_optical_frame'),('openni_camera','openni_depth_frame')),
        
        (('map','robot_3/odom'),('map','robot_2/odom')),
        
        (('right_camera_link','right_camera_optical_frame'),('left_camera_link','left_camera_optical_frame')),
        
        (('left_camera_link','left_camera_optical_frame'),('right_camera_link','right_camera_optical_frame')),
        
        (('map','headCamera'),('world','map')),
        
        (('base_link','top_link'),('base_link','base_footprint')),
        
        (('base_frame','camera_link'),('base_footprint','base_link')),
        
        (('base_frame','camera_link'),('base_frame','nav')),
        
        (('base_frame','camera_link'),('base_link','base_stabilized')),
        
        (('base_frame','camera_link'),('base_stabilized','base_frame')),
        
        (('base_frame','camera_link'),('map','base_footprint')),
        
        (('base_link','top_link'),('base_link','fcu')),
        
        (('elikos_base_link','r200'),('elikos_base_link','elikos_ffmv_bottom')),
        
        (('openni_camera','openni_rgb_frame'),('openni_camera','openni_depth_frame')),
        
        (('top_plate','imu'),('top_plate','velodyne')),
        
        (('openni_camera','openni_rgb_frame'),('openni_depth_frame','openni_depth_optical_frame')),
        
        (('openni_camera','openni_rgb_frame'),('openni_rgb_frame','openni_rgb_optical_frame')),
        
        (('base_link','wheel_right_link'),('base_link','wheel_left_link')),
        
        (('base_link','wheel_left_link'),('base_link','wheel_right_link')),
        
        (('world','robot_1/odom'),('world','robot_0/odom')),
        
        (('world','robot_0/odom'),('world','robot_1/odom')),
        
    ]

    return sig_pairs


def get_name_implication_rules():
    name_pairs = [
        
        ('base_link_2_base_stabilized_link','base_2_nav_link'),
        
        ('base_stablized_2_base_frame','base_2_nav_link'),
        
        ('base_2_nav_link','base_link_2_base_stabilized_link'),
        
        ('base_stablized_2_base_frame','base_link_2_base_stabilized_link'),
        
        ('base_2_nav_link','base_stablized_2_base_frame'),
        
        ('base_link_2_base_stabilized_link','base_stablized_2_base_frame'),
        
        ('base_2_nav_link','base_frame_2_laser_link'),
        
        ('base_link_2_base_stabilized_link','base_frame_2_laser_link'),
        
        ('base_stablized_2_base_frame','base_frame_2_laser_link'),
        
        ('link2_broadcaster','link1_broadcaster'),
        
        ('base_footprint_2_base_link','base_2_nav_link'),
        
        ('base_footprint_2_base_link','base_link_2_base_stabilized_link'),
        
        ('base_footprint_2_base_link','base_stablized_2_base_frame'),
        
        ('odom_2_base_footprint','base_2_nav_link'),
        
        ('odom_2_base_footprint','base_link_2_base_stabilized_link'),
        
        ('odom_2_base_footprint','base_stablized_2_base_frame'),
        
        ('odom_2_base_footprint','base_footprint_2_base_link'),
        
        ('odom_2_base_footprint','map_2_odom'),
        
        ('base_link_to_right_wheel','base_link_to_left_wheel'),
        
        ('base_link_to_left_wheel','base_link_to_right_wheel'),
        
        ('odom_right_wheel_broadcaster','odom_left_wheel_broadcaster'),
        
        ('odom_left_wheel_broadcaster','odom_right_wheel_broadcaster'),
        
        ('odom_to_rgbd_cam','base_link_to_left_wheel'),
        
        ('odom_to_rgbd_cam','base_link_to_right_wheel'),
        
        ('tf_front','tf_back'),
        
        ('tf_back','tf_front'),
        
        ('scanmatch_to_base','base_link_to_laser'),
        
        ('link4_broadcaster','link1_broadcaster'),
        
        ('link4_broadcaster','link2_broadcaster'),
        
        ('map_2_base_footprint','base_frame_2_laser_link'),
        
        ('map_2_base_footprint','base_2_nav_link'),
        
        ('map_2_base_footprint','base_link_2_base_stabilized_link'),
        
        ('map_2_base_footprint','base_stablized_2_base_frame'),
        
        ('map_2_base_footprint','base_footprint_2_base_link'),
        
        ('link4_broadcaster','link3_broadcaster'),
        
        ('world_map_frame','world_laser_frame'),
        
        ('world_laser_frame','world_map_frame'),
        
        ('tf1','tf2'),
        
        ('tf_up','tf_back'),
        
        ('tf_up','tf_front'),
        
        ('base_to_camera2_tf','base_to_camera1_tf'),
        
        ('base_to_camera1_tf','base_to_camera2_tf'),
        
        ('link3_broadcaster','link2_broadcaster'),
        
        ('kinect_base_link2','kinect_base_link'),
        
        ('laser_scan_frame','world_laser_frame'),
        
        ('laser_scan_frame','world_map_frame'),
        
        ('base_frame_2_laser_rear_link','base_frame_2_laser_link'),
        
        ('base_frame_2_laser_rear_link','base_2_nav_link'),
        
        ('base_frame_2_laser_rear_link','base_link_2_base_stabilized_link'),
        
        ('base_frame_2_laser_rear_link','base_stablized_2_base_frame'),
        
        ('ee_to_robotiq_c','world_to_base_link'),
        
        ('ee_to_wrist_camera','world_to_base_link'),
        
        ('world_to_first','offset_publisher'),
        
        ('world_to_second','offset_publisher'),
        
        ('arm_quad','camera_quad'),
        
        ('depth_camera','link'),
        
        ('ee_to_wrist_camera','ee_to_robotiq_c'),
        
        ('ee_to_robotiq_c','ee_to_wrist_camera'),
        
        ('world_to_second','world_to_first'),
        
        ('world_to_first','world_to_second'),
        
        ('base_frame_2_laser_marged_link','base_frame_2_laser_link'),
        
        ('base_frame_2_laser_marged_link','base_2_nav_link'),
        
        ('base_frame_2_laser_marged_link','base_link_2_base_stabilized_link'),
        
        ('base_frame_2_laser_marged_link','base_stablized_2_base_frame'),
        
        ('base_link2laser_link2','base_link2laser_link'),
        
        ('tf3','tf2'),
        
        ('base_link2laser_link2','base_link2imu'),
        
        ('kinect_base_link1','kinect_base_link'),
        
        ('kinect_base_link1','kinect_base_link2'),
        
        ('lcamera_frame_bdcst','rcamera_frame_bdcst'),
        
        ('kinect_base_link1','kinect_base_link3'),
        
        ('base_link_2_base_frame','laser_2_base_link'),
        
        ('top_plate_to_imu','top_plate_to_velodyne'),
        
        ('base_footprint_2_base_link','base_frame_2_laser_link'),
        
        ('link0_broadcaster','link1_broadcaster'),
        
        ('link5_broadcaster','link1_broadcaster'),
        
        ('tf_scan_base','tf_footprint_base'),
        
        ('tf_top_link','tf_footprint_base'),
        
        ('base_to_fcu_broadcaster','tf_footprint_base'),
        
        ('link0_broadcaster','link2_broadcaster'),
        
        ('link5_broadcaster','link2_broadcaster'),
        
        ('r200_broadcaster','camera_broadcaster'),
        
        ('r200_broadcaster','baselink_broadcaster'),
        
        ('link5_broadcaster','link3_broadcaster'),
        
        ('link5_broadcaster','link4_broadcaster'),
        
        ('pancake_transform','table_transform'),
        
        ('map_to_odom_tf','odom_to_base_tf'),
        
        ('base_link_to_wheel_right_link','base_link_to_wheel_left_link'),
        
        ('base_link_to_wheel_left_link','base_link_to_wheel_right_link'),
        
        ('tf_top_link','base_to_fcu_broadcaster'),
        
        ('base_to_fcu_broadcaster','tf_top_link'),
        
        ('world_vive_to_operator_origin','vive_sn_to_head'),
        
        ('world_odom1_link','world_odom0_link'),
        
        ('world_odom0_link','world_odom1_link'),
        
        ('vive_sn_to_head','world_vive_to_operator_origin'),
        
    ]

    return name_pairs


def get_sig_null_disp_rules():
    null_sigs = {
        
        ('kinect_link','kinect_depth_frame'),
        
        ('base_frame','base_link'),
        
        ('world','vision_world'),
        
        ('laser','camera_link'),
        
        ('openni_depth_frame','openni_depth_optical_frame'),
        
        ('openni_rgb_frame','openni_rgb_optical_frame'),
        
        ('base_laser_front_link','laser'),
        
        ('world','vicon'),
        
        ('camera_link','openni_depth_frame'),
        
        ('scanmatcher_frame','base_footprint'),
        
    }

    return null_sigs


def get_name_null_disp_rules():
    null_names = {
        
        'world_to_map_broadcaster',
        
        'base_frame_laser',
        
        'world_to_usb_cam',
        
        'baselink_laser_broadcaster',
        
        'base_link_2_base_frame',
        
        'realsense2_camera_manager',
        
        'odom_to_base_link',
        
        'static_transform',
        
        'world_laser_frame_frame',
        
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
        
        ('base_link','imu_link'),
        
        ('map','base_radar_link'),
        
        ('base_link','base_scan'),
        
        ('base_link','centerlaser'),
        
        ('base_link_second','base_link_laser_second'),
        
        ('base_footprint','velodyne'),
        
        ('amcl_frame','base_link'),
        
        ('base_footprint','any_frame'),
        
        ('base_footprint','base_laser'),
        
        ('base_footprint','gyro_link'),
        
        ('base_frame','usb_cam'),
        
        ('base_link','axle'),
        
        ('base_link','base_christa'),
        
        ('base_link','compass'),
        
        ('base_link','front_axel_link'),
        
        ('base_link','gps0_link'),
        
        ('base_link','velodyne_link'),
        
        ('camera','depth'),
        
        ('camera_link','2d_blue'),
        
        ('camera_rgb_optical_frame','map'),
        
        ('chassis','base_laser'),
        
        ('dummy_link','camera_link'),
        
        ('end_effector','end_effector_edge'),
        
        ('far_field','origin'),
        
        ('map','camera_odom_frame'),
        
        ('map','map_origin'),
        
        ('odom','imu_link'),
        
        ('odom_frame','odom'),
        
        ('robot_1/map','robot_2/map'),
        
        ('world','laser_cube1'),
        
        ('world','laser_cube2'),
        
        ('world','neato_laser'),
        
        ('world_link','map'),
        
        ('world_local','world'),
        
        ('base_link','lidar'),
        
        ('base_link','top_link'),
        
        ('base_link','wheel_left_link'),
        
        ('base_link','wheel_right_link'),
        
        ('base_link','scan'),
        
        ('map','odom_combined'),
        
        ('map','my_frame'),
        
        ('world','base_link'),
        
        ('base_link','hokuyo_link'),
        
        ('elikos_arena_origin','elikos_local_origin'),
        
        ('odom','odom_combined'),
        
        ('base_link','velodyne'),
        
        ('base_footprint_first','base_link_first_offset'),
        
        ('base_footprint_second','base_link_second_offset'),
        
        ('base_laser','base_footprint'),
        
        ('base_link','table'),
        
        ('base_link','wheel_rr'),
        
        ('fixed','sr_arm/position/world'),
        
        ('LARM_LINK7','LARM_WRIST_P'),
        
        ('left_wrist','left_gripper_center'),
        
        ('LLEG_LINK6','LLEG_ANKLE_R'),
        
        ('map','environment/base_link'),
        
        ('map','robot_1/map'),
        
        ('RARM_LINK7','RARM_WRIST_P'),
        
        ('right_wrist','right_gripper_center'),
        
        ('RLEG_LINK6','RLEG_ANKLE_R'),
        
        ('WAIST_LINK0','gyrometer'),
        
        ('world','robot_2/odom'),
        
        ('world','world_marker'),
        
        ('world','world_visual1'),
        
        ('world','world_visual2'),
        
        ('world','world_visual3'),
        
        ('world','world_visual4'),
        
        ('world','world_visual5'),
        
        ('world','world_visual6'),
        
        ('zed_camera_center','base_link'),
        
        ('zed_camera_center','laser_base'),
        
        ('base_link','pan_base'),
        
        ('base_link','camera_depth_frame_notilt'),
        
        ('map','iai_kitchen/world'),
        
        ('camera_link','camera_rgb_frame'),
        
        ('base_footprint','camera_link'),
        
        ('\/base_link','\/camera_link'),
        
        ('base_link','arm_base'),
        
        ('camera_link','zed_center'),
        
        ('head_link','head_lidar_actuator_frame'),
        
        ('laser_link','camera_depth_frame'),
        
        ('link_6','vicon_tip'),
        
        ('map','robot_0/map'),
        
        ('odom','footprint'),
        
        ('world','torso_roll_link'),
        
        ('base_footprint','laser'),
        
        ('base_footprint','mobile_base'),
        
        ('base_laser_link','laser_front'),
        
        ('base_link','sick_laser_link'),
        
        ('base_link_first','base_link_laser_first'),
        
        ('car_link','velodyne'),
        
        ('estimate/local_cs','estimate_prior/local_cs'),
        
        ('estimate/local_cs','local_cs'),
        
        ('footprint','base_imu_link'),
        
        ('footprint','laser'),
        
        ('footprint','zed_initial_frame'),
        
        ('world_frame','task_frame'),
        
        ('base_footprint','imu_link'),
        
        ('world','leap_motion'),
        
        ('world','robot_0/odom'),
        
        ('world','robot_1/odom'),
        
        ('camera_link','camera_depth_frame'),
        
        ('world','panda_link0'),
        
        ('1','map'),
        
        ('a','b'),
        
        ('base','kinematic_sim/base'),
        
        ('base','new'),
        
        ('base_footprint','base_left_cam'),
        
        ('base_footprint','BODY'),
        
        ('base_footprint','octomap_world'),
        
        ('base_footprint','table'),
        
        ('base_footprint','WAIST'),
        
        ('base_frame','lidar'),
        
        ('base_laser','laser_+000_DIST1'),
        
        ('base_link','axle_front_wheel'),
        
        ('base_link','axle_mid_wheel'),
        
        ('base_link','axle_rear_wheel'),
        
        ('base_link','baker'),
        
        ('base_link','base_decawave_t0'),
        
        ('base_link','base_laser_link0'),
        
        ('base_link','camera_base_link'),
        
        ('base_link','denso_arm/base'),
        
        ('base_link','ego_vehicle/camera/rgb/front'),
        
        ('base_link','ego_vehicle/gnss/gnss1'),
        
        ('base_link','ego_vehicle/lidar/lidar1'),
        
        ('base_link','front_left_cliff'),
        
        ('base_link','front_left_sonar'),
        
        ('base_link','front_right_cliff'),
        
        ('base_link','front_right_sonar'),
        
        ('base_link','frontLeftSonar'),
        
        ('base_link','frontRightSonar'),
        
        ('base_link','hokuyo_frame'),
        
        ('base_link','hokuyo_front_laser_tilt_support_link'),
        
        ('base_link','imu_mpu_9150_link'),
        
        ('base_link','imu_um7_link'),
        
        ('base_link','katana_base_link'),
        
        ('base_link','laser_filt'),
        
        ('base_link','left_caster_wheel'),
        
        ('base_link','left_drive_wheel'),
        
        ('base_link','left_wheel'),
        
        ('base_link','left_wheel_frame'),
        
        ('base_link','link1'),
        
        ('base_link','link2'),
        
        ('base_link','link3'),
        
        ('base_link','link4'),
        
        ('base_link','link5'),
        
        ('base_link','link6'),
        
        ('base_link','link7'),
        
        ('base_link','LLA'),
        
        ('base_link','navsat'),
        
        ('base_link','neato'),
        
        ('base_link','p3dx/odom'),
        
        ('base_link','previewer/base_link'),
        
        ('base_link','radar_mount'),
        
        ('base_link','right_caster_wheel'),
        
        ('base_link','right_drive_wheel'),
        
        ('base_link','right_wheel'),
        
        ('base_link','right_wheel_frame'),
        
        ('base_link','robot/lidar_link'),
        
        ('base_link','rs_link'),
        
        ('base_link','support_bottom_link'),
        
        ('base_link','sw_arm_left_1'),
        
        ('base_link','sw_arm_right_1'),
        
        ('base_link','tof'),
        
        ('base_link','torso_fixed_link'),
        
        ('base_link','velo_link'),
        
        ('base_link','velodyne_left'),
        
        ('base_link','velodyne_right'),
        
        ('base_link','wheel_back_left_link'),
        
        ('base_link','wheel_back_right_link'),
        
        ('base_link','wheel_front_left_link'),
        
        ('base_link','wheel_front_right_link'),
        
        ('camera','camera_rgb_optical_frame'),
        
        ('camera_link','zed_actual_frame'),
        
        ('camera_link_support_axis','camera_link'),
        
        ('camera_pose_frame','3dm_gx5_15'),
        
        ('camera_pose_frame','base_radar_link'),
        
        ('camera_pose_frame','imu_link'),
        
        ('camera_pose_frame','laser'),
        
        ('catvehicle/base_link','velodyne'),
        
        ('catvehicle/front_laser_link','laser'),
        
        ('cube_cloud','world'),
        
        ('depth','color'),
        
        ('drone','laser'),
        
        ('drone/base_link','ardrone_base_link'),
        
        ('drone/odom','odom'),
        
        ('dummy_cam','camera_link'),
        
        ('dummy_link','zed_left_camera_frame'),
        
        ('ee_link','endpoint'),
        
        ('elikos_arena_origin','elikos_setpoint'),
        
        ('eng2/7f','map'),
        
        ('floor','my_frame'),
        
        ('gps_wamv_link','wamv/gps_wamv_link'),
        
        ('ground_truth//ground_truth/odometry_sensorgt_link','base_link'),
        
        ('head','kinect_link_phys'),
        
        ('head_camera_link','head_camera_depth_frame'),
        
        ('head_camera_link','head_camera_rgb_frame'),
        
        ('head_tilt_link','head_camera_link'),
        
        ('hebi_mount','world'),
        
        ('hokuyo_link','laser'),
        
        ('imu_link','3dm_gx5_15'),
        
        ('imu_link','base_imu_link'),
        
        ('imu_link','base_link'),
        
        ('imu_link','base_radar_link'),
        
        ('imu_link','imu_joint'),
        
        ('imu_wamv_link','wamv/imu_wamv_link'),
        
        ('inside_camera','inside_camera_inside_fiducial'),
        
        ('inside_camera','inside_camera_outside_fiducial'),
        
        ('iris/xtion_sensor/ground_truth/iris/xtion_sensor/ground_truth/odometry_sensor_link','base_link'),
        
        ('kinect_front_link','openni_depth_frame'),
        
        ('kinect_rgb_optical_frame','arm_base_link'),
        
        ('l_gripper_tool_frame','pancake_bottle'),
        
        ('laser','laser_front'),
        
        ('left_gripper','suction_cup'),
        
        ('lidar_wamv_link','wamv/lidar_wamv_link'),
        
        ('lidar/scan','turtlebot2i/lidar/scan'),
        
        ('link_6','cross_tip'),
        
        ('map','base_imu_link'),
        
        ('map','bbc_camera_link'),
        
        ('map','bottom_link'),
        
        ('map','celoxia_base_link'),
        
        ('map','data'),
        
        ('map','dum_c605'),
        
        ('map','entry_laser_base'),
        
        ('map','fixed_map'),
        
        ('map','force_sensor'),
        
        ('map','humans_frame'),
        
        ('map','marker1'),
        
        ('map','measurements_debug'),
        
        ('map','overhead1'),
        
        ('map','p3dx/odom'),
        
        ('map','person1_head'),
        
        ('map','person1_torso'),
        
        ('map','person2_head'),
        
        ('map','person2_torso'),
        
        ('map','person3_head'),
        
        ('map','person3_torso'),
        
        ('map','ptu_base_link'),
        
        ('map','shelf_base'),
        
        ('map','slam_map'),
        
        ('map','STEVE0/map'),
        
        ('map','table'),
        
        ('map','table_link'),
        
        ('map','track_start'),
        
        ('map','UGV/odom'),
        
        ('map','uwb'),
        
        ('map','wheelodom'),
        
        ('map0','map'),
        
        ('mocap_world','odom_combined'),
        
        ('nav','navsat'),
        
        ('not_rot_baselink','not_rot_velodyne'),
        
        ('odom','gps'),
        
        ('odom','imu'),
        
        ('odom','launch'),
        
        ('odom','local_origin'),
        
        ('odom','odom_comb_out'),
        
        ('odom','table'),
        
        ('odom','vehicle'),
        
        ('odom_combined','base_linkq'),
        
        ('odom_combined','goal_area'),
        
        ('odom_combined','map'),
        
        ('odom_combined','pelvis'),
        
        ('odom_left','left_sole_link'),
        
        ('odom_right','right_sole_link'),
        
        ('openni_rgb_frame','openni_camera'),
        
        ('optitrack_base/base_link','base_link'),
        
        ('oriented_optimization_frame','optimization_frame'),
        
        ('pelvis','vehicle_frame'),
        
        ('Pioneer3AT/odom','obstacle/left_corner'),
        
        ('Pioneer3AT/odom','obstacle/left_up_corner'),
        
        ('Pioneer3AT/odom','obstacle/middle'),
        
        ('Pioneer3AT/odom','obstacle/right_corner'),
        
        ('Pioneer3AT/odom','obstacle/right_up_corner'),
        
        ('quadrotor','base_link'),
        
        ('right_gripper','calib_frame'),
        
        ('robot','lidar'),
        
        ('robot_0/odom','Larry/base_footprint'),
        
        ('robot_1/map','robot_3/map'),
        
        ('rotation_link','scanner_link'),
        
        ('rs_link','rs_camera_link'),
        
        ('rs_odom','rs_odom_frame'),
        
        ('rtabmap/grid_map','map'),
        
        ('scanmatcher_frame','firefly/base_link'),
        
        ('support_bottom_link','support_top_link'),
        
        ('T0','kinect_front_link'),
        
        ('table','pancake_maker'),
        
        ('table','plate'),
        
        ('tb','base_link'),
        
        ('ti_mmwave','ti_mmwave/point_cloud'),
        
        ('ti_mmwave_pcl','ti_mmwave_0'),
        
        ('ti_mmwave_pcl','ti_mmwave_1'),
        
        ('tilt_bracket','gun'),
        
        ('tilt_bracket_forward','gun_forward'),
        
        ('torso_lift_link','bellows_link2'),
        
        ('torso_lift_link','pancake'),
        
        ('turtlebot2i/base_footprint','base_footprint'),
        
        ('velvet_fingers_palm','camera_depth_frame'),
        
        ('vicon','odom'),
        
        ('WaistYaw_Link','odom'),
        
        ('world','arm1'),
        
        ('world','arm2'),
        
        ('world','ball'),
        
        ('world','cc_move_torso_up'),
        
        ('world','cc_order_tequila_sunrise'),
        
        ('world','cc_pause'),
        
        ('world','cf_q'),
        
        ('world','fcu'),
        
        ('world','gantry'),
        
        ('world','gate1'),
        
        ('world','gate2'),
        
        ('world','imu_link'),
        
        ('world','left_drive_wheel_link'),
        
        ('world','lidar'),
        
        ('world','light'),
        
        ('world','odom_frame'),
        
        ('world','odom_frame_est'),
        
        ('world','odom_gt_frame'),
        
        ('world','omni/base'),
        
        ('world','peg1'),
        
        ('world','peg2'),
        
        ('world','Qualisys'),
        
        ('world','right_drive_wheel_link'),
        
        ('world','ring1'),
        
        ('world','robot_frame'),
        
        ('world','robot4'),
        
        ('world','sr_arm/position/world'),
        
        ('world','table_map'),
        
        ('world','tsdf_origin'),
        
        ('world','walker_base'),
        
        ('world','world/tags_base'),
        
        ('world_joint','world'),
        
        ('wrist_roll_link','gripper_link'),
        
        ('xiroi','xiroi/gps'),
        
        ('xiroi','xiroi/usbl'),
        
        ('yumi_metal_bottom_r','yumi_dlsr_r'),
        
        ('zed_rgb_optical_frame','zed_depth_optical_frame'),
        
        ('zed0/zed_center','zed0/zed_left_camera'),
        
        ('base_link','neato_laser'),
        
        ('camera_rotated','world'),
        
        ('odom','BODY'),
        
        ('sandwich_center','front_link'),
        
        ('base_link','imu_frame'),
        
        ('map','lisa'),
        
        ('ar_marker_0','base_link'),
        
        ('base','MAV'),
        
        ('base','trep_world'),
        
        ('base_footprint','base_laser_link'),
        
        ('base_footprint','base_odometry'),
        
        ('base_footprint','base_sensors'),
        
        ('base_footprint','scantf'),
        
        ('base_link','base_link2'),
        
        ('base_link','base_range'),
        
        ('base_link','front_sonar_link'),
        
        ('base_link','head_cam3d_link'),
        
        ('base_link','ir_center'),
        
        ('base_link','left_center_drive_wheel'),
        
        ('base_link','left_front_drive_wheel'),
        
        ('base_link','left_rear_drive_wheel'),
        
        ('base_link','os1'),
        
        ('base_link','right_center_drive_wheel'),
        
        ('base_link','right_front_drive_wheel'),
        
        ('base_link','right_rear_drive_wheel'),
        
        ('base_link','road_markings'),
        
        ('base_link','rockin_marker'),
        
        ('base_link','s4'),
        
        ('base_link','xtion'),
        
        ('base_odometry','imu_link'),
        
        ('bender/odom','bender/base_link'),
        
        ('BUMBLEBEE_LEFT_REAL','BUMBLEBEE_LEFT'),
        
        ('c3po_marker_top','c3po_base_link'),
        
        ('calib_right_arm_base_link','world_frame'),
        
        ('camera','camera_frame'),
        
        ('Camera','PlateImage'),
        
        ('camera_link','ackermann_vehicle_13/camera_link'),
        
        ('camera_rgb_frame','right_realsense'),
        
        ('CHEST_LINK1','gyrometer'),
        
        ('drone','base_link'),
        
        ('ee_link','tcp_link'),
        
        ('elikos_arena_origin','elikos_base_link'),
        
        ('elikos_local_origin','elikos_arena_origin'),
        
        ('headCamera','base_footprint'),
        
        ('hokuyo_front_laser_tilt_support_link','hokuyo_front_laser_tilt_axis_link'),
        
        ('hokuyo_link','ackermann_vehicle_13/hokuyo_link'),
        
        ('kingfisher/base','kingfisher/axis'),
        
        ('kingfisher/base','kingfisher/gps'),
        
        ('kingfisher/base','kingfisher/hazcam'),
        
        ('LARM_LINK6','lhsensor'),
        
        ('lidar_link','laser'),
        
        ('LLEG_LINK5','lfsensor'),
        
        ('local_origin','world'),
        
        ('map','basestation'),
        
        ('map','deckard/odom'),
        
        ('map','duckiebot_link'),
        
        ('map','laser_frame'),
        
        ('map','nav_origin'),
        
        ('map','pris/odom'),
        
        ('map','robot1_tf/odom'),
        
        ('map','RosAria/odom'),
        
        ('map','roy/odom'),
        
        ('map','tracer/odom'),
        
        ('map','turtlebot2i/odom'),
        
        ('map','Zed_sim/odom'),
        
        ('map','zhora/odom'),
        
        ('mico_mount','camera_mount'),
        
        ('mico_mount','mico'),
        
        ('odom','laser'),
        
        ('odom','rel_odom'),
        
        ('odom','zed_initial_frame'),
        
        ('openni_camera','camera_link'),
        
        ('pancake_maker','pancake'),
        
        ('Parrot_base','imu'),
        
        ('r2d2_marker_top','r2d2_base_link'),
        
        ('RARM_LINK6','rhsensor'),
        
        ('rel_odom','rel_c3po/odom'),
        
        ('rel_odom','rel_r2d2/odom'),
        
        ('RLEG_LINK5','rfsensor'),
        
        ('robot_locked','world'),
        
        ('root','ldmrs0'),
        
        ('root','ldmrs1'),
        
        ('root','ldmrs2'),
        
        ('root','ldmrs3'),
        
        ('stereo','left'),
        
        ('stereo','right'),
        
        ('stereo_forward','left_optical'),
        
        ('table','mico_mount'),
        
        ('velodyne','front_laser'),
        
        ('vicon_global_frame','world'),
        
        ('volume_pose','map'),
        
        ('world','bumblebee2/left'),
        
        ('world','camera/capture0'),
        
        ('world','hydra_base'),
        
        ('world','phantom_base_link'),
        
        ('world','root'),
        
        ('world','scanner'),
        
        ('world','something'),
        
        ('world','ur5_1/world'),
        
        ('world','ur5_2/world'),
        
        ('xtion','laser'),
        
        ('yumi_body','leap_optical_frame'),
        
        ('base_link','openni_camera'),
        
        ('base_link','laser_link'),
        
        ('base','human/base'),
        
        ('base_link','3dm_gx5_15'),
        
        ('base_link','base'),
        
        ('base_link','laser_virtual'),
        
        ('Body_PS_Mount','Body_PS2'),
        
        ('camera_color_optical_frame','lines_link'),
        
        ('camera_link','Base'),
        
        ('earth','utm'),
        
        ('HEAD_LEFT_CAMERA','head_root'),
        
        ('map','laser'),
        
        ('map_nav','map'),
        
        ('map_nav','path'),
        
        ('my_frame','map'),
        
        ('odom','map_nav'),
        
        ('odom','t265_odom_frame'),
        
        ('odom','WAIST_LINK0'),
        
        ('odom_combined','cylinder'),
        
        ('ohm_base_link','laser'),
        
        ('robot_0/odom','robot_1/odom'),
        
        ('stereo_camera','left_optical'),
        
        ('user_rail_link','camera_link'),
        
        ('world','body'),
        
        ('world','conveyer'),
        
        ('world','link0'),
        
        ('world','mocap_origin'),
        
        ('world_frame','base_link'),
        
        ('world_utm','world_local'),
        
        ('map','nav'),
        
        ('base_link','base_laser1_link'),
        
        ('base_link','sonar_front'),
        
        ('camera_link','d435_link'),
        
        ('head','kinect_link'),
        
        ('kinect_rgb','kinect_depth'),
        
        ('map','desired_trajec'),
        
        ('map','mobility'),
        
        ('reference_frame','world'),
        
        ('robot_center','base_link'),
        
        ('robot_center','hokuyo_frame'),
        
        ('vi_sensor/camera_depth_optical_center_link','sensor'),
        
        ('world','elikos_arena_origin'),
        
        ('world','test'),
        
        ('world_link','smartpal5_link'),
        
        ('youbot/base_link','youbot/base_laser_front_link'),
        
        ('map','head_rgbd_sensor_rgb_frame'),
        
        ('openni_camera','openni_depth_frame'),
        
        ('base_link','axis/image_raw/compressed'),
        
        ('base_link','phone'),
        
        ('base_link','sonar_frame'),
        
        ('camera_depth_frame','openni_depth_frame'),
        
        ('chassis','base_link'),
        
        ('elikos_fcu','elikos_ffmv_bottom'),
        
        ('odom_combined','segment_0'),
        
        ('base','map'),
        
        ('base_frame','camera_link'),
        
        ('base_link','sonar'),
        
        ('nav','base_link'),
        
        ('odom','vicon_odom'),
        
        ('ohm_base_link','sick_laser_link'),
        
        ('world','navigation'),
        
        ('base_footprint','world'),
        
        ('base_frame','merged_lrf'),
        
        ('base_link','base_radar_link'),
        
        ('ground','camera'),
        
        ('map','origin'),
        
        ('map','respeaker_base'),
        
        ('base_link','base_laser_link'),
        
        ('base_link','camera_link'),
        
        ('base_link','base_imu_link'),
        
        ('base_frame','base_link'),
        
        ('base_link','world'),
        
        ('odom','base_frame'),
        
        ('base_link','kinect2_base_link'),
        
        ('camera_link','base_link'),
        
        ('base_laser_front_link','laser'),
        
        ('base_link','imu_baselink'),
        
        ('world','vicon'),
        
        ('base_link','gx5_link'),
        
        ('camera_link','openni_depth_frame'),
        
        ('kinect2_link','kinect2_rgb_optical_frame'),
        
        ('nav','base_footprint'),
        
        ('openni_camera','openni_rgb_frame'),
        
        ('scanmatcher_frame','base_footprint'),
        
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
        
        'link',
        
        'arena_origin_broadcaster',
        
        'base_laser_link',
        
        'base_link_to_base_laser_link',
        
        'static_tf_broadcaster',
        
        'imu_link_broadcaster',
        
        'odom_broadcaster',
        
        'base_link_second_to_laser',
        
        'base_link_to_imu_broadcaster',
        
        'sensor_transform_0',
        
        'sensor_transform_1',
        
        'sensor_transform_2',
        
        'sensor_transform_3',
        
        'sensor_transform_4',
        
        'static_tf_zed',
        
        'map_to_world',
        
        'world_to_map_publisher',
        
        'link1_broadcaster',
        
        'amcl_frame_to_base_link',
        
        'arm_to_kinect_mount',
        
        'bl_bf',
        
        'bl_front_link',
        
        'bl_lidar',
        
        'bl_rear_link',
        
        'camera_link_base_broadcaster',
        
        'camera2base',
        
        'compass_tf_publisher',
        
        'depth_transform_publisher',
        
        'ee_edge_frame',
        
        'fake_broadcaster',
        
        'fixed_frame_pub',
        
        'gps_tf_publisher',
        
        'link_broadcast',
        
        'localizer',
        
        'odom_2_odom',
        
        'odom_base_broadcaster',
        
        'odom_is_map',
        
        'odom_test_tf',
        
        'robot2_to_robot1',
        
        'scan_frame_broadcaster',
        
        'stf_hokuyo3d_laser',
        
        'table_to_arm',
        
        'tf_static_node',
        
        'trans_pub_map_world',
        
        'usb_cam_broadcaster',
        
        'world_local_broadcaster',
        
        'world_to_laser1',
        
        'world_to_laser2',
        
        'world_to_map_tf',
        
        'base_link_to_gps',
        
        'base_link_to_wheel_left_link',
        
        'base_link_to_wheel_right_link',
        
        'base_to_fcu_broadcaster',
        
        'gps_link_broadcaster',
        
        'static_tf_laser',
        
        'tf_scan_base',
        
        'tf_top_link',
        
        'world_odom0_link',
        
        'world_odom1_link',
        
        'base_frame_to_laser',
        
        'base_to_laser',
        
        'base_frame_2_laser_marged_link',
        
        'base_to_camera_broadcaster',
        
        'bl_gps',
        
        'initial_pose_link_broadcaster',
        
        'static_tf_imu',
        
        'base_to_kinect_broadcaster',
        
        'odom_tf',
        
        'static_tf1',
        
        'base_link_to_scan_broadcaster',
        
        'tf_local_origin',
        
        'bl_laser',
        
        '$(anon tf)',
        
        'any_transform',
        
        'base_footprint_base_link_tf',
        
        'base_footprint_transform',
        
        'base_to_gps',
        
        'base2rr',
        
        'bl_imu',
        
        'head_left_frame_id',
        
        'imu_link_transform',
        
        'laser_base_link',
        
        'left_gripper_center_to_wrist',
        
        'link_hokuyo',
        
        'map_base_tf',
        
        'map_root_frame_id',
        
        'map2base',
        
        'R1_MapAlign',
        
        'right_gripper_center_to_wrist',
        
        'tf_publisher_base_link',
        
        'tf_publisher_base_scan',
        
        'tf_publisher_camera_link',
        
        'tfdummy1',
        
        'tfdummy2',
        
        'tfdummy3',
        
        'tfdummy4',
        
        'tfdummy5',
        
        'tfdummy6',
        
        'world_frame',
        
        'world_odom2_link',
        
        'base2laser',
        
        'notilt',
        
        'static_map',
        
        'map_odom',
        
        'swri_transform',
        
        'arm_base',
        
        'base_laser_tf',
        
        'base_link_camera_link',
        
        'base_mask_tf',
        
        'base2imu',
        
        'bf2camera',
        
        'camera_link_zed_center',
        
        'environment_link_broadcaster',
        
        'fcu_broadcaster',
        
        'head_lidar_actuator_frame_pub',
        
        'link_laser_neato_broadcaster',
        
        'maplink',
        
        'my_stp',
        
        'odom',
        
        'odom_to_footprint',
        
        'R0_MapAlign',
        
        'static_world_frame',
        
        'tf_world_map',
        
        'transform_publisher',
        
        'vicontip_broadcaster',
        
        'base_link_first_to_laser',
        
        'hokuyo_transform',
        
        'imu_base_tf',
        
        'odom_2_map',
        
        'static_transform_publisher_sick_laser_link',
        
        'transform_local_cs',
        
        'transform_local_estimate_prior',
        
        'base_link_to_base_footprint',
        
        'camera_base_link',
        
        'fake_localize',
        
        'hokuyo_link_broadcaster',
        
        'leap_to_world_publisher',
        
        'task_frame',
        
        'tf_laser_link',
        
        'baselink_broadcaster',
        
        '$(anon map_tf01)',
        
        'april_tag_landmark_3',
        
        'arm1_pub',
        
        'arm2_pub',
        
        'ARtag',
        
        'ball_broadcaster',
        
        'base_2_cam',
        
        'base_camera_link',
        
        'base_footprint_base_link_publisher',
        
        'base_footprint_to_odom',
        
        'base_footprint_to_odom_tf_broadcaster',
        
        'base_frame',
        
        'base_frame_2_laser',
        
        'base_frame_2_lidar_link',
        
        'base_gps',
        
        'base_gps_link',
        
        'base_imu',
        
        'base_imu_broadcaster',
        
        'base_laser_link_tf',
        
        'base_laser_to_base_link',
        
        'base_link__Hokuyo_URG_04LX_UG01_ROS__broadcaster',
        
        'base_link_laser_link',
        
        'base_link_to_axle_front_wheel',
        
        'base_link_to_axle_mid_wheel',
        
        'base_link_to_axle_rear_wheel',
        
        'base_link_to_base_footprint_tf_broadcaster',
        
        'base_link_to_denso',
        
        'base_link_to_hokuyo_broadcaster',
        
        'base_link_to_laser_filt',
        
        'base_link_to_left_caster_wheel',
        
        'base_link_to_left_drive_wheel',
        
        'base_link_to_left_wheel_frame',
        
        'base_link_to_map',
        
        'base_link_to_right_caster_wheel',
        
        'base_link_to_right_drive_wheel',
        
        'base_link_to_right_wheel_frame',
        
        'base_link2base_footprint',
        
        'base_to_imu_tf',
        
        'base_to_laser_frame',
        
        'base_to_odom_p3dx',
        
        'base_to_rs',
        
        'basefootprint2baseleftcam',
        
        'baselink_laser',
        
        'baselink_to_camera',
        
        'baselink_to_gnss',
        
        'baselink_to_lidar',
        
        'baselink2basefootprint',
        
        'baselink2velodyne_$(arg robot_name)',
        
        'baselinkr2front_laser_link_tf_$(arg robot_name)',
        
        'bellows_link_broadcaster',
        
        'bl_phone',
        
        'camera_cam_to_depthframe',
        
        'camera_depth_frame_link',
        
        'camera_frame_link',
        
        'camera_in_base_link',
        
        'camera_lidar_tf',
        
        'camera_link_rgb_to_camera_link_depth',
        
        'camera_link_to_rgb_frame',
        
        'camera_link_to_zed_actual_frame',
        
        'camera_linker',
        
        'camera_radar_tf',
        
        'camera_to_baselink',
        
        'celoxia_base_broadcaster',
        
        'chassis_tf_pub',
        
        'correct_vrep_broadcaster',
        
        'correct_vrep_broadcaster2',
        
        'cross_tip_broadcaster',
        
        'debug_publisher',
        
        'dummy_imu_frame_broadcaster',
        
        'dummy_odom_frame_broadcaster',
        
        'dummycam_cameralink',
        
        'ee_link_to_endpoint',
        
        'ekf_frame',
        
        'entry_link_broadcaster',
        
        'env_broadcaster',
        
        'fake_odom_tf_publisher',
        
        'fake_tf_baseLink_map',
        
        'fake_tf_baseLink_odom',
        
        'fixed_frame_publisher',
        
        'foobar',
        
        'foot_to_odom',
        
        'footprint_to_link',
        
        'front_left_cliff_to_base_link',
        
        'front_right_cliff_to_base_link',
        
        'frontLeftSonarTF',
        
        'frontRightSonarTF',
        
        'gate1_broadcaster',
        
        'gate2_broadcaster',
        
        'gps_base_link',
        
        'gps_bug_fix',
        
        'gps_frame',
        
        'gps_tf_broadcaster',
        
        'gps_transform',
        
        'gripper_link_broadcaster',
        
        'gun_broadcaster',
        
        'gun_forward_broadcaster',
        
        'gyro_link_tf',
        
        'head_cam3d_link_frame',
        
        'head_camera_depth_link_broadcaster',
        
        'head_camera_link_broadcaster',
        
        'head_camera_rgb_link_broadcaster',
        
        'hokuyo_tf',
        
        'hydra_world_pub',
        
        'imu_bug_fix',
        
        'imu_imu_tf',
        
        'imu_link_connect',
        
        'ins_tf',
        
        'inside_camera_inside_fiducial_broadcaster',
        
        'inside_camera_outside_fiducial_broadcaster',
        
        'isam_to_imu',
        
        'katana_link_broadcaster',
        
        'kinect_front',
        
        'kinect_right',
        
        'kinect_tf_publisher',
        
        'lala_broadcaster',
        
        'laser_layer_0_first_echo_base_laser',
        
        'laser_pose',
        
        'laser_scan_broadcaster',
        
        'laser_transform_broadcaster',
        
        'laser2front_laser_link_tf_$(arg robot_name)',
        
        'launch_frame',
        
        'left_corner',
        
        'left_up_corner',
        
        'lidar_base_broadcaster',
        
        'lidar_bug_fix',
        
        'lidar_tf_pub',
        
        'LiDAR_to_world',
        
        'light_tf',
        
        'link_broadcaster_map',
        
        'link_broadcaster_odom',
        
        'link_laser_broadcaster',
        
        'link_rotation_laser_neato_broadcaster',
        
        'link_to_sim',
        
        'link_world2pillar_broadcaster',
        
        'link2odom',
        
        'LinkToScan',
        
        'map__to__STEVE0_map__static_tf',
        
        'map_base_footprint_publisher',
        
        'map_frame_broadcast',
        
        'map_humans_link',
        
        'map_odom_publisher',
        
        'map_odom_static_tf_broadcaster_for_testing',
        
        'map_odom_transform_publisher',
        
        'map_openni_camera',
        
        'map_ra_odom',
        
        'map_T_odom',
        
        'map_tf_static_pub_node',
        
        'map_to_base_imu_link',
        
        'map_to_odom_p3dx',
        
        'map_to_odom_perfect',
        
        'map_to_odom_transform_pub',
        
        'map_to_rtab',
        
        'map2slam_map_publisher',
        
        'MapTrasformPublisher',
        
        'marker_0_to_base',
        
        'marker_pos1',
        
        'marker_pos2',
        
        'marker_pos3',
        
        'marker_pos4',
        
        'mbOdom_to_odom',
        
        'middle',
        
        'nav',
        
        'navsat',
        
        'new_broad',
        
        'occam0_gt_broadcaster',
        
        'odom_comb_out_to_odom',
        
        'odom_combined_base_link_broadcaster',
        
        'odom_combined_to_base_footprint',
        
        'odom_matcher_2',
        
        'odom_pub',
        
        'odom_to_local_origin',
        
        'odom_to_map_tf_broadcaster',
        
        'openni_depth_frame_publisher',
        
        'openni_tracker_to_meka',
        
        'optimization_link_1',
        
        'overhead1_frame',
        
        'p3_camera_link_publisher',
        
        'pancake_maker_transform',
        
        'peg1_pub',
        
        'peg2_pub',
        
        'person1_head',
        
        'person1_torso',
        
        'person2_head',
        
        'person2_torso',
        
        'person3_head',
        
        'person3_torso',
        
        'plate_transform',
        
        'point_cloud_broadcaster',
        
        'pr2_simulation_mocap_to_odomcombined_broadcaster',
        
        'primesense_to_world',
        
        'ptu_frame_broadcaster',
        
        'quadrotor_baselink_transform_publisher',
        
        'radar_baselink_0',
        
        'radar_baselink_1',
        
        'radar_imu_tf',
        
        'right_corner',
        
        'right_up_corner',
        
        'right_vacuum_gripper_tf_publisher',
        
        'ring1_pub',
        
        'robot_to_octomap',
        
        'robot3_to_robot1',
        
        'root_static_tf_publisher',
        
        'root_static_tf_publisher2',
        
        'ROSbot_camera',
        
        'rs_base_link_transform',
        
        'rs_odom_transform',
        
        'scan2link',
        
        'sensor_bridge',
        
        'sensor_tf_imu',
        
        'sensor_tf_lleg',
        
        'sensor_tf_rleg',
        
        'setpoint_publisher',
        
        'sim_drone_base_alias',
        
        'sim_drone_odom_alias',
        
        'sim_map_odom_broadcaster',
        
        'sonar_T_base_link',
        
        'start_broadcaster',
        
        'static_publisher2',
        
        'static_tf_6',
        
        'static_tf_7',
        
        'static_tf_publisher_map_to_shelf',
        
        'static_tf_publisher_world_tags_base',
        
        'static_tf_radar_to_pcl',
        
        'static_transform_pub',
        
        'static_transform_publisher_beam_beam',
        
        'static_transform_publisher_openni',
        
        'static_world_cc_pause_publisher',
        
        'static_world_cc_tequila_publisher',
        
        'static_world_torso_up_publisher',
        
        'staticLaser',
        
        'stp_depth',
        
        'suck_cup_adjuster',
        
        'sw_arm_l_to_base',
        
        'sw_arm_r_to_base',
        
        'tb_base_link_publisher',
        
        'tf_base_gps',
        
        'tf_baselink2laser',
        
        'tf_broadcaster_sick',
        
        'tf_camera_opticalframe',
        
        'tf_fixed_localization',
        
        'tf_front_laser_base_link',
        
        'tf_imu_base_link',
        
        'tf_laser_frame',
        
        'tf_map_odom',
        
        'tf_optitrack_to_youbot_base_link',
        
        'tf_pub_first',
        
        'tf_pub_second',
        
        'tf_publisher_decawave0',
        
        'tf_velodyne_base_link',
        
        'tf4',
        
        'tf5',
        
        'tf6',
        
        'tf7',
        
        'tof_tf_broadcaster',
        
        'torso_fixed_link_broadcaster',
        
        'torso_static_transform_pub',
        
        'trans_pub_world_odom',
        
        'trans_pub_world_odom_est',
        
        'trans_pub_world_odom_gt',
        
        'trans_tf_static',
        
        'trololololol',
        
        'ur5_link_broadcaster',
        
        'uwb_tf_static_publisher',
        
        'vectornav_tf_odom',
        
        'vehicle_is_odom',
        
        'velo_link_broadcaster',
        
        'velodyne_frame',
        
        'velodyne_left',
        
        'velodyne_right',
        
        'velodyne_tf_broadcaster',
        
        'velodyne_to_baselink',
        
        'virtual_laser_to_laser_front',
        
        'virtual_odom_tf',
        
        'vis_odom_to_odom',
        
        'vp6242_tf',
        
        'W2Q_tf',
        
        'wheel_back_left_broadcaster',
        
        'wheel_back_right_broadcaster',
        
        'wheel_front_left__broadcaster',
        
        'wheel_front_right_broadcaster',
        
        'world_baker_transform',
        
        'world_joint_broadcaster',
        
        'world_pancake_transform',
        
        'world_to_base_publisher',
        
        'world_to_scanner',
        
        'xiroi_to_gps$(arg suffix)',
        
        'xiroi_to_usbl$(arg suffix)',
        
        'xtion_to_hexapod',
        
        'yumi_dlsr_r',
        
        'Zed_to_camera_broadcaster',
        
        'Zed_to_odom_broadcaster',
        
        'zed0_dumy_tf',
        
        'map_tf_broadcaster',
        
        'laser_broadcaster',
        
        'imu_tf',
        
        'lidar_tf',
        
        'world_transform',
        
        'map_nav_broadcaster',
        
        'virtual_joint_broadcaster_1',
        
        'world_map_broadcaster',
        
        'world_odom_frame',
        
        'kitchen_link_broadcaster',
        
        'laser_link_broadcaster',
        
        'origin_broadcaster',
        
        'base_to_camera_tf',
        
        '$(arg prefix)laser_link',
        
        '$(arg prefix)xtion_link',
        
        'ar_marker_2_rename',
        
        'arm_base_rotation',
        
        'base_foot_print_to_waist',
        
        'base_link_2_lidar',
        
        'base_link_laser_publisher',
        
        'base_link_to_camera_bcaster',
        
        'base_link_to_gx5_link',
        
        'base_link_to_left_center_drive_wheel',
        
        'base_link_to_left_front_drive_wheel',
        
        'base_link_to_left_rear_drive_wheel',
        
        'base_link_to_right_center_drive_wheel',
        
        'base_link_to_right_front_drive_wheel',
        
        'base_link_to_right_rear_drive_wheel',
        
        'base_to_footprint',
        
        'base_to_teraranger',
        
        'base_transform',
        
        'base_trep_broadcaster',
        
        'basestation_publisher',
        
        'bl2map',
        
        'board_tf_broadcaster',
        
        'body_link',
        
        'c3po_base_link_tf',
        
        'cam_to_cam_frame',
        
        'camera_link_publisher',
        
        'camera_rgb_frame_tf',
        
        'camtf',
        
        'deckard_identity',
        
        'dummy_odom_to_map',
        
        'front_sonar_to_base_link',
        
        'hazcam_broadcaster',
        
        'headCamera2Basefootprint',
        
        'imu_to_bl',
        
        'ir_center_tf',
        
        'jinx_merry_trasnform',
        
        'kinect_to_base_link',
        
        'kinect2_broadcaster',
        
        'kinect3_broadcaster',
        
        'kinect4_broadcaster',
        
        'kinect5_broadcaster',
        
        'laser_base',
        
        'laser_to_odom',
        
        'ldmrs0_broadcaster',
        
        'ldmrs1_broadcaster',
        
        'ldmrs2_broadcaster',
        
        'ldmrs3_broadcaster',
        
        'leap_link',
        
        'link_realsense',
        
        'map_odom_tf_broadcaster',
        
        'map_odom_transform_broadcaster',
        
        'map_to_duckiebot_link_broadcaster',
        
        'map_to_odom_broadcaster',
        
        'map_to_odom_tf_publisher',
        
        'map_to_real_base_link',
        
        'map_to_volume_publisher',
        
        'map2base_tf',
        
        'map2frame',
        
        'map2odom1',
        
        'marker_robot',
        
        'marker_to_world',
        
        'model_connector',
        
        'nav_origin_tf',
        
        'nav2base_broadcaster',
        
        'neck_fixed_joint',
        
        'odom_base',
        
        'odom_base_foot',
        
        'odom_to_base_link_broadcaster',
        
        'odom_to_world_tf',
        
        'odom_world_broadcaster',
        
        'Parrot_imu',
        
        'PlateImage_broadcaster',
        
        'pris_identity',
        
        'ptz_broadcaster',
        
        'r2d2_base_link_tf',
        
        'rel_c3po_odom_tf',
        
        'rel_odom_tf',
        
        'rel_r2d2_odom_tf',
        
        'right_realsense',
        
        'robot_marker_pub',
        
        'ROIPlateImage_broadcaster',
        
        'room_link_broadcaster',
        
        'roy_identity',
        
        'scan_tf',
        
        'sensor_tf_larm',
        
        'sensor_tf_rarm',
        
        'sensor_to_base_link',
        
        'sonar4_tf',
        
        'st_trans',
        
        'static_broadcaster',
        
        'static_laser_link_tf',
        
        'static_tf_2',
        
        'static_tf_stage',
        
        'static_transform_publisher_local_origin_world',
        
        'static1',
        
        'stereo_down_to_left_optical',
        
        'stereo_to_left_tf',
        
        'stereo_to_right_tf',
        
        'stero_tf_publisher',
        
        'tcp_publisher',
        
        'tf_base_link',
        
        'tf_base2road_markings',
        
        'tf_map_to_odom',
        
        'tf_publisher',
        
        'tf_publisher_christa',
        
        'uwb_to_vicon_tf',
        
        'velodyne_base_link',
        
        'velodyne_to_front_laser',
        
        'virtual_joint_broadcaster',
        
        'wheel_odom_broadcaster_b',
        
        'wheel_odom_broadcaster_c',
        
        'wheel_odom_broadcaster_d',
        
        'word_link0_tf_broadcaster',
        
        'world_phantom_base_broadcaster',
        
        'world_robot1_base_broadcaster',
        
        'world_robot2_base_broadcaster',
        
        'world_tf_pub',
        
        'world_to_robot',
        
        'world2map_broadcaster',
        
        'ZeroBBOffsetPublisher',
        
        'zhora_identity',
        
        'link2_broadcaster',
        
        'laser',
        
        'base_to_camera',
        
        'base_footprint_base_link',
        
        'base_imu_link',
        
        'base_link_to_laser_virtual',
        
        'base_link_transform',
        
        'base_map_tf',
        
        'baselink_to_basefootprint',
        
        'centerlaser_transform',
        
        'conveyer',
        
        'head_root_frame_id',
        
        'kinect1_broadcaster',
        
        'left_optical2stereo_camera',
        
        'link_static_tf',
        
        'map_broadcaster2',
        
        'map_cam_tf',
        
        'map_footprint_broadcaster',
        
        'map_nav_map_bcast',
        
        'map_nav_path_bcast',
        
        'map_to_baselink_broadcaster',
        
        'map_to_gps',
        
        'odom_map_nav_bcast',
        
        'ps2_publisher',
        
        'sonar_tf',
        
        'static_tf_map_to_odom',
        
        'static_transform_publisher_zed',
        
        'test_broadcaster',
        
        'tf_base_footprint',
        
        'tf_base_imu',
        
        'tf_publisher_world',
        
        'velodyne_link_broadcaster',
        
        'wheel_odom_broadcaster',
        
        'world_utm_broadcaster',
        
        'world2odom',
        
        'odom_left_wheel_broadcaster',
        
        'odom_right_wheel_broadcaster',
        
        'tf_front',
        
        'base_laser1_broadcaster',
        
        'base_link_laser_broadcaster',
        
        'base_link_to_center',
        
        'base_link_to_imu_bosch',
        
        'base_link2laser',
        
        'base_tf',
        
        'bl_sonar_front',
        
        'broadcaster2',
        
        'camera_FRAME',
        
        'camera_link_to_d435',
        
        'elikos_arena_origin',
        
        'fake_odom',
        
        'human_broadcaster',
        
        'kinect_rgb_to_kinect_depth',
        
        'laser_frame_broadcaster',
        
        'laser_transform',
        
        'map_baselink_broadcaster',
        
        'map_to_base_link',
        
        'map_to_des',
        
        'map_to_maplink_frame_publisher',
        
        'map_to_mobility',
        
        'map_to_utm',
        
        'moveit_odom_broadcaster',
        
        'odom_combined_broadcaster',
        
        'odom_to_t265_odom',
        
        'scanmatcher_to_base_footprint',
        
        'static_tf3',
        
        'tf_02',
        
        'tf_03',
        
        'tf_05',
        
        'tf_3Dlidar',
        
        'tf_base2imu',
        
        'tf_scanner',
        
        'tf_static',
        
        'trasform_sensor',
        
        'map_2_base_footprint',
        
        'base_link_to_laser_broadcaster',
        
        'tf1',
        
        'base_link_to_imu_base_link',
        
        'camera_base_tf',
        
        'laser_tf',
        
        'odom_to_basefootprint',
        
        'odom_to_world',
        
        'ROSbot2_camera',
        
        'static_map_tf_publisher',
        
        'tf_53',
        
        'world_to_base',
        
        'world_to_map_frame_publisher',
        
        'base_link_to_velodyne',
        
        'imu_tf_broadcaster',
        
        'base_footprint_fixed_publisher',
        
        'base_to_odom_r1',
        
        'fake_odometry',
        
        'odom_to_vicon_odom',
        
        'add_laser_to_baselink',
        
        'base2lidar',
        
        'camera_to_ground',
        
        'kinect_base_link1',
        
        'laser_base_tf',
        
        'static_transformer',
        
        'base_link_to_laser4',
        
        'base_link_to_imu',
        
        'link3_broadcaster',
        
        'base_laser_broadcaster',
        
        'world_to_map_broadcaster',
        
        'base_frame_laser',
        
        'base_to_kinect2',
        
        'laser_2_base_link',
        
        'static_transform_publisher',
        
        'base_link_2_base_frame',
        
        'base_link_to_laser_link',
        
        'baselink_laser_broadcaster',
        
        'marker_broadcaster',
        
        'tf3',
        
        'base_link_to_cam',
        
        'map_2_base_link',
        
        'odom_to_base_link',
        
        'static_transform',
        
        'tabmap_broadcaster',
        
    }

    return null_rot_names