#!/usr/bin/python
 
import tkinter as tk
from json import load as json_load
from sys import exit
from tkinter.constants import NW, RIGHT, SUNKEN, TOP
import time
from pythonping import ping
import threading
from winsound import Beep

def main():
    dataset = ""
    OverwatchThreadList = []

    # Handle Closing
    def on_closing():
        window.destroy();
        exit()

    # Create thread to overwatch hostname
    def Overwatch(entryset, label):
        global dataset
        hostname = str(entryset["hostname"])
        pingrate = entryset["ping_rate"]   
        next_beep = 0

        while 1:
            try:
                result = ping(hostname, verbose=False, timeout=10)
                result_avg = int(result.rtt_avg * 1000)
                label["text"] = str(result_avg) + "MS"
                if (result_avg > 250):
                    if dataset["beeping"]:
                        if next_beep < time.time() * 1000:
                            # Beep Every 60 Seconds
                            next_beep = int(time.time() * 1000) + dataset["beeping_time_between"]
                            Beep(dataset["beeping_freq"], dataset["beeping_duration"])
                    label["bg"] = "red"
                elif (result_avg > 100):
                    label["bg"] = "yellow"
                elif (result_avg < 100):
                    label["bg"] = "green"
            except:
                if dataset["beeping"]:
                    if next_beep < time.time() * 1000:
                        # Beep Every 60 Seconds
                        next_beep = int(time.time() * 1000) + dataset["beeping_time_between"]
                        Beep(dataset["beeping_freq"], dataset["beeping_duration"])

                label["text"] = "Not Reachable"
                label["bg"] = "red"
        
            time.sleep(pingrate/1000)

    # Load Data from file
    def LoadData():
        global dataset
        try:
            with open("data.json") as json_file:
                json_data = json_load(json_file)
                print("data loaded successfully")
                print("dataset name" + str(json_data["name"]))
                print("dataset version " + str(json_data["version"]))
                print("dataset count " + str(len(json_data["data"])))
                print("dataset beeping enabled : " + str(json_data["beeping"]))
                print("dataset beeping_time_between : " + str(json_data["beeping_time_between"]))
                print("dataset beeping_freq : " + str(json_data["beeping_freq"]))
                print("dataset beeping_duration : " + str(json_data["beeping_duration"]))
                dataset = json_data
        except:
            print("cannot load data...")
            exit(-1)

    # Setup Window
    def SetupGUI(_window):
        global dataset
        _window.title("Stahlgruber - PingOverview")
        _window.resizable(False, False)

        # Loop over elements
        for i in range(len(dataset["data"])):
            lbl_entry = tk.Label(master=_window, text=dataset["data"][i]["hostname"])
            lbl_entry.grid(row=(i+1), column=0, stick=NW, padx=3, pady=3)
            lbl_ping = tk.Label(master=_window, text="LAST_PING", relief=SUNKEN)
            lbl_ping.grid(row=(i+1), column=1, stick=NW, padx=3, pady=3)
            overwatch_thread = threading.Thread(target=Overwatch, daemon=True, args=(dataset["data"][i], lbl_ping))
            overwatch_thread.start()
            OverwatchThreadList.append(overwatch_thread)

    # Startup
    window = tk.Tk()

    LoadData()
    SetupGUI(window)

    window.protocol("WM_DELETE_WINDOW", on_closing)
    window.mainloop()

if __name__ == "__main__":
    main()