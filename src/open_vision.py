from fusional_vergence_game import FusionalVergenceGame
from config import Config

def main():
    cfg = Config()
    fvg = FusionalVergenceGame(cfg=cfg)
    fvg.run()

if __name__ == "__main__":
    main()