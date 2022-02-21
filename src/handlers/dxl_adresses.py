from collections import namedtuple

Field = namedtuple('Field', ['addr', 'bytelen', 'readonly', 'maxval'], defaults=(False, 1023))
# field_name = Field(addr, bytelen, ...)

# Info for servo identification
id =                Field(3,  1, readonly=False, maxval=255) # Servo id
model =             Field(0,  2, readonly=True)              # Servo model
firmware_ver =      Field(2,  1, readonly=True,  maxval=255) # Servo firmware
return_delay_time = Field(5,  1, readonly=False, maxval=255) # Response delay

# Essential controls
led =               Field(25, 1, readonly=False, maxval=1)  # Built-in LED
torque_enable =     Field(24, 1, readonly=False, maxval=1)  # Enables The servo to move. Resets 
goal_position =     Field(30, 2) # Where we should move
torque_limit =      Field(34, 2) # That's a torque limit, I hope you can read
max_torque =        Field(14, 2) # Same as torque_limit, but permanent
moving_speed =      Field(32, 2) # Speed limit, also main control in wheelmode

# The read-onlys
present_position =  Field(36, 2, readonly=True) # They speak for themselves
present_speed =     Field(38, 2, readonly=True)
present_load =      Field(40, 2, readonly=True)
present_voltage =   Field(42, 1, readonly=True)
present_temp =      Field(43, 1, readonly=True)

# These are basically for setting wheelmode
cw_angle_limit =    Field(6,  2)
ccw_angle_limit =   Field(8,  2)

# These you shouldn't ever have to modify, but just in case
cw_compliance =     Field(26, 1)
ccw_compliance =    Field(27, 1)
cw_slope =          Field(28, 1)
ccw_slope =         Field(29, 1)

ADDR_TABLE = dict(locals())
garbage = ['Field', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__', 'namedtuple']
for g in garbage:
    ADDR_TABLE.pop(g, None)