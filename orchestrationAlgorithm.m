%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%  UAV-swarm Orchestrator  %%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

clc
close all
clear all

%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% INITIALIZATIONS
%%%%%%%%%%%%%%%%%%%%%%%%%%%

%number of UAVs
U = 8;

%number of cells (or CSs)
C = 4;

%number of IoT devices (IDs)
N = 20;

%number of Monte Carlo iterations
monte_carlo_iters = 100;


%cell quota (maximum number of UAVs assigned into a cell)
quota = 3*ones(1,C);

%WPT and RF EH parameters
a_exp = 2;                %path-loss exponent
UAV_Ptrans = 5;           %WPT transmission power in Watt
height = 1;               %Height while WPT
theta = 40;               %degrees
antennaGain = 29000/theta^2;      %antenna gain

%%%%%%%%%%% Real implementation %%%%%%%%%%%%%%%
%read positions from .csv file
ID_positions = readmatrix('Files\sensors_positions.csv');
origin = [40.343278, 22.595930, 0];

for i = 1:length(ID_positions)
    arclen(i) = distance([40.343278, 22.595930], [ID_positions(i,1), ID_positions(i,2)]);
end
dist_m = deg2km(arclen)*10^3;

%Convert to cartesian coordinates relative to the origin (the origin corresponds to (0,0) )
[pos_xx, pos_yy] = latlon2local(ID_positions(:,1), ID_positions(:,2), 0, origin);

%Assume a cartesian plane (field): x*y
x = 600;
y = 700;

%maximum energy demand of the IoT devices
maxDemand = linspace(0.005, 0.05, 10);

%initializations
average_coverage_proposed = zeros(1, length(maxDemand));
average_coverage_baseline = zeros(1, length(maxDemand));

for demand=1:length(maxDemand)
    
%initializations
av_per_proposed = 0;
av_per_baseline = 0;

for iterations=1:monte_carlo_iters

%generate position of IDs randomly
pos_x = -x/2 + x*rand(N,1);
pos_y = -y/2 + y*rand(N,1);
pos = [pos_x, pos_y];

%generate initial position of UAVs randomly
UAV_pos_x = -x/2 + x*rand(U,1);
UAV_pos_y = -y/2 + y*rand(U,1);
UAV_pos = [UAV_pos_x, UAV_pos_y];

%cell center position (assuming 4 cells)
cell_pos = [x/4, y/4; -x/4, y/4; -x/4, -y/4; x/4, -y/4];

%distance among IDs and cell centers
ID_cellDistance = ones(N,C);
for i=1:N
    for j=1:C
        ID_cellDistance(i,j) = norm(pos(i,:) - cell_pos(j,:));
    end
end

%association among IDs and cells
ID_cellAssociation = zeros(N,1);
N_cell = zeros(C,1);            %number of IDs in a cell

for i=1:N
    [unused ID_cellAssociation(i)] = min(ID_cellDistance(i,:));
    N_cell(ID_cellAssociation(i)) = N_cell(ID_cellAssociation(i)) + 1;   %number of IDs in each cell
end

%BM is a Binary Matrix indicating ID-cell association
BM = zeros(N,C);
for i=1:N
    BM(i,ID_cellAssociation(i))=1;
end

%cell area
cell_area = ones(C,1);
cell_area = (x*y/4)*cell_area;

%maximum energy of UAVs in Wh
E_f = 120 + 60*rand(1,U);

%define some parameters
WPT_eff = 0.6;                %RF-to-DC conversion efficiency
Path_loss = height^-a_exp;
G = 10^-3*WPT_eff*Path_loss*antennaGain;       %The channel gain while WPTing
UAV_speed = 10;                       %We assume that the UAV flies with 10m/s (35kmh)
Flying_cons = 350;                    %This is the energy consumption in Wh while the UAV flies at UAV_speed=10m/s.
Hover_cons = 300;                     %This is the energy consumption in Wh while the UAV hovers.
r = UAV_Ptrans / Hover_cons;          %WPTtransmit to hover ratio (r in paper)

%ID density per area (in IDs per m^2)
cell_ID_density = N_cell./cell_area;
ID_average_distance = 1./(2*sqrt(cell_ID_density));
Time2ReachNeighbor = ID_average_distance/UAV_speed; % T2RN is given in sec.
e = Time2ReachNeighbor*Flying_cons/3600; %Transit cost for a ID to ID movement (in each cell), \epsilon_c in paper

for i=1:length(e)
    if e(i)==inf
         e(i) = 0;
    end
end
 
%energy demands of IDs in Wh
E_d = maxDemand(demand)*rand(1,N);

%Energy for relocation matrix
E_r = ones(U,C);
for i=1:U
    for j=1:C
        E_r(i,j) = ((norm(UAV_pos(i,:) - cell_pos(j,:))) / UAV_speed)*(Flying_cons / 3600); %Energy cost for relocation in Wh 
    end
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%  OPTIMIZATION PROCESS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
lb = zeros(1, C + U*C);
ub = ones(1, C + U*C);
ub(1:C) = 10^4;

