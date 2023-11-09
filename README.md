# UAV-orchestrator
## Overview
The UAV-orchestrator undetakes the task to orchestrate a swarm of UAVs to wirelessly charge a group of IoT devices (e.g., sensors) through wireless power transfer technology. The orchestration process is aimed at delivering the maximum amount of energy to the IoT devices, by taking into account the energy constraints of the UAVs.

This repository contains the code for simulating a part of the paper: https://ieeexplore.ieee.org/abstract/document/10275044. In the paper, the modeling of the system is thoroughly discussed.

Also, a GUI is included ([emulator_dashboard.py](https://github.com/wcipAUTH/UAV-orchestrator/blob/main/emulator_dashboard.py)), which visualises the orchestration of the UAVs into the field of interest.

## Orchestration algorithm
The UAV orchestrator is a versatile framework designed for the efficient orchestration of a UAV swarms in supporting wireless power transfer within IoT devices and the promoting green energy practices in precision agriculture. A visual abstract representation is given below

![image](https://github.com/wcipAUTH/UAV-orchestrator/assets/148755699/dbe0d058-68b7-48ad-bc17-2dee809f9267)

The initial component of the UAV emulator defines the simulated model and environment. This includes defining the field's dimensions, sensor locations, initial UAV positions, and other relevant parameters. 

The second block describes the simulated environment, which receives the initialization as an input. Given the simulated environment, the UAV orchestration algorithm follows, which is depicted in the third block. The latter was developed based on the solid mathematical, and outputs the optimal UAV-IoT devices assignment subject to the given parameters

The GUI is a user-friendly visualization which depicts the final and the initial UAVs positions, as well as the final energy coverage that the UAVs provide to the sensors

## GUI
