
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

    }

    return null_rot_names



