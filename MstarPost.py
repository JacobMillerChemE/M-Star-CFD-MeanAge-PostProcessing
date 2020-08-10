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


run = True

while run:

    path = input("Please enter file or directory path: ")
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
    file_name = str(input("What would you like to name the output file?: ") + ".txt")
    write_path = os.path.join(desktop, file_name)
    df_final.to_csv(write_path, sep="\t")
    print(f"Your data has been saved to the Desktop as {file_name}.")

    run_again = input("Press 1 to run again and 2 to exit: ")

    if run_again == "1":
        run = True
    elif run_again == "2":
        run = False