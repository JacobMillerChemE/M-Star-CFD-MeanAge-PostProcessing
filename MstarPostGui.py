from tkinter import *
import pandas as pd
from pathlib import Path
import os.path, time


def add_mean_age(path):
    df_stats1 = pd.read_csv(path, sep='\t')
    df_stats1 = df_stats1.copy()

    df_stats1 = df_stats1[(df_stats1['Time [s]'] <= 1.3) & (df_stats1['Time [s]'] >= 0.4)]
    df_stats1 = df_stats1['Flux Age [s]']

    mean = sum(df_stats1) / len(df_stats1)
    return mean


def q_retrive(path):
    df_stats2 = pd.read_csv(path, sep='\t')
    df_stats2 = df_stats2.copy()

    df_stats2 = df_stats2[(df_stats2['Time [s]'] <= 1.3) & (df_stats2['Time [s]'] >= 0.4)]
    df_stats2 = df_stats2['Flow Rate [m^3/s]']

    q = sum(df_stats2) / len(df_stats2)
    q = "{:e}".format(q)
    return q


def particle_rt(path):
    df_stats3 = pd.read_csv(path, sep='\t', index_col=0)
    df_stats3 = df_stats3.drop(columns=["Diameter [m]", "Volume [mm^3]", "Position X [m]", "Position Y [m]",
                                        "Position Z [m]", "Velocity X [m/s]", "Velocity Y [m/s]", "Velocity Z [m/s]",
                                        "Origin [-]", "Exit Location [-]"])
    rt_list = df_stats3["Exit Time [s]"] - df_stats3["Time Added [s]"]
    rt = sum(rt_list) / len(rt_list)
    return rt


def processing():
    path = entry_1.get()
    path = Path(path.replace('\"', ''))

    df_flow = pd.DataFrame(columns=["Patient", "Flow Rate [m^3/s]"])
    df_age = pd.DataFrame(columns=["Patient", "Mean Flux Age"])
    df_particles = pd.DataFrame(columns=["Patient", "Effective Residence Time"])

    for folder in os.listdir(path):
        path_flow = os.path.join(path, folder, "out\\Stats\\InletOutlet_Inlet.txt")
        new_row_flow = [{'Patient': folder, "Flow Rate [m^3/s]": q_retrive(path_flow)}]
        df_flow = df_flow.append(new_row_flow, ignore_index=False)

        path_age = os.path.join(path, folder, "out\\Stats\\InletOutlet_Outlet.txt")
        new_row_age = [{'Patient': folder, "Mean Flux Age": add_mean_age(path_age)}]
        df_age = df_age.append(new_row_age, ignore_index=False)

        path_rt = os.path.join(path, folder, "out\\Stats\\ExitParticles.txt")
        if os.path.exists(path_rt):
            new_row_rt = [{'Patient': folder, "Effective Residence Time": particle_rt(path_rt)}]
            df_particles = df_particles.append(new_row_rt, ignore_index=False)

    df_merge = pd.DataFrame.merge(df_age, df_flow, on="Patient")
    df_final = pd.DataFrame.merge(df_merge, df_particles, on="Patient", how='outer')

    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    file_name = (entry_2.get() + ".txt")
    write_path = os.path.join(desktop, file_name)
    df_final.to_csv(write_path, sep="\t")


root = Tk()
root.title("M-Star Post Processing")

label_1 = Label(root, text="ENTER FULL PATH")
entry_1 = Entry(root)
button_1 = Button(root, text="Run", command=processing)
label_2 = Label(root, text="Enter desired output file name")
entry_2 = Entry(root)


label_1.grid(row=0, column=0)
entry_1.grid(row=0, column=1, ipadx=100)
label_2.grid(row=1, column=0)
entry_2.grid(row=1, column=1, sticky=W)
button_1.grid(row=2, column=0)

root.mainloop()


