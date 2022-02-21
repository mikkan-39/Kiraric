from robot import Robot

def_offsets = {
    4: -90,
    5: 90,
    6: 45,
}

reversed_motors = range(3, 12)

def main():
    robot = Robot()
    for id, offset in def_offsets.items():
        robot.set_offset(id, offset) 
        robot.set_offset(id+9, offset) 
    for id in reversed_motors:
        robot.set_reverse(id, True)
    
    for id in robot.servos:
        robot.write_angle(id, 0)

    

if __name__ == "__main__":
    main()
