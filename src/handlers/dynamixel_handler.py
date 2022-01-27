from dynamixel_sdk import *


class Dynamixel_handler:
    def __init__(self, portname):
        self.PORTNAME = portname
        self.memory_adresses = {
            "id":                (3,  1), # "name": (addr, bytes)
            "model":             (0,  2),
            "firmware_ver":      (2,  1),
            "return_delay_time": (5,  1),
            "max_torque":        (14, 2),
            "torque_enable":     (24, 1),
            "torque_limit":      (34, 2),
            "led":               (25, 1),
            "goal_position":     (30, 2),
            "present_position":  (36, 2),
            "moving_speed":      (32, 2),
            "present_speed":     (38, 2),
            "present_load":      (40, 2),
            "present_voltage":   (42, 1),
            "present_temp":      (43, 1),
            "cw_angle_limit":    (6,  2),
            "ccw_angle_limit":   (8,  2),
            "cw_compliance":     (26, 1),
            "ccw_compliance":    (27, 1),
            "cw_slope":          (28, 1),
            "ccw_slope":         (29, 1),
        }
        self.default_params = {
            "return_delay_time": 0,
            "max_torque": 1023,
            "cw_angle_limit": 0,
            "ccw_angle_limit": 1023,
        }
        self.models = {
            300: "AX-12W",
            12:  "AX-12A"
        }
        pass


    def connect(self):
        PROTOCOL_VERSION = 1.0
        BAUDRATE = 1000000
        DEVICENAME = self.PORTNAME
        self.__portHandler = PortHandler(DEVICENAME)
        self.__packetHandler = PacketHandler(PROTOCOL_VERSION)
        if self.__portHandler.openPort():
            if self.__portHandler.setBaudRate(BAUDRATE):
                return
            else:
                raise Exception
        else:
            raise Exception


    def disconnect(self):
        return self.__portHandler.closePort()


    def ping_all(self, logging=False):
        found_motors = []
        for ID in range(30):
            dxl_model_number, dxl_comm_result, dxl_error = self.__packetHandler.ping(self.__portHandler, ID)
            if dxl_comm_result != COMM_SUCCESS:
                pass
            elif dxl_error != 0:
                pass
            else:
                found_motors.append(ID)
                if logging:
                    print("[ID:%03d] Found %s" % (ID, self.models[dxl_model_number]))
        return found_motors


    def write_to_ram(self, DXL_ID, name, value):
        (addr, byte_len) = self.memory_adresses[name]

        if byte_len == 1:
            dxl_comm_result, dxl_error = self.__packetHandler.write1ByteTxRx(
                self.__portHandler, DXL_ID, addr, value)
        elif byte_len == 2:
            dxl_comm_result, dxl_error = self.__packetHandler.write2ByteTxRx(
                self.__portHandler, DXL_ID, addr, value)
        if dxl_comm_result != COMM_SUCCESS:
            raise Exception("%s" % self.__packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error:
            raise Exception("%s" % self.__packetHandler.getRxPacketError(dxl_error))


    def read_from_ram(self, DXL_ID, name):
        (addr, byte_len) = self.memory_adresses[name]
        if byte_len == 1:
            value, dxl_comm_result, dxl_error = self.__packetHandler.read1ByteTxRx(self.__portHandler, DXL_ID, addr)
        elif byte_len == 2:
            value, dxl_comm_result, dxl_error = self.__packetHandler.read2ByteTxRx(self.__portHandler, DXL_ID, addr)

        if dxl_comm_result != COMM_SUCCESS:
            raise Exception("%s" % self.__packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error:
            raise Exception("%s" % self.__packetHandler.getRxPacketError(dxl_error))

        return value


    def syncWrite(self,  DXL_IDS, name, values):
        if name in self.memory_adresses.keys():
            (addr, byte_len) = self.memory_adresses[name]
        else:
            raise Exception("Cannot find parameter [%s]" % name)
        if len(DXL_IDS) != len(values):
            raise ValueError('Cannot match motors with positions')
        self.__groupSyncWrite = GroupSyncWrite(self.__portHandler, self.__packetHandler, addr, byte_len)
        for (DXL_ID, val) in zip(DXL_IDS, values):
            if byte_len == 1:
                param = [DXL_LOBYTE(val)]
            elif byte_len == 2:
                param = [DXL_LOBYTE(val), DXL_HIBYTE(val)]
            dxl_addparam_result = self.__groupSyncWrite.addParam(DXL_ID, param)
            if not dxl_addparam_result:
                raise Exception("[ID:%03d] groupSyncWrite addparam failed" % DXL_ID)
        dxl_comm_result = self.__groupSyncWrite.txPacket()
        if dxl_comm_result != COMM_SUCCESS:
            raise Exception("%s" % self.__packetHandler.getTxRxResult(dxl_comm_result))
        self.__groupSyncWrite.clearParam()


    def dump_ram(self, DXL_ID):
        return {param: self.read_from_ram(DXL_ID, param) for param in self.memory_adresses.keys()}
