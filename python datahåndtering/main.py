import csv
import matplotlib.pyplot as plt
import sys
import re
import os
import matplotlib.colors as mcolors
from tqdm import tqdm

print("Processing config...")

keys = {
        "in": 0,
        "out": 0,
        "iscale": 0.001,
        "oscale": 1,
        "start": 0,
        "end": 1000,
        "oo": [],
        "yscale": [],
        "xlabel": "t",
        "ylabel": [],
        "curves": [],
        }

cfile = "config.txt"
if "-c" in sys.argv:
    cfile = sys.argv[sys.argv.index("-c") + 1]

if not os.path.isfile(cfile):
    print(f"Error: given config file \"{cfile}\" does not exist, exiting...")
    sys.exit()


with open(cfile, "r") as f:
    for l in f:
        sl = l.split(": ")
        if sl[0] == "oo":
            for oo in sl[1].split(","):
                keys["oo"].append(oo.strip())
        elif sl[0] == "curves":
            for label in sl[1].split(","):
                keys["curves"].append(label.strip())
        elif sl[0] == "yscale":
            for label in sl[1].split(","):
                keys["yscale"].append(float(label.strip()))
        elif sl[0] == "ylabel":
            for label in sl[1].split(","):
                keys["ylabel"].append(label.strip())
        elif sl[0] in keys:
            keys[sl[0]] = sl[1].strip()
        else:
            print(f"Warning: key \"{sl[0]}\" is not valid, continuing...")

if keys["oscale"] < keys["iscale"]:
    print("Error: out scale is larger than in scale, unable to create precision that doesn't exist, exiting...")
if keys["start"] > keys["end"]:
    print("Error: start time is larger that end time, exiting...")
if len(keys["oo"]) == 0 and "show" not in sys.argv:
    print("Warning: No output options or \"show\" command, program will produce no output, continuing...")

print("Done!\n\nProcessing input csv file...")

n_lines = 0
with open(keys["in"], "rb") as f:
    n_lines = sum(1 for _ in f)
n_lines -= 1

maxi = 0
vals = []
with open(keys["in"], newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    colnames = []
    colnames_o = []
    for i,col in enumerate(next(reader)):
        if "t0" in col or "tInc" in col or len(col) == 0:
            continue
        else:
            colnames.append(col)
        if i >= len(keys["curves"]):
            colnames_o.append(col)
        else:
            colnames_o.append(keys["curves"][i])
    for i,row in tqdm(enumerate(reader), total=n_lines):
        vals.append({colnames_o[i]: row[colnames[i]] for i in range(len(colnames_o))})
        maxi = i

stepsize = int(float(keys["oscale"]) / float(keys["iscale"]))
s_start = int(float(keys["start"]) / float(keys["iscale"]))
s_end = int(float(keys["end"]) / float(keys["iscale"]))

for i,key in enumerate(vals[0].keys()):
    if len(keys["yscale"]) == 0 or len(keys["ylabel"]) == 0:
           keys["yscale"].append(0)
           break
    if i == len(keys["yscale"]):
        keys["yscale"].append(keys["yscale"][0])
    elif i == len(keys["ylabel"]):
        keys["yscale"] = keys["yscale"][0]

outvals = []
sec = 0
for i,row in enumerate(vals):
    if i < s_start:
        continue
    if i == s_end:
        break
    if (i % stepsize == 0):
        outvals.append({keys["xlabel"]: sec} | {key: float(row[key]) / float(keys["yscale"][n]) if row[key] != '' else None for n,key in enumerate(row.keys())})
        sec += float(keys["oscale"])

print("Done!\n\nOutputting csv...")

name = keys["in"].split(".")[0]
outname = f"{name}-out"
if keys["out"] is str:
    outname = keys["out"]

if "csv" in keys["oo"]:
    keys["oo"].remove("csv")
    with open(f"{outname}.csv", "w", newline="") as csvfile:
        fieldnames = [key for key in outvals[0].keys()]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in outvals:
            writer.writerow(row)

print("Done!\n\n")
if len(keys["oo"]) == 0 and "show" not in sys.argv:
    sys.exit()

print("Plotting...")

spine_offset = 0.05;

fig, ax = plt.subplots()

twins = []
twinplots = []

for i,key in enumerate(outvals[0].keys()):
    if key != keys["xlabel"]:
        if i > 1 and i <= len(keys["ylabel"]):
            cur = len(twins)
            twins.append(ax.twinx())
            twinplots.append(twins[cur].plot([row[keys["xlabel"]] for row in outvals], [row[key] for row in outvals], label=key, color=f"C{(i-1) % 10}"))
        else:
            ax.plot([row[keys["xlabel"]] for row in outvals], [row[key] for row in outvals], label=key, color=f"C{(i-1) % 10}")


plt.title(name, fontsize=20)
fig.legend(loc='upper right')
if len(keys["ylabel"]) == 0:
    ax.set(xlabel=keys["xlabel"], ylabel="V")
else:
    ax.set(xlabel=keys["xlabel"], ylabel=keys["ylabel"][0])
if len(keys["ylabel"]) > 1:
    ax.yaxis.label.set_color("C0")
    ax.tick_params(axis='y', colors="C0")

for i in range(len(twins)):
    twins[i].set(xlabel=keys["xlabel"], ylabel=keys["ylabel"][i + 1])
    twins[i].yaxis.label.set_color(twinplots[i][0].get_color())
    twins[i].tick_params(axis='y', colors=twinplots[i][0].get_color())
    twins[i].spines.right.set_position(("axes", 1 + spine_offset * i))

for oo in keys["oo"]:
    if oo == "csv":
        continue
    plt.savefig(f"{outname}.{oo}")

if "debug" in sys.argv:
    pltstring = ""
    for key,val in keys.items():
        pltstring += f"{key}: {val}\n"
    pltstring += f"stepsize: {stepsize}\n"

    plt.text(0.91, 0.07, pltstring, fontsize=9, transform=plt.gcf().transFigure)

if "show" in sys.argv:
    plt.show()

print("Done!\n\n")
