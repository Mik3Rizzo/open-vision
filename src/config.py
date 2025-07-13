import yaml

# Default values as constants
DEFAULT_CONFIG_FILE="config.yaml"

DEFAULT_SCREEN_DIAGONAL_INCH = 27

DEFAULT_INTERPUPILLARY_DIST_MM = 65
DEFAULT_Z_SCREEN_MM = 500
DEFAULT_Z_OBJECT_MM = 490

DEFAULT_LAYER_WIDTH = 600
DEFAULT_LAYER_HEIGHT = 450

DEFAULT_NOISE_INTENSITY = 180
DEFAULT_SQUARE_SIZE = 80

DEFAULT_MIN_OFFSET = 0
DEFAULT_MAX_OFFSET = 800
DEFAULT_INITIAL_OFFSET = 0
DEFAULT_STEP = 5

DEFAULT_GAME_DURATION_SEC = 180

class Config:
    def __init__(self, config_file=DEFAULT_CONFIG_FILE):
        # Load the configuration from a YAML file
        with open(config_file, "r") as file:
            config_data = yaml.safe_load(file)
        
        # Screen settings
        self.screen_diagonal_inch = config_data.get("screen_diagonal_inch", DEFAULT_SCREEN_DIAGONAL_INCH)
        
        # Observer parameters
        self.interpupillary_dist_mm = config_data.get("interpupillary_dist_mm", DEFAULT_INTERPUPILLARY_DIST_MM)
        self.z_screen_mm = config_data.get("z_screen_mm", DEFAULT_Z_SCREEN_MM)
        self.z_object_mm = config_data.get("z_object_mm", DEFAULT_Z_OBJECT_MM)
        
        # Layer settings
        self.layer_width = config_data.get("layer_width", DEFAULT_LAYER_WIDTH)
        self.layer_height = config_data.get("layer_height", DEFAULT_LAYER_HEIGHT)
        
        # Noise settings
        self.noise_intensity = config_data.get("noise_intensity", DEFAULT_NOISE_INTENSITY)
        
        # Hidden square size
        self.square_size = config_data.get("square_size", DEFAULT_SQUARE_SIZE)

        # Offset settings
        self.min_offset = config_data.get("min_offset", DEFAULT_MIN_OFFSET)
        self.max_offset = config_data.get("max_offset", DEFAULT_MAX_OFFSET)
        self.initial_offset = config_data.get("initial_offset", DEFAULT_INITIAL_OFFSET)
        self.step = config_data.get("step", DEFAULT_STEP)

        # Game duration
        self.game_duration_sec = config_data.get("game_duration_sec", DEFAULT_GAME_DURATION_SEC)