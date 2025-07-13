from src.entities.open_vision import OpenVision
from config.config import Config

def main():
    cfg = Config()
    manager = OpenVision(cfg)
    manager.run()

if __name__ == "__main__":
    main()