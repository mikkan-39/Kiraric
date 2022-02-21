from src.handlers.dynamixel_handler import Dynamixel_handler

def main():
    dxl = Dynamixel_handler()
    dxl.diagnostics()


if __name__ == "__main__":
    main()
