#!/usr/bin/env python3

import sys
import argparse
import serial
import csv
from datetime import datetime
from threading import Thread, Event
import matplotlib.pyplot as plt
from itertools import count
import pandas as pd
from matplotlib.animation import FuncAnimation
import time
import numpy as np


# Parse command line args
ap = argparse.ArgumentParser()
ap.add_argument("-b", "--baud", default="9600",
                help="baud rate of serial stream, defaults to 9600")
ap.add_argument("-p", "--port", default="/dev/ttyACM0",
                help="serial port, defaults to /dev/ttyACM0")
ap.add_argument("-o", "--output", default="output.csv",
                help="file name of the output file, defaults to output.csv")
args = vars(ap.parse_args())
print(args)

# Setup Serial
port = args["port"]
baud = args["baud"]
#commented out for testing
ser = serial.Serial(port, baud)

# Setup output file
writer = csv.writer(open(args["output"], "w"))
header = ["Time Stamp", "deltaT", "t/4", "TC1", "TC2", "TC3", "TC4", "TC5", "TC6",
          "TC7", "TC8", "SET", "Error", "Int", "Der", "Ontime"]
writer.writerow(header)

# Create figure for plotting data

fig_size = plt.rcParams["figure.figsize"]
fig_size[0] = 15
fig_size[1] = 8
plt.rcParams["figure.figsize"] = fig_size
plt.style.use("fivethirtyeight")

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)



# Create lists for data
deltaT = []
# Thermocouple lists
tc1 = []
tc2 = []
tc3 = []
tc4 = []
tc5 = []
tc6 = []
tc7 = []
tc8 = []

tc_list = [tc1, tc2, tc3, tc4, tc5,tc6,tc7,tc8]
print (tc_list)
# Index of the columns for each data type in the parsed serial read
deltaT_col = 1

tc1_col = 3
tc2_col = 4
tc3_col = 5
tc4_col = 6
tc5_col = 10 
tc6_col = 9 
tc7_col = 8 
tc8_col = 7 
set_col = 11
err_col = 12

tc_cols = [tc1_col,tc2_col,tc3_col,tc4_col,
           tc5_col,tc6_col,tc7_col,tc8_col]

# Used to compute deltaT
t0 = datetime.now()

line = None
set_pt = None
error = None
# Helper function to take the raw serial data and parse it to a list
def parse_serial_read(line):
    parse_list = []

    timestamp = datetime.now().strftime("%c")
    parse_list.append(timestamp)

    # timedelta from start of data collection
    t = datetime.now() - t0
    t = int(t.total_seconds())
    parse_list.append(t)

    # parse the serial data
    line = line.decode("utf-8", errors='ignore')
    # delimited by \t 
    line_as_list=line.split('\t')

    parse_list = parse_list + line_as_list
    
    
    return parse_list

# Helper function to check for valid serial read
def validate_parse(line):

    if len(line) is not 16:
        return False

     # the first several serial reads can be 'corrupted' so discard the first 5
    if int(line[1]) < 5:
        return

    # check last 13 elements for vaild float values, discard if not valid
    valid_line = line[-13:]
    for i in range(len(valid_line)):
        try:
            valid_line[i] = float(valid_line[i])
        # print error and failed parse to console for troubleshooting
        except Exception as ex:
            print ("************* Parse failed: ********************")
        
            for x in header[1:]:
                print(x, end ="\t")
            print()
            for x in line[1:]:
                print(x, end="\t")
            print()
            print()
            
            return False

    # join list with time stamp
    valid_line = line[:3] + valid_line


    #commented out for testing
    print ("Parse success:")
        
    for x in header[1:]:
        print(x, end ="\t")
    print()
    for x in valid_line[1:]:
        print(x, end="\t")
    print()
    

    writer.writerow(valid_line)
    return (valid_line)
  

def capture_data(x,run_event):
    while run_event.is_set():
        global set_pt
        global error
        #global line
        time.sleep(.001)
        line = ser.readline().strip()
        line = parse_serial_read(line)
        if validate_parse(line):
            #print (line)
            deltaT.append(line[deltaT_col])
            tc1.append(float(line[tc1_col]))
            tc2.append(float(line[tc2_col]))
            tc3.append(float(line[tc3_col]))
            tc4.append(float(line[tc4_col]))
            tc5.append(float(line[tc5_col]))
            tc6.append(float(line[tc6_col]))
            tc7.append(float(line[tc7_col]))
            tc8.append(float(line[tc8_col]))

            set_pt = "Set Point: " + str(line[set_col])
            error = "Error: " + str(line[err_col])


