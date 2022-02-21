from dynamixel_sdk import *
import dxl_adresses as DXL

class Dynamixel_handler:
    def __init__(self, portname='/dev/ttyACM0'):
        self.PORTNAME = portname
        PROTOCOL_VERSION = 1.0
        BAUDRATE = 1000000
        DEVICENAME = self.PORTNAME
        self.__portHandler = PortHandler(DEVICENAME)
        self.__packetHandler = PacketHandler(PROTOCOL_VERSION)
        if self.__portHandler.openPort():
            if not self.__portHandler.setBaudRate(BAUDRATE):
                raise Exception
        else:
            raise Exception
        self.memory_adresses = DXL.ADDR_TABLE
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


    # Finds all servos on the bus and returns an ID list
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


    # Writes to a field in memory
    def write(self, DXL_ID, memory_field, value):
        (ADDR, BYTELEN, READONLY, MAXVAL) = memory_field
        # Support for Boolean values
        if MAXVAL == 1:
            value = 1 if value else 0
        # Sanity check
        if value < 0 or value > MAXVAL: 
            raise ValueError(f'Unacceptable value {value} for address {ADDR}.')
        if READONLY:
            raise ValueError(f'Address {ADDR} is read-only.')
        
        if BYTELEN == 1:
            dxl_comm_result, dxl_error = self.__packetHandler.write1ByteTxRx(
                self.__portHandler, DXL_ID, ADDR, value)
        elif BYTELEN == 2:
            dxl_comm_result, dxl_error = self.__packetHandler.write2ByteTxRx(
                self.__portHandler, DXL_ID, ADDR, value)
        if dxl_comm_result != COMM_SUCCESS:
            raise Exception("%s" % self.__packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error:
            raise Exception("%s" % self.__packetHandler.getRxPacketError(dxl_error))

    # Reads a field from memory
    def read(self, DXL_ID, memory_field):
        (ADDR, BYTELEN, READONLY, MAXVAL) = memory_field
        
        if BYTELEN == 1:
            value, dxl_comm_result, dxl_error = self.__packetHandler.read1ByteTxRx(self.__portHandler, DXL_ID, ADDR)
        elif BYTELEN == 2:
            value, dxl_comm_result, dxl_error = self.__packetHandler.read2ByteTxRx(self.__portHandler, DXL_ID, ADDR)

        if dxl_comm_result != COMM_SUCCESS:
            raise Exception("%s" % self.__packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error:
            raise Exception("%s" % self.__packetHandler.getRxPacketError(dxl_error))

        # Convert to Boolean 
        if MAXVAL == 1:
            value = True if value else False

        return value

    # Syncronized write to multiple servos. Only can write to the same field
    def syncWrite(self,  DXL_IDS, memory_field, values):
        (ADDR, BYTELEN, READONLY, MAXVAL) = memory_field

        # Support for Boolean values
        if MAXVAL == 1:
            values = [1 if v else 0 for v in values]
        # In case we want to write the same value
        if len(list(values) == 1):
            values = list(values) * len(DXL_IDS)
        # Sanity check
        if any([v < 0 or v > MAXVAL for v in values]):
            raise ValueError(f'Unacceptable value for address {ADDR}.')
        if READONLY:
            raise ValueError(f'Address {ADDR} is read-only.')
        if len(DXL_IDS) != len(values):
            raise ValueError('Cannot match motors with positions')

        self.__groupSyncWrite = GroupSyncWrite(self.__portHandler, self.__packetHandler, ADDR, BYTELEN)
        for (DXL_ID, val) in zip(DXL_IDS, values):
            if BYTELEN == 1:
                param = [DXL_LOBYTE(val)]
            elif BYTELEN == 2:
                param = [DXL_LOBYTE(val), DXL_HIBYTE(val)]
            dxl_addparam_result = self.__groupSyncWrite.addParam(DXL_ID, param)
            if not dxl_addparam_result:
                raise Exception("[ID:%03d] groupSyncWrite addparam failed" % DXL_ID)
        dxl_comm_result = self.__groupSyncWrite.txPacket()
        if dxl_comm_result != COMM_SUCCESS:
            raise Exception("%s" % self.__packetHandler.getTxRxResult(dxl_comm_result))
        self.__groupSyncWrite.clearParam()


    # Reads all memory from a servo. Used for diagnostics
    def dump(self, DXL_ID):
        return {name: self.read(DXL_ID, params) for name, params in self.memory_adresses.items()}


    # Checks connection with each servo, and enforces default values for some critical memory fields. 
    # Also, it prints out a nice table of all servo's memory fields
    def diagnostics(self, logging=True, autofix=True):
        def tablelize(headers_v, headers_h, values_by_h):
            max_header_v_width = max(len(key) for key in headers_v)
            max_headers_h_max_header_v_widths = [
                max(len(str(value)) for value in values_by_h[key].values()) for key in headers_h
            ]

            line_width = (
                max_header_v_width + sum(max_headers_h_max_header_v_widths) + len(headers_h)
            )

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
            self.write(id, DXL.led, True)
            res = self.dump(id)
            self.write(id, DXL.led, False)
            return res

        motors_params = {id: check_motor(id) for id in id_list}

        self.syncWrite(id_list, DXL.led, False)

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
                            self.write(ID, param, default)
            pass

        return motors_params

    def wait_for_goal_positions(self, DXL_IDS):
        goals = {
            ID: self.read(ID, DXL.goal_position) for ID in DXL_IDS
        }
        reached = False
        while not ready:
            positions = {
                ID: self.read(ID, DXL.present_position) for ID in DXL_IDS
            }
            reached = all([
                abs(positions[ID]-goals[ID])<10 for ID in DXL_IDS
            ])
            speeds = {
                ID: self.read(ID, DXL.present_speed) for ID in DXL_IDS
            }
            ready = reached and all([
                abs(speeds[ID])<2 for ID in DXL_IDS
            ])
        pass
    
    
    def set_wheel_mode(self, DXL_IDS, value):
        for DXL_ID in DXL_IDS:
            self.write(DXL_ID, DXL.ccw_angle_limit, 0 if value else 1)
        pass