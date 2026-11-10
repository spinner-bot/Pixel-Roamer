"""Command-line entry point. Importing this module does not start the game."""
from pixel_roamer.application import GameApp


def main():
    GameApp().run()


if __name__ == "__main__":
    main()