# Helper function to plot the parsed data into the figure and write to csv.
def aplot_data(line):
    
    set = "Set Point: " + str(line[set_col])
    error = "Error: " + str(line[err_col])

    plt.text(0.02, 0.45, set, fontsize=14, transform=plt.gcf().transFigure)
    plt.text(0.02, 0.40, error, fontsize=14, transform=plt.gcf().transFigure)



    # add data points from line to each list
    '''
    try:
        deltaT.append(line[deltaT_col])
        #plt.plot(deltaT, tc1, label="tc1", linewidth=1)
    except Exception as e:
        print(e)
    '''
    #print(line)
    try:
        #print(float(line[tc1_col]))
        pass

    except Exception as e:
        print ("tc1 error: ")
        print(e)

 
    
    plt.plot(deltaT, tc1, "b", label="tc1", linewidth=1)
    plt.plot(deltaT, tc2, "g", label="tc2", linewidth=1)
    plt.plot(deltaT, tc3, "r", label="tc3", linewidth=1)
    plt.plot(deltaT, tc4, "y", label="tc4", linewidth=1)
    plt.plot(deltaT, tc5, "b", label="tc5", linewidth=1)
    plt.plot(deltaT, tc6, "g", label="tc6", linewidth=1)
    plt.plot(deltaT, tc7, "r", label="tc7", linewidth=1)
    plt.plot(deltaT, tc8, "y", label="tc8", linewidth=1)
    
    

    
    # write data to .csv file
    #writer.writerow(line)

def plot_data(x,run_event):
    while run_event.is_set():
            global tc_list
            global plt
            plt.cla()
            time.sleep(2)
            #n = 3
            #list2 = [sum(tc_list[0][i:i+n])//n for i in range(0,len(tc_list[0]),n)]
            #print(list2)
            

def animate(i):
    ax.clear()
    plt.cla()
    plt.plot(deltaT, tc1, "black", label="tc1", linewidth=2)
    plt.plot(deltaT, tc2, "red", label="tc2", linewidth=2)
    plt.plot(deltaT, tc3, "orangered", label="tc3", linewidth=2)
    plt.plot(deltaT, tc4, "gold", label="tc4", linewidth=2)
    plt.plot(deltaT, tc5, "green", label="tc5", linewidth=2)
    plt.plot(deltaT, tc6, "cyan", label="tc6", linewidth=2)
    plt.plot(deltaT, tc7, "navy", label="tc7", linewidth=2)
    plt.plot(deltaT, tc8, "fuchsia", label="tc8", linewidth=2)
    plt.xticks(rotation=45, ha='right')
    #fig.tight_layout()
    plt.subplots_adjust(left=0.25, top = .90, bottom = .10)
    #plt.subplots_adjust(left=0.35)
    '''
    plt.axis('auto')
    start, end = ax.get_ylim()
    print (start)
    print(end)
    ax.yaxis.set_ticks(np.arange(start, end, 10))
    '''

    plt.yticks(np.arange(0, 100, 10.0))

    plt.title('TVAC Data')
    plt.xlabel("Time (seconds)")
    plt.ylabel("Temperature (°C)")
    #plt.axis([1, None, 0, None])
    plt.legend()
    '''
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.15,
                 box.width, box.height * 0.85])
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
          fancybox=True, shadow=True, ncol=8)             
    '''
    #ax.relim()
    #yticks = [0, 150]
    #ax.set_yticks(yticks)

    if set_pt is not None:
        plt.text(0.02, 0.45, set_pt, fontsize=14, transform=plt.gcf().transFigure)
    if error is not None:
        plt.text(0.02, 0.40, error, fontsize=14, transform=plt.gcf().transFigure)
    
    plt.text(0.02, 0.90, "Press 'q' to Quit", fontsize=14, transform=plt.gcf().transFigure)
    
def onclick(event):
    if event.key in ['Q', 'q']:
        run_event.clear()
        t1.join()
        print("\nTerminating...")


if __name__ == '__main__':

    run_event = Event()
    run_event.set()
    t1 = Thread(target=capture_data, args=("thread name", run_event))
    t1.daemon = True
    t1.start()
    print ("Flushing Serial Data...")
    time.sleep(1)
    cid = fig.canvas.mpl_connect('key_press_event', onclick)
    try:  
        
        #capture_data()
        ani = FuncAnimation(fig, animate, interval=1000)
        #print(tc1)
        plt.tight_layout()
        #plt.axis('auto')
        plt.show()

        
    except KeyboardInterrupt:
        run_event.clear()
        t1.join()
        print("\nTerminating...")
        #f.close()
        pass
