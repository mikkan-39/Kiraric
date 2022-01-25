from pip._internal import main as pipmain
import io


def main():
    def is_raspberrypi():
        try:
            with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
                if 'raspberry pi' in m.read().lower(): return True
        except Exception: pass
        return False

    assert(is_raspberrypi()), "This code is intended to be run only on RPi"

    pipmain(['install', 'dynamixel-sdk'])


if __name__ == '__main__':
    main()
