from asyncore import read
from time import sleep
from robot import Robot
import src.handlers.dxl_adresses as ADR
from math import acos, atan, degrees, sqrt


def_offsets = {
    4: -70, #-90
    5: 90,
    6: 45,
}

reversed_motors = [4, 5, 6, 7, 9, 10, 11, 17, 12]

def main():
    def IK(x, y):
        AB, BC, AC = sqrt(x**2+y**2), 92, 93 #mm
        if  AB > (BC+AC):
            raise ValueError()
        XAB = 90-degrees(atan(y/x))
        ABC = degrees(acos((AB**2+BC**2-AC**2)/(2*AB*BC)))
        BAC = degrees(acos((AB**2+AC**2-BC**2)/(2*AB*AC)))
        ACB = 180-ABC-BAC
        alpha = ABC-(90-XAB)
        beta = 180 - ACB
        gamma = 90 -(XAB-BAC)
        return alpha, beta, gamma

    robot = Robot()
    for id, offset in def_offsets.items():
        robot.set_offset(id, offset) 
        robot.set_offset(id+9, offset) 
    for id in reversed_motors:
        robot.set_reverse(id, True)
    for i in [6, 7, 15, 16, 4, 13, 11, 20]:
        robot.write_angle(i, 0)

    robot.write(8, ADR.moving_speed, 1023)
    robot.write(17, ADR.moving_speed, 1023)
    
    def read_load():
        return (robot.read_load(19)+robot.read_load(10))/200

    for x in range(80, 185):
        alpha, beta, gamma = IK(x, 0)
        robot.write_angle(8, alpha)
        robot.write_angle(9, beta)
        robot.write_angle(10, gamma)
        robot.write_angle(17, alpha)
        robot.write_angle(18, beta)
        robot.write_angle(19, gamma)

    for _ in range(1000):
        l = read_load()
        robot.write_angle(3,  l*3)
        robot.write_angle(12, l*3)
        robot.write_angle(8, l/2+5)
        robot.write_angle(17, l/2+5)
        sleep(0.01)
    
    for x in reversed(range(80, 185)):
        alpha, beta, gamma = IK(x, 0)
        robot.write_angle(8, alpha)
        robot.write_angle(9, beta)
        robot.write_angle(10, gamma)
        robot.write_angle(17, alpha)
        robot.write_angle(18, beta)
        robot.write_angle(19, gamma)

    robot.relax()
    

if __name__ == "__main__":
    main()
