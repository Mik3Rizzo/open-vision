from game_manager import GameManager
from config import Config

def main():
    cfg = Config()
    manager = GameManager(cfg)
    manager.run()

if __name__ == "__main__":
    main()