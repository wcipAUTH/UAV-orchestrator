# UAV-orchestrator
## Overview
The **Orchestration of Intelligent UAVs Swarm** undetakes the task of orchestrating a swarm of UAVs to wirelessly charge a group of IoT devices (e.g., sensors) through wireless power transfer technology. The orchestration process is aimed at delivering the maximum amount of energy to the IoT devices, by taking into account the energy constraints of the UAVs.

This repository contains the code for simulating a part of the paper: https://ieeexplore.ieee.org/abstract/document/10275044. In the paper, the modeling of the system is thoroughly discussed.

 A visual abstract representation of the **Orchestration of Intelligent UAVs Swarm** mechanism is given below.

<p align="center">
<img width="563" alt="structure" src="https://github.com/wcipAUTH/UAV-orchestrator/assets/148755699/27e2dfbc-25b8-4c05-bc76-d6d1b8a8e296">
</p>


## Orchestration algorithm

The above blocks of data generation, simulated model, and UAV-orchestration algorithm are included in `orchestration_algorithm.m` and `orchestration_algorithm_given_position.m`.
The former file generates random initializations of the system, while the latter receives the initial parameters (e.g., location of UAVs and sensors) by the user.
The output of the `orchestration_algorithm_given_position.m` is the assignment of the UAVs to charge specific sensors into the field of interest. This result is fed to the GUI, which produces a visual representation of the system.

## GUI
The GUI, `emulator_dashboard.py`,  is a user-friendly visualization which depicts the final and the initial UAVs positions, as well as the final energy coverage that the UAVs provide to the sensors. 

Among others, somw basic functionalities of the GUI are described below. By pressing the “Devices' locations” button, the positions of the sensors and the UAVs appear into the field of interest, which is highlighted with boundaries. Moreover, each sensor and UAV is associated with an identity which is visible to the user, as depicted below

<p align="center">
<img width="560" alt="image" src="https://github.com/wcipAUTH/UAV-orchestrator/assets/148755699/dde47fc6-3495-4e90-b698-13651ea09848">
</p>

At first, all sensors (ID) are denoted with a red marker, while the UAVs with a black marker and white inner circle. By pressing the “Run UAV Orchestrator” button, each UAV is relocating towards the vicinity of the sensors that is assigned to charge. Sensors that now match the new color of each UAV are being recharged by the corresponding UAVs, as depicted below.

![image](https://github.com/wcipAUTH/UAV-orchestrator/assets/148755699/70ca6054-1ac1-44c1-80e7-70bd5f9cd993)

Finally, the user can reset the environment by pressing the “Reset” button. In this stage, only the energy requirements of the sensors are visible to the user, as the assignment of the UAVs has not been initiated yet. 
