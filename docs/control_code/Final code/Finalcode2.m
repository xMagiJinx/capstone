%% Orca-Pico Calibration Loop (±1% Margin, Auto-Zero, PID, Serial)
clear all; clc;

% --- Serial Setup ---
pico = serialport("COM10", 115200);
configureTerminator(pico, "LF");
flush(pico);
disp("Serial to Pico open at 115200 baud");

port = "COM9";
orca = Actuator(port, 19200);

MODE_OF_OPERATION_address = 317;
SHAFT_POS_UM_address      = 342;
FORCE_REGISTER_address    = 348;

%% --- Sleep & Auto-Zero ---
fprintf("Putting actuator into Sleep Mode...\n");
orca.op_mode = 0;
while orca.op_mode ~= orca.SleepMode
    orca.change_mode(orca.SleepMode);
    pause(0.2);
    orca.op_mode = orca.read_register(MODE_OF_OPERATION_address, 1);
end
fprintf("Actuator now in Sleep Mode.\n");

fprintf("Configuring Auto-Zero...\n");
orca.configure_zero(2, 25, orca.KinematicMode);
fprintf("Auto-Zeroing...\n");
orca.auto_zero_wait();
fprintf("Auto-Zero Complete.\n");

pause(0.5);

%% --- Set Filter + PID Tune ---
orca.write_register(650, 4000);  % FORCE_FILT
fprintf("Force filter set.\n");

orca.read_stream(317,1);
if orca.errors ~= 0
    orca.change_mode(orca.KinematicMode);
    pause(0.2);
end

orca.op_mode = orca.read_register(MODE_OF_OPERATION_address,1);
if orca.op_mode ~= orca.KinematicMode
    error('Orca not in Kinematic Mode after reset.');
end
disp('Orca in Kinematic Mode.');

orca.tune_pid_controller(8000, 400, 0, 0, 0);
disp('PID tuned.');

%% --- Motion Configuration ---
orca.configure_motion(0, 20000, 2000, 200, 1, 0, 0);  % Push
orca.configure_motion(1,     0, 1500, 200, 2, 0, 0);  % Retract
orca.configure_motion(2,     0, 1000, 200, 3, 0, 0);  % Home

%% --- Calibration Parameters ---
min_force = 7.38;  % N
max_force = 7.50;  % N
percent_margin = 0.01;  % 1%
avg_force = (min_force + max_force) / 2;
lower_bound = avg_force * (1 - percent_margin);
upper_bound = avg_force * (1 + percent_margin);

max_attempts = 10;
attempt = 0;

fprintf("Starting calibration loop...\n");

%% --- Calibration Loop ---
while attempt < max_attempts
    attempt = attempt + 1;
    fprintf("\n--- Attempt %d ---\n", attempt);

    orca.read_stream(317,1);
    if orca.errors ~= 0
        warning('Orca error detected (code %d). Resetting...', orca.errors);
        orca.change_mode(orca.KinematicMode);
        pause(0.2);
    end

    orca.op_mode = orca.read_register(MODE_OF_OPERATION_address,1);
    if orca.op_mode ~= orca.KinematicMode
        orca.change_mode(orca.KinematicMode);
        pause(0.2);
    end

    %% 1) Push
    orca.kinematic_trigger(0);
    pause(0.5);

    %% 2) Force Sampling
    num_samples = 10;
    force_samples = zeros(1, num_samples);
    for i = 1:num_samples
        orca.read_stream(SHAFT_POS_UM_address, 1);
        orca.read_stream(FORCE_REGISTER_address, 1);
        force_samples(i) = orca.force / 1000;
        fprintf("Sample %02d: %.4f N at %.0f um\n", i, force_samples(i), orca.position);
        pause(0.2);
    end

    force_N = mean(force_samples(end-4:end));
    position_um = orca.position;

    fprintf("Averaged Force (Last 5): %.4f N | Position: %.0f µm\n", force_N, position_um);

    %% 3) Check using ±1% margin
    if force_N >= lower_bound && force_N <= upper_bound
        fprintf("Force within ±1%% margin! No adjustment needed.\n");
        break;
    end

    %% 4) Retract
    orca.kinematic_trigger(1);
    t0 = tic;
    while toc(t0) < 5
        orca.read_stream(SHAFT_POS_UM_address, 1);
        if abs(orca.position) < 200
            break;
        end
        pause(0.1);
    end

    %% 5) Send to Pico
    msg = sprintf("ORCA %.4f %d", force_N, position_um);
    writeline(pico, msg);
    fprintf("Sent to Pico >%s<\n", msg);

    %% 6) Wait for Pico Response
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
                fprintf("Pico completed motor adjustment.\n");
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

%% --- Final Force Check (±1% margin)
orca.kinematic_trigger(0);
pause(0.5);
orca.read_stream(SHAFT_POS_UM_address, 1);
orca.read_stream(FORCE_REGISTER_address, 1);

final_force_N = orca.force / 1000;
fprintf("\nFinal Force: %.4f N\n", final_force_N);

orca.kinematic_trigger(2);
fprintf("Returned to zero position.\n");

if final_force_N >= lower_bound && final_force_N <= upper_bound
    fprintf("Calibration successful within ±1%% margin.\n");
else
    fprintf("Calibration incomplete after %d attempts.\n", attempt);
end
