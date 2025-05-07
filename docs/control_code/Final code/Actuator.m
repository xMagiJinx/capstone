classdef Actuator < handle
    properties (Constant)
        %% Modbus Function Codes
        Read = 3
        Write = 6
        Write_Multi = 16
        MotorCommand = 100
        MotorRead = 104
        MotorWrite = 105

        %% Modes of Operation
        SleepMode = 1
        ForceMode = 2
        PositionMode = 3
        HapticMode = 4
        KinematicMode = 5

        %% Haptic Effect Flags
        ConstF = 0b1
        Spring0 = 0b10
        Spring1 = 0b100
        Spring2 = 0b1000
        Damper  = 0b10000
        Inertia = 0b100000
        Osc0    = 0b1000000
        Osc1    = 0b10000000

        %% Control Registers
        CTRL_REG_0 = 0
        CTRL_REG_1 = 1
        CTRL_REG_2 = 2
        CTRL_REG_3 = 3
    end

    properties
        %% Serial Port Configuration
        comport;
        baudrate;
        s;

        %% Orca Motor Data
        position = 0;
        force = 0;     % (now stored as double immediately)
        power = 0;
        temperature = 0;
        voltage = 0;
        errors = 0;
        op_mode = 0;
    end

    methods
        %% Constructor
        function obj = Actuator(com_port, baud_rate)
            clear obj.s;
            obj.comport = com_port;
            obj.baudrate = baud_rate;
            obj.s = serialport(com_port, baud_rate, "Parity", "even");
        end

        %% Command Orca to Force
        function position = command_orca_force(obj, force_mN)
            forcebytes = int32(typecast(int32(force_mN), 'uint8'));
            obj.s.write(obj.append_crc([1, obj.MotorCommand, 28, forcebytes(4), forcebytes(3), forcebytes(2), forcebytes(1)]), "uint8");
            data = obj.s.read(19, "uint8");

            obj.position = typecast(uint8([data(6) data(5) data(4) data(3)]), 'int32');
            temp = typecast(uint8([data(10) data(9) data(8) data(7)]), 'int32');
            obj.force = double(temp);

            obj.power = typecast(uint8([data(12) data(11)]), 'uint16');
            obj.temperature = data(13);
            obj.voltage = typecast(uint8([data(15) data(14)]), 'uint16');
            obj.errors = typecast(uint8([data(17) data(16)]), 'uint16');

            position = double(obj.position);

            if obj.errors == 2048
                obj.change_mode(obj.SleepMode);
            end
        end

        %% Command Orca to Position
        function force = command_orca_position(obj, position_um)
            positionbytes = int32(typecast(int32(position_um), 'uint8'));
            obj.s.write(obj.append_crc([1, obj.MotorCommand, 30, positionbytes(4), positionbytes(3), positionbytes(2), positionbytes(1)]), "uint8");
            data = obj.s.read(19, "uint8");

            obj.position = typecast(uint8([data(6) data(5) data(4) data(3)]), 'int32');
            temp = typecast(uint8([data(10) data(9) data(8) data(7)]), 'int32');
            obj.force = double(temp);

            obj.power = typecast(uint8([data(12) data(11)]), 'uint16');
            obj.temperature = data(13);
            obj.voltage = typecast(uint8([data(15) data(14)]), 'uint16');
            obj.errors = typecast(uint8([data(17) data(16)]), 'uint16');

            force = double(obj.force);

            if obj.errors == 2048
                obj.change_mode(obj.SleepMode);
            end
        end

        %% Read Stream
        function read_value = read_stream(obj, register_address, width)
            addressbytes = obj.u16_to_bytes(register_address);
            obj.s.write(obj.append_crc([1, obj.MotorRead, addressbytes, width]), "uint8");
            data = obj.s.read(24, "uint8");

            read_value = typecast(uint8([data(6) data(5) data(4) data(3)]), 'int32');
            obj.op_mode = data(7);
            obj.position = typecast(uint8([data(11) data(10) data(9) data(8)]), 'int32');
            temp = typecast(uint8([data(15) data(14) data(13) data(12)]), 'int32');
            obj.force = double(temp);

            obj.power = typecast(uint8([data(17) data(16)]), 'uint16');
            obj.temperature = data(18);
            obj.voltage = typecast(uint8([data(20) data(19)]), 'uint16');
            obj.errors = typecast(uint8([data(22) data(21)]), 'uint16');

            read_value = double(read_value);
        end

        %% Write Stream
        function force = write_stream(obj, registeraddr, width, value)
            addressbytes = obj.u16_to_bytes(registeraddr);
            valuebytes = int32(typecast(int32(value), 'uint8'));
            obj.s.write(obj.append_crc([1, obj.MotorWrite, addressbytes, width, valuebytes(4), valuebytes(3), valuebytes(2), valuebytes(1)]), "uint8");
            data = obj.s.read(20, "uint8");

            obj.op_mode = data(3);
            obj.position = typecast(uint8([data(7) data(6) data(5) data(4)]), 'int32');
            temp = typecast(uint8([data(11) data(10) data(9) data(8)]), 'int32');
            obj.force = double(temp);

            obj.power = typecast(uint8([data(13) data(12)]), 'uint16');
            obj.temperature = data(14);
            obj.voltage = typecast(uint8([data(16) data(15)]), 'uint16');
            obj.errors = typecast(uint8([data(18) data(17)]), 'uint16');

            force = double(obj.force);
        end

        %% (rest of your methods are unchanged and working fine)
        %% Change Mode
        function change_mode(obj, mode)
            obj.write_register(3, mode);
        end

        function kinematic_trigger(obj, motionID)
            obj.write_register(9, motionID);
        end

        function configure_motion(obj, motionID, position, time, delay, nextID, type, autonext)
            positionL_H = obj.int32_to_u16(position);
            timeL_H = obj.int32_to_u16(time);
            next_type_auto = bitshift(nextID, 3) + bitshift(type, 1) + autonext;
            configuration = [positionL_H, timeL_H, delay, next_type_auto];
            obj.write_multi_registers(780 + motionID*6, 6, configuration);
        end

        function enable_haptic_effect(obj, effect_bits)
            obj.write_register(641, effect_bits);
        end

        function configure_springA(obj, gain, center, coupling, deadzone, force_sat)
            center = typecast(int32(center), 'uint16');
            configuration = [gain center coupling deadzone force_sat];
            obj.write_multi_registers(644, 6, configuration);
        end

        function tune_pid_controller(obj, saturation, p_gain, i_gain, dv_gain, de_gain)
            saturationL_H = obj.int32_to_u16(saturation);
            configuration = [p_gain, i_gain, dv_gain, de_gain, saturationL_H];
            obj.write_multi_registers(133, 6, configuration);
        end

        function set_direction(obj, direction)
            obj.write_register(obj.CTRL_REG_0, 4);
            obj.write_register(152, direction);
        end

        function configure_zero(obj, ZERO_MODE, AUTO_ZERO_FORCE_N, AUTO_ZERO_EXIT_MODE)
            configuration = [ZERO_MODE AUTO_ZERO_FORCE_N AUTO_ZERO_EXIT_MODE];
            obj.write_multi_registers(171, 3, configuration);
        end

        function auto_zero_wait(obj)
            obj.write_register(3, 55);
            pause(0.1);
            while obj.read_register(317,1) == 55
            end
        end

        function write_register(obj, register_address, value)
            addressbytes = obj.u16_to_bytes(register_address);
            valuebytes = obj.u16_to_bytes(value);
            obj.s.write(obj.append_crc([1, obj.Write, addressbytes, valuebytes]), "uint8");
            obj.s.read(8, "uint8");
        end

        function write_multi_registers(obj, start_address, num_registers, register_data)
            register_data = uint16(register_data);
            databytes = obj.u16_to_bytes(register_data);
            addressbytes = obj.u16_to_bytes(start_address);
            num_registersbytes = obj.u16_to_bytes(num_registers);
            obj.s.write(obj.append_crc([1, obj.Write_Multi, addressbytes, num_registersbytes, num_registers*2, databytes]), "uint8");
            obj.s.read(8, "uint8");
        end

        function read_value = read_register(obj, start_address, num_registers)
            addressbytes = obj.u16_to_bytes(start_address);
            num_registersbytes = obj.u16_to_bytes(num_registers);
            obj.s.write(obj.append_crc([1, obj.Read, addressbytes, num_registersbytes]), "uint8");
            data = obj.s.read(5 + 2*num_registers, "uint8");

            read_value = zeros(1, num_registers);
            for i = 1:num_registers
                read_value(i) = typecast(uint8([data(2*(i-1)+5) data(2*(i-1)+4)]), 'uint16');
            end
        end
    end

    methods (Static)
        function amsg = append_crc(message)
            N = length(message);
            crc = hex2dec('ffff');
            polynomial = hex2dec('a001');
            for i = 1:N
                crc = bitxor(crc, message(i));
                for j = 1:8
                    if bitand(crc,1)
                        crc = bitshift(crc,-1);
                        crc = bitxor(crc,polynomial);
                    else
                        crc = bitshift(crc,-1);
                    end
                end
            end
            lowByte = bitand(crc, hex2dec('ff'));
            highByte = bitshift(bitand(crc, hex2dec('ff00')), -8);
            amsg = message;
            amsg(N+1) = lowByte;
            amsg(N+2) = highByte;
        end

        function bytes = u16_to_bytes(data)
            bytes = int32(typecast(swapbytes(uint16(data)), 'uint8'));
        end

        function u16 = int32_to_u16(data)
            u16 = int32(typecast(int32(data), 'uint16'));
        end
    end
end
