%% Orca-3 Force Feedback Control System
% Written by Abby Palaia, Moises Hernandez, & Jake Taranov
% Final version with serial communication to Raspberry Pi Pico

clear all;
clc;

%% Serial Setup
pico = serialport("COM10", 9600);  % Replace COM8 with your Pico USB CDC data port
configureTerminator(pico, "LF");
flush(pico);
disp("Serial connection to Pico established");

%% Actuator Setup
orca = Actuator("COM9", 9600);  % Connect to Orca actuator

% Memory Map addresses
MODE_OF_OPERATION_address = 317;
SHAFT_POS_UM_address = 342;
FORCE_REGISTER_address = 348;

% Target force range in Newtons
min_force = 1.9765;
max_force = 2.8593;

%% Sleep & Zero Actuator
orca.op_mode = 0;
while orca.op_mode ~= orca.SleepMode
    orca.change_mode(orca.SleepMode);
    orca.op_mode = orca.read_register(MODE_OF_OPERATION_address, 1);
end
fprintf("Actuator in Sleep Mode\n");

%% AUTO-ZERO
    fprintf("Auto-Zeroing...\n")
    orca.configure_zero(2, 25, orca.KinematicMode);
    orca.auto_zero_wait();
    fprintf("Auto-Zero Complete\n");

%% Kinematic Mode
orca.op_mode = 5;
while orca.op_mode ~= orca.KinematicMode
    orca.change_mode(orca.KinematicMode);
    orca.op_mode = orca.read_register(MODE_OF_OPERATION_address, 1);
end
fprintf("Actuator set to Kinematic Mode\n");

%% Kinematic Configuration
orca.configure_motion(0, 0, 1000, 200, 1, 0, 0); 
orca.configure_motion(1, 20000, 1000, 200, 2, 0, 0);
orca.configure_motion(2, 30000, 1000, 200, 3, 0, 0);


%% Main Control Loop: Adjust Until Force Is Within Target Range
fprintf("Beginning force-controlled adjustment...\n");

while true
    % Trigger Orca motion
    orca.kinematic_trigger(1); % 1 is 20000 microm pos

    % Read latest force and position - push and read initial
    orca.read_stream(SHAFT_POS_UM_address, 1);  % Updates .force and .position
    orca.read_stream(FORCE_REGISTER_address,1);
    position_um = orca.position;
    force_mN = orca.force;
    force_N = force_mN / 1000;

    % Display to user
    fprintf("Position: %d µm | Force: %.4f N\n", position_um, force_N);

    % Check force range 
    if force_N >= min_force && force_N <= max_force % Force within 1.9765-2.8593
        fprintf("Target force achieved. Stopping loop.\n"); 
        break;
    end

    % Format & send ORCA data to Pico
    msg = sprintf("ORCA %.4f %d", force_N, position_um);  % e.g., "ORCA 2.54 12500"
    writeline(pico, msg);

    % Wait and read Pico's response
    pause(0.1);
    if pico.NumBytesAvailable > 0
        response = readline(pico);

        fprintf("Pico: %s\n", response);
    end

    pause(5);  % Allow time for Pico to adjust screws
end

fprintf("Control loop complete.\n");

orca.kinematic_trigger(0) % Return to postion 0 um



%%

%% Orca-Pico Calibration Loop
clear; clc;

% --- Setup
pico = serialport("COM10", 115200);
configureTerminator(pico, "LF");
flush(pico);
disp("Serial to Pico open at 115200 baud");

port = "COM9";
orca = Actuator(port, 19200);

MODE_OF_OPERATION_address = 317;
SHAFT_POS_UM_address      = 342;
FORCE_REGISTER_address    = 348;

orca.change_mode(orca.KinematicMode);
orca.configure_motion(0, 30000, 1000, 200, 1, 0, 0);  % Push
orca.configure_motion(1,     0, 1500, 200, 2, 0, 0);  % Retract
orca.configure_motion(2,     0, 1000, 200, 3, 0, 0);  % Home

% --- Parameters
min_force    = 1.9765;  % N
max_force    = 2.8593;  % N
max_attempts = 10;
attempt      = 0;

fprintf("Starting calibration loop...\n");

while attempt < max_attempts
    attempt = attempt + 1;
    fprintf("\n--- Attempt %d ---\n", attempt);

    % 1) Push motion
    orca.kinematic_trigger(0);
    pause(0.5);

    % 2) Wait for force to stabilize
    for i = 1:10
        orca.read_stream(SHAFT_POS_UM_address, 1);
        orca.read_stream(FORCE_REGISTER_address, 1);
        position_um = orca.position;
        force_N = orca.force / 1000;
        fprintf("Checking Force: %.4f N at Pos: %d um\n", force_N, position_um);
        pause(0.2);
    end

    if force_N >= min_force && force_N <= max_force
        fprintf("Force in range, no adjustment needed.\n");
        break;
    end

    % 3) Retract actuator
    orca.kinematic_trigger(1);

    % 3b) Wait for position to return to ~0
    t0 = tic;
    while toc(t0) < 5
        orca.read_stream(SHAFT_POS_UM_address, 1);
        if abs(orca.position) < 200
            break;
        end
        pause(0.1);
    end

    % 4) Send force and position to Pico
    msg = sprintf("ORCA %.4f %d", force_N, position_um);
    fprintf("Sent to Pico >%s<\n", msg);
    writeline(pico, msg);

    % 5) Wait for Pico response
    timeout = 4;
    t0 = tic;
    done_received = false;

    while toc(t0) < timeout
        if pico.NumBytesAvailable > 0
            line = readline(pico);
            if contains(line, "Response:")
                fprintf("Pico: %s\n", line);
            elseif contains(line, "DONE")
                done_received = true;
                fprintf("Pico finished motor adjustment.\n");
                break;
            else
                fprintf("Pico (other): %s\n", line);
            end
        end
        pause(0.05);
    end

    if ~done_received
        fprintf("Timeout: No DONE from Pico.\n");
    end
end

% 6) Final check and return home
orca.kinematic_trigger(0);
pause(0.5);
orca.read_stream(SHAFT_POS_UM_address, 1);
orca.read_stream(FORCE_REGISTER_address, 1);
final_force = orca.force / 1000;
fprintf("\nFinal force: %.4f N\n", final_force);

orca.kinematic_trigger(2);
fprintf("Returned to zero position.\n");

if final_force >= min_force && final_force <= max_force
    fprintf("Calibration successful.\n");
else
    fprintf("Calibration incomplete after %d attempts.\n", attempt);
end
