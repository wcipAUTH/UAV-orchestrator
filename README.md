# UAV-orchestrator
## Overview
The UAV-orchestrator undetakes the task to orchestrate a swarm of UAVs to wirelessly charge a group of IoT devices (e.g., sensors) through wireless power transfer technology. The orchestration process is aimed at delivering the maximum amount of energy to the IoT devices, by taking into account the energy constraints of the UAVs.

This repository contains the code for simulating a part of the paper: https://ieeexplore.ieee.org/abstract/document/10275044. In the paper, the modeling of the system is thoroughly discussed.

Also, a GUI is included `emulator_dashboard.py`, which visualises the orchestration of the UAVs into the field of interest. A visual abstract representation of the main components is given below

<img width="563" alt="structure" src="https://github.com/wcipAUTH/UAV-orchestrator/assets/148755699/f086612f-66e6-49e7-b658-450c0795b907">


## Orchestration algorithm

The above blocks of data generation, simulated environment, and UAV-orchestration algorithm are included in
The initial blocks define the simulated model and environment. This includes defining the field's dimensions, sensor locations, initial UAV positions, and other relevant parameters, which are given as inputs to the orchestration algorithm. The input parameters can be either real-time data, given as a .csv file, or any other format, or simulated data. Both options are supported.

The second block describes the simulated environment, which receives the initialization as an input. Given the simulated environment, the UAV orchestration algorithm follows, which is depicted in the third block. The latter was developed based on the solid mathematical, and outputs the optimal UAV-IoT devices assignment subject to the given parameters. Two orchestration algorithms are available. The first is based on linear programming, and the latter on game theory, and specifically matching with externalities.

## GUI
The GUI is a user-friendly visualization which depicts the final and the initial UAVs positions, as well as the final energy coverage that the UAVs provide to the sensors. The GUI is based on the custom tkinter library. 

By pressing the “Devices locations” button, the positions of the sensors and the UAVs appear into the field of interest, which is highlighted with boundaries. Moreover, each sensor and UAV is associated with an identity which is visible to the user, as depicted below

![image](https://github.com/wcipAUTH/UAV-orchestrator/assets/148755699/52b007c7-847d-4130-b3cd-99d9c766b4f9)

At first, all IoT nodes are red, while all UAVs are black. By pressing the “Run UAV Orchestrator” button, each UAV is relocating towards the vicinity of the sensors that is assigned to charge. Sensors that now match the new color of each UAV are being recharged by the corresponding UAVs, as depicted below

![image](https://github.com/wcipAUTH/UAV-orchestrator/assets/148755699/70ca6054-1ac1-44c1-80e7-70bd5f9cd993)

Finally, the user can reset the environment by pressing the “Reset” button. In this stage, only the energy requirement of the sensors are visible to the user, as the assignment of the UAVs has not been initiated yet. 
