import math

def calc_disparity(cfg, screen_width, screen_height):
    screen_diagonal_mm = cfg.screen_diagonal_inch * 25.4
    screen_width_mm = screen_diagonal_mm / math.sqrt(1 + (screen_height / screen_width) ** 2)
    px_per_mm = screen_width / screen_width_mm
    disparity = int(round(cfg.interpupillary_dist_mm * px_per_mm * abs(cfg.z_screen_mm - cfg.z_object_mm) / cfg.z_object_mm))
    return disparity