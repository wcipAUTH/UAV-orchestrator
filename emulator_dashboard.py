import customtkinter
from tkintermapview import TkinterMapView
#import pandas as pd
import numpy as np
from numpy import genfromtxt
from haversine import haversine
import time
from PIL import ImageTk, Image
#from math import sin, cos, sqrt, atan2, radians
#import mpu
#import geopy.distance

#customtkinter.set_default_color_theme("blue")


class App(customtkinter.CTk):

    APP_NAME = "UAV Orchestrator"
    WIDTH = 900
    HEIGHT = 500
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title(App.APP_NAME)
        self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
        self.minsize(App.WIDTH, App.HEIGHT)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Command-q>", self.on_closing)
        self.bind("<Command-w>", self.on_closing)
        self.createcommand('tk::mac::Quit', self.on_closing)

        self.marker_list = []
        self.uav_marker_list = []
        self.UAVinit_list = []
        self.UAVcurrent_list = []

        # ============ create two CTkFrames ============

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self, width=150, corner_radius=0, fg_color=None)
        self.frame_left.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        self.frame_right = customtkinter.CTkFrame(master=self, corner_radius=0)
        self.frame_right.grid(row=0, column=1, rowspan=1, pady=0, padx=0, sticky="nsew")

        # ============ frame_left ============

        self.frame_left.grid_rowconfigure(2, weight=1)

        self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Run UAV Orchestrator",
                                                command=self.set_marker_event)
        self.button_1.grid(pady=(20, 0), padx=(20, 20), row=0, column=0)
        

        self.button_2 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Reset",
                                                command=self.clear_marker_event)
        self.button_2.grid(pady=(20, 0), padx=(20, 20), row=1, column=0)
        
        self.button_3 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Devices locations",
                                                command=self.set_ID_event)
        self.button_3.grid(pady=(0, 0), padx=(20, 20), row=2, column=0)
        
        sensors_array = genfromtxt('Files/sensors_positions.csv',delimiter=',')
        val = []
        for i in range(len(sensors_array)):
            val.append("ID#"+str(i+1))
        self.button_4 = customtkinter.CTkLabel(master=self.frame_left,
                                                 text="Sensors energy:", anchor="w")
        self.button_4.grid(pady=(20, 0), padx=(20, 20), row=3, column=0)
        
        
        self.button4_option_menu = customtkinter.CTkOptionMenu(self.frame_left, values=val, command=self.create_window)
        self.button4_option_menu.grid(row=4, column=0, padx=(20, 20), pady=(10, 0))
        
        self.map_label = customtkinter.CTkLabel(self.frame_left, text="Tile Server:", anchor="w")
        self.map_label.grid(row=5, column=0, padx=(20, 20), pady=(20, 0))
        self.map_option_menu = customtkinter.CTkOptionMenu(self.frame_left, values=["OpenStreetMap", "Google normal", "Google satellite"],
                                                                       command=self.change_map)
        self.map_option_menu.grid(row=6, column=0, padx=(20, 20), pady=(10, 0))

        self.appearance_mode_label = customtkinter.CTkLabel(self.frame_left, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=7, column=0, padx=(20, 20), pady=(20, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.frame_left, values=["Light", "Dark"],
                                                                       command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.grid(row=8, column=0, padx=(20, 20), pady=(10, 20))

        # ============ frame_right ============

        self.frame_right.grid_rowconfigure(1, weight=1)
        self.frame_right.grid_rowconfigure(0, weight=0)
        self.frame_right.grid_columnconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(1, weight=0)
        self.frame_right.grid_columnconfigure(2, weight=1)

        self.map_widget = TkinterMapView(self.frame_right, corner_radius=0)
        self.map_widget.grid(row=1, rowspan=1, column=0, columnspan=3, sticky="nswe", padx=(0, 0), pady=(0, 0))
        

        self.entry = customtkinter.CTkEntry(master=self.frame_right,
                                            placeholder_text="type address")
        self.entry.grid(row=0, column=0, sticky="we", padx=(12, 0), pady=12)
        self.entry.bind("<Return>", self.search_event)

        self.button_5 = customtkinter.CTkButton(master=self.frame_right,
                                                text="Search",
                                                width=90,
                                                command=self.search_event)
        self.button_5.grid(row=0, column=1, sticky="w", padx=(12, 0), pady=12)
        
        #TERMINET logo
        self.logo = ImageTk.PhotoImage(Image.open("images/terminet_logo2.png").resize((100,100)))
        self.label = customtkinter.CTkLabel(master=self.frame_right, text="Search", image=self.logo)
        self.label.grid(row=0, column=2, sticky="w", padx=(350, 0), pady=12)

        # Set default values
        self.map_widget.set_position(40.343140, 22.595897)  #AFS's premises
        self.map_option_menu.set("OpenStreetMap")
        self.appearance_mode_optionemenu.set("Light")
        
        #flag for delivered energy in panel
        self.flag = 0
        
        #flag for energy demand
        self.flag2 = 0
        
    def search_event(self, event=None):
        self.map_widget.set_address(self.entry.get())

    def set_marker_event(self):
        if self.flag2 == 0:
            pass
        else:
            self.flag = 1
            sensors_array = genfromtxt('Files/sensors_positions.csv',delimiter=',')
            #self.map_widget.set_position(40.343140, 22.595897)  #AFS's premises
            
            #read UAV initial positions
            UAVinit_array = genfromtxt('Files/uav_initial_position.csv',delimiter=',')
            
            #first we delete the initial ID (red) markers
            for marker in self.marker_list:
                marker.delete()
                
            cell_centers = genfromtxt('Files/cell_centers.csv',delimiter=',')
            
            #distances among IDs and cell centers
            ID_cell_distances = np.zeros((len(sensors_array), len(cell_centers)))
            for i in range(len(sensors_array)):
                for j in range(len(cell_centers)):
                    ID_cell_distances[i,j] = haversine(sensors_array[i,:], cell_centers[j,:])
                    
            #ID - cell association vector        
            ID_cell_association =  np.zeros((len(sensors_array), 1))
            for i in range(len(sensors_array)):
                ID_cell_association[i] = np.argmin(ID_cell_distances[i,:])
                
                #set the ID markers with the color of the associated cell
                if (ID_cell_association[i]==0):
                    self.marker_list.append(self.map_widget.set_marker(sensors_array[i,0], sensors_array[i,1], marker_color_outside="blue", marker_color_circle="blue", text="ID#"+str(i+1), font=10))
                if (ID_cell_association[i]==1):
                    self.marker_list.append(self.map_widget.set_marker(sensors_array[i,0], sensors_array[i,1], marker_color_outside="orange", marker_color_circle="orange", text="ID#"+str(i+1), font=10))
                if (ID_cell_association[i]==2):
                    self.marker_list.append(self.map_widget.set_marker(sensors_array[i,0], sensors_array[i,1], marker_color_outside="green", marker_color_circle="green", text="ID#"+str(i+1), font=10))
                if (ID_cell_association[i]==3):
                    self.marker_list.append(self.map_widget.set_marker(sensors_array[i,0], sensors_array[i,1], marker_color_outside="yellow", marker_color_circle="yellow", text="ID#"+str(i+1), font=10))
                    
            ###########   UAVs ###################
            
            #read UAV-cell assignment
            uavs_array = genfromtxt('Files/uavs.csv',delimiter=',')
            df2 = np.zeros((4, 1)) # number of UAVs within each cluster
            for cluster in range(1,5):
                
                counter=0;
                for index in range(0,len(uavs_array)):
                    if int(uavs_array[index,1])==cluster:
                        counter = counter + 1
                df2[cluster-1,0] = counter
            
            UAVs=0
            for index in range(0,len(df2)):
                UAVs=UAVs+df2[index,0]
            
            
            #UAVs final positions (in cell centers)
            uavs_coordinates=np.zeros((int(UAVs), 2))
            for drone in range(0,len(uavs_array)):
                if uavs_array[drone,1]==1:
                    uavs_coordinates[drone,0]= 40.345467 + np.random.normal(0,0.0006,1)
                    uavs_coordinates[drone,1]= 22.594981 + np.random.normal(0,0.0006,1)
                if uavs_array[drone,1]==2:
                    uavs_coordinates[drone,0]= 40.342524 - np.random.normal(0,0.0006,1)
                    uavs_coordinates[drone,1]= 22.592986 - np.random.normal(0,0.0006,1)
                if uavs_array[drone,1]==3:
                    uavs_coordinates[drone,0]= 40.344103 + np.random.normal(0,0.0006,1)
                    uavs_coordinates[drone,1]= 22.598356 + np.random.normal(0,0.0006,1)
                if uavs_array[drone,1]==4:
                    uavs_coordinates[drone,0]= 40.340965 - np.random.normal(0,0.0006,1)
                    uavs_coordinates[drone,1]= 22.596259 - np.random.normal(0,0.0006,1)
            
            UAV_distance_to_travel = np.zeros(len(uavs_array))
            for i in range(len(uavs_array)):
                    UAV_distance_to_travel[i] = haversine(UAVinit_array[i,:], uavs_coordinates[i,:])
            
            #create UAV trajectories
            UAV_distance_to_travel = np.zeros(len(uavs_array))
            aux = np.zeros(len(uavs_array))
            for i in range(len(uavs_array)):
                    UAV_distance_to_travel[i] = haversine(UAVinit_array[i,:], uavs_coordinates[i,:])
                    #aux is the points needed when travelling with velocity 10 m/s
                    aux[i] = UAV_distance_to_travel[i]/0.01
                    aux[i] = np.ceil(aux[i])
    
            theta = np.zeros((len(uavs_array), int(np.max(aux))))
            for i in range(len(uavs_array)):
                #th_aux1 is the trajecroy of the given UAV
                th_aux1 = np.linspace(0, 1, num=int(aux[i]))
                #th_aux2 is only ones vector, .i.e, the UAV is not moving (the other UAVS may still move)
                th_aux2 = np.ones(int(theta.shape[1]) - int(len(th_aux1)))
                theta[i,:] = np.concatenate((th_aux1, th_aux2))
    
            #create UAVs trajectory
            UAV_traj_x = np.zeros((len(uavs_array), int(theta.shape[1])))
            UAV_traj_y = np.zeros((len(uavs_array), int(theta.shape[1])))
            for i in range(0,len(uavs_array)):
                for j in range(0,int(theta.shape[1])):
                    UAV_traj_x[i,j] = (1-theta[i,j])*UAVinit_array[i,0] + (theta[i,j])*uavs_coordinates[i,0]
                    UAV_traj_y[i,j] = (1-theta[i,j])*UAVinit_array[i,1] + (theta[i,j])*uavs_coordinates[i,1]
            
            #sleep for some time to create the moving effect
            self.UAVcurrent_list = self.UAVinit_list
            for i in range(int(theta.shape[1])):
                self.set_UAV_current_pos(UAV_traj_x, UAV_traj_y,i)
                t = 200
                self.tksleep(t)
                
            #use this mainloop, otherwise the map is not updated
            self.mainloop()
        
    def set_ID_event(self):
        
        self.flag2 = 1
        #read the field boundaries and plot them
        field_boundaries_array = genfromtxt('Files/field_boundaries.csv',delimiter=',')
        self.polygon = self.map_widget.set_polygon([(field_boundaries_array[0,0], field_boundaries_array[0,1]),
                                    (field_boundaries_array[1,0], field_boundaries_array[1,1]),
                                    (field_boundaries_array[2,0], field_boundaries_array[2,1]),
                                    (field_boundaries_array[3,0], field_boundaries_array[3,1]),
                                    ],
                                   name="polygon")
        
        #read sensors positions
        sensors_array = genfromtxt('Files/sensors_positions.csv',delimiter=',')
        #create list with sensors and set markers
        for i in range (0,len(sensors_array)):
            self.marker_list.append(self.map_widget.set_marker(sensors_array[i,0], sensors_array[i,1], text="ID#"+str(i+1), font=10))
            
        #read UAV initial positions
        UAVinit_array = genfromtxt('Files/uav_initial_position.csv',delimiter=',')
        #create list with UAVs init. positions and set markers
        for j in range (0,len(UAVinit_array)):
            self.UAVinit_list.append(self.map_widget.set_marker(UAVinit_array[j,0], UAVinit_array[j,1], text="UAV#"+str(j+1), marker_color_outside="black", marker_color_circle="white"))
        

    def clear_marker_event(self):
        
        self.flag = 0
        self.flag2 = 0
        #delete UAV markers
        for marker in self.uav_marker_list:
            marker.delete()
            
        #delete initial UAV markers
        for marker in self.UAVinit_list:
            marker.delete()   
            
        #delete IDs markers and polygon
        for marker in self.marker_list:
            marker.delete()
            self.polygon.delete()
        
    def change_appearance_mode(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_map(self, new_map: str):
        if new_map == "OpenStreetMap":
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif new_map == "Google normal":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        elif new_map == "Google satellite":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()
    
    def set_UAV_current_pos(self, UAV_traj_x, UAV_traj_y,i):
        uavs_array = genfromtxt('Files/uavs.csv',delimiter=',')
        ii=-1
        for marker in self.UAVcurrent_list:
            marker.delete()
            
        uavs_array = genfromtxt('Files/uavs.csv',delimiter=',')
        for ii in range (0,len(uavs_array)): 
              if uavs_array[ii,1]==1:
                  self.UAVcurrent_list.append(self.map_widget.set_marker(UAV_traj_x[ii,i], UAV_traj_y[ii,i], text="UAV#"+str(ii+1), marker_color_outside="blue", marker_color_circle="white"))
              if uavs_array[ii,1]==2:
                  self.UAVcurrent_list.append(self.map_widget.set_marker(UAV_traj_x[ii,i], UAV_traj_y[ii,i], text="UAV#"+str(ii+1), marker_color_outside="orange", marker_color_circle="white"))
              if uavs_array[ii,1]==3:
                  self.UAVcurrent_list.append(self.map_widget.set_marker(UAV_traj_x[ii,i], UAV_traj_y[ii,i], text="UAV#"+str(ii+1), marker_color_outside="green", marker_color_circle="white"))
              if uavs_array[ii,1]==4:
                  self.UAVcurrent_list.append(self.map_widget.set_marker(UAV_traj_x[ii,i], UAV_traj_y[ii,i], text="UAV#"+str(ii+1), marker_color_outside="yellow", marker_color_circle="white"))

    def tksleep(self, time: float) -> None:
        self.after(int(time), self.quit)
        self.mainloop()
        
    def create_window(self, ID: str):
        sensors_array = genfromtxt('Files/sensors_positions.csv',delimiter=',')
        sensors_energy_demand = 1000*genfromtxt('Files/sensors_energy_demand.csv',delimiter=',')
        sensors_energy_delivered = 1000*genfromtxt('Files/sensors_energy_delivered.csv',delimiter=',')

        for i in range(len(sensors_array)):
            if ID == "ID#"+str(i+1):
                window = customtkinter.CTkToplevel(self)
                window.geometry("400x200")
                window.title("IoT Device#"+str(i+1))
                textbox1 = customtkinter.CTkTextbox(window)
                textbox1.grid(row=0, column=0)
                textbox2 = customtkinter.CTkTextbox(window)
                textbox2.grid(row=0, column=1)
                if (self.flag2==1):
                    textbox1.insert("0.0","Energy need:   {:.2f}".format(sensors_energy_demand[i])+"  mWh")
                    textbox1.configure(state="disabled")
                else:
                    textbox1.insert("0.0","Energy need:  Please set positions")
                    textbox1.configure(state="disabled")
                if (self.flag==1):
                    textbox2.insert("0.0","Energy delivered:  {:.2f}".format(sensors_energy_delivered[i])+"  mWh")
                    textbox2.configure(state="disabled")
                else:
                    textbox2.insert("0.0","Energy delivered:  Please Run Uav Orchestrator")
                    textbox2.configure(state="disabled")
                break
       
        
        
if __name__ == "__main__":
    app = App()
    app.start()
