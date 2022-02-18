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

    def diagnostics(self, logging=False, autofix=False):
        def tablelize(headers_v, headers_h, values_by_h):
            max_header_v_width = max(len(key) for key in headers_v)
            max_headers_h_max_header_v_widths = [
                max(len(str(value)) for value in values_by_h[key].values()) for key in headers_h
            ]

            line_width = (
                max_header_v_width + sum(max_headers_h_max_header_v_widths) + len(headers_h)
            )  # len(headers_h.keys()) to count whitespaces between ids

            print(" ".join([
                        " " * max_header_v_width,
                        *[
                            str(header_h).ljust(max_headers_h_max_header_v_widths[index])
                            for index, header_h in enumerate(headers_h)
                        ],
                    ]))

            for header_v in headers_v:
                print("-" * line_width)
                print(" ".join([
                            header_v.ljust(max_header_v_width),
                            *[
                                str(values_by_h[header_h][header_v]).ljust(max_headers_h_max_header_v_widths[index])
                                for index, header_h in enumerate(headers_h)
                            ],
                        ]))

        id_list = self.ping_all()
        param_list = self.memory_adresses.keys()
        
        def check_motor(id):
            self.set_led([id], 1)
            res = self.dump_ram(id)
            #self.set_led([id], 0)
            return res

        motors_params = {id: check_motor(id) for id in id_list}

        self.syncWrite(id_list, "led", [0]*len(id_list))

        if logging:
            print('\n')
            tablelize(param_list, id_list, motors_params)
            print('\n')
        
        if autofix:
            for ID in motors_params.keys():
                motor = motors_params[ID]
                for param in motor.keys():
                    if param in self.default_params.keys():
                        default = self.default_params[param]
                        if motor[param] != default:
                            print("\033[1m" + 
                                "[Autofix] Set %s to %d for ID%d" % (param, default, ID) 
                                + "\033[0m")
                            self.write_to_ram(ID, param, default)
            pass

        return motors_params

    def enable_torque(self, DXL_IDS):
        for DXL_ID in DXL_IDS:
            self.write_to_ram(DXL_ID, "torque_enable", 1)


    def disable_torque(self, DXL_IDS):
        for DXL_ID in DXL_IDS:
            self.write_to_ram(DXL_ID, "torque_enable", 0)

    def set_led(self, DXL_IDS, val):
        for DXL_ID in DXL_IDS:
            self.write_to_ram(DXL_ID, "led", val)

    def wait_for_goal_positions(self, DXL_IDS):
        goals = {
            ID: self.read_from_ram(ID, "goal_position") for ID in DXL_IDS
        }
        reached = False
        while not reached:
            positions = {
                ID: self.read_from_ram(ID, "present_position") for ID in DXL_IDS
            }
            reached = all([
                abs(positions[ID]-goals[ID])<10 for ID in DXL_IDS
            ])
            speeds = {
                ID: self.read_from_ram(ID, "present_speed") for ID in DXL_IDS
            }
            reached = reached and all([
                abs(speeds[ID])<2 for ID in DXL_IDS
            ])
        pass
    
    
    def set_wheel_mode(self, DXL_IDS):
        for DXL_ID in DXL_IDS:
            self.write_to_ram(DXL_ID, "ccw_limit", 0)
        pass