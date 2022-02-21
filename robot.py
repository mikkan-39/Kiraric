from src.handlers.dynamixel_handler import Dynamixel_handler
import src.handlers.dxl_adresses as ADR
from collections import defaultdict


class Robot(Dynamixel_handler):
    def __init__(self):
        Dynamixel_handler.__init__(self)
        self.servos = {}
        self.scan_for_servos()
    
    def scan_for_servos(self):
        servo_ids = self.ping_all()
        for id in servo_ids:
            self.servos[id] = defaultdict(int)
    
    def write_angle(self, servo_id, angle):
        if not self.servos[servo_id]["enabled"]:
            self.write(servo_id, ADR.torque_enable, True)
            self.servos[servo_id]["enabled"] = True
        
        offset = self.servos[servo_id]["offset"]
        reversed = self.servos[servo_id]["reversed"]
        if not reversed:
            val = int(512+((angle+offset)*512/150))
        else:
            val = int(512-((angle+offset)*512/150))
        self.write(servo_id, ADR.goal_position, val)


    def read_angle(self, servo_id):
        pos = self.read(servo_id, ADR.present_position)
        offset = self.servos[servo_id]["offset"]
        reversed = self.servos[servo_id]["reversed"]
        if not reversed:
            val = (pos-512)*150/512 - offset
        else:
            val = -1*(pos-512)*150/512 - offset
        return val

    def relax(self, servo_id=None):
        if not servo_id:
            ids = self.servos.keys()
        else:
            ids = [servo_id]

        for i in ids:
            self.write(i, ADR.torque_enable, False)
            self.servos[i]["enabled"] = False
    
    def set_offset(self, servo_id, offset):
        self.servos[servo_id]["offset"] = offset
    
    def set_reverse(self, servo_id, reverse):
        self.servos[servo_id]["reversed"] = reverse

    def read_load(self, servo_id):
        reversed = self.servos[servo_id]["reversed"]
        load = self.read(servo_id, ADR.present_load)
        if load < 1024:
            res = load
        else:
            res = 1023-load
        return res if reversed else res*-1