%Initialize matrix A and vector b for intlinprog
A = zeros(C + U + C, C+U*C);
b = zeros(C + U + C, 1);

%C1
for i=1:C
    A(i, (i-1)*U+C+1:C+U+(i-1)*U) = 1;
    b(i) = quota(i);
end

%C2
for i=1:U
    for j=1:C
        A(C + i, C + i + (j-1)*U) = 1;
        b(C + i) = 1;
    end
end

%C3
for j=1:C
    sum2 = 0;
    for i=1:N
        sum2 = sum2 + BM(i,j)*E_d(i);
    end
    b(C + U + j) = - sum2 - ((G*r)/(r+1))*e(j)*(N_cell(j) - 1);
    A(C + U + j, j) = -1;
    for i=1:U
        A(C + U + j, C + i + (j-1)*U) = - ((G*r)/(r+1))*( E_f(i) - e(j) - E_r(i,j));
    end
end

%initialize optimization vector x0
%First, create an auxiliary UAV-CELL association binary matrix, AA
AA = zeros(U, C);
choice = 1:C;       %choice indicates the available cells
current_quota = zeros(1, C); 
for i=1:U  % for every UAV do
    while ( sum(AA(i,:))==0 )   %while not assigned in a cell
        c = randi(length(choice));  %randomly select a cell
        if current_quota(choice(c)) < quota(choice(c))  %if its not full go there
            AA(i, choice(c)) = 1;
            current_quota(choice(c)) = current_quota(choice(c)) + 1; %update the current quota (+ 1)
        else
            choice(c) = []; %else the cell is full, remove this cell as an option
        end
    end
end
AA_random = AA;
AA = reshape(AA, [U*C, 1]);
x0 = zeros(C + U*C, 1);
x0 = [ones(C, 1); AA];

%objective function coefficients
f = zeros(U*C + C, 1);
f(1:C) = 1;

%binary variable x, size: U * C, form: (y_1, y_2, ..., y_C, a{1,1}, ..., a{U,1}, a{1,2}, ..., a{U,C})
[vector, obj_value, exitflag] = intlinprog( f, ((C+1):(C + U*C)), A, b, [], [], lb, ub, x0);
obj_value;
coverage_percentage = (sum(E_d) - obj_value )/sum(E_d);


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% UAV-cell ASSIGNMENT OUTPUT %%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

v = vector(C+1:end);
%final assignment matrix
Assignment = reshape(v, [U, C]);


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% BASELINE SCHEME %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
UAV_cellDistance = ones(U,C);
sorted = ones(U,C);
for i=1:U
    for j=1:C
        UAV_cellDistance(i,j) = norm(UAV_pos(i,:) - cell_pos(j,:));
    end
end

%UAV - cell association matrix for the baseline scheme
AA = zeros(U, C);
for i = 1:U
    %sort the UAV-cell distance in ascending order and save the order
    [sorted(i,:) order(i,:)]= sort(UAV_cellDistance(i,:), 'ascend');
end

for i=1:U
    j = 1;
    while (j <= C)
        if sum(AA(1:U, order(i,j))) < quota(order(i,j))
            AA(i, order(i,j)) = 1;
            break
        end
        j = j + 1;
    end
end

%caclulate objective function for the baseline matching
overall_sum = 0;
for j=1:C
aux = 0;
sum1 = 0;
for i=1:U
    sum1 = sum1 + AA(i,j)*( E_f(i) - E_r(i,j) - e(j) );
end
aux = ( G*r/(r+1) )*(sum1 - e(j)*(N_cell(j) - 1));

sum2 = 0;
for i=1:N
    sum2 = sum2 + BM(i,j)*E_d(i);
end

aux = sum2 - aux;
overall_sum = overall_sum + max(aux, 0);
end
obj_value_baseline = overall_sum;

%energy coverage percentage of the baseline algorithm
coverage_percentage_baseline = (sum(E_d) - obj_value_baseline)/sum(E_d);

%average over the M iterations
av_per_proposed = av_per_proposed + coverage_percentage;
av_per_baseline = av_per_baseline + coverage_percentage_baseline;

end

%calculate the average for the respective energy demand
average_coverage_proposed(demand) = av_per_proposed/monte_carlo_iters;
average_coverage_baseline(demand) = av_per_baseline/monte_carlo_iters;

end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% FIGURES
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
figure(1)
plot(10^3*maxDemand, 100*average_coverage_proposed, '-ok', 'Linewidth', 1.5)
hold on
plot(10^3*maxDemand, 100*average_coverage_baseline, '-vr', 'Linewidth', 1.5)
xlim([5 50])
xlabel('Maximum energy need per sensor(mWh)')
ylabel('Average energy coverage of sensors(%)')
legend('Proposed UAV-orchestration algorithm','Greedy UAV-orchestration algorithm')
grid on