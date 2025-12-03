import csv
import matplotlib.pyplot as plt
import sys
import re
import os

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
    for i,row in enumerate(reader):
        vals.append({colnames_o[i]: row[colnames[i]] for i in range(len(colnames_o))})
        maxi = i

stepsize = int(float(keys["oscale"]) / float(keys["iscale"]))
s_start = int(float(keys["start"]) / float(keys["iscale"]))
s_end = int(float(keys["end"]) / float(keys["iscale"]))

for i,key in enumerate(vals[0].keys()):
    if key != keys["xlabel"] and i > len(keys["yscale"]):
            yscale[i] = 1

outvals = []
sec = 0
for i,row in enumerate(vals):
    if i < s_start:
        continue
    if i == s_end:
        break
    if (i % stepsize == 0):
        outvals.append({keys["xlabel"]: sec} | {key: float(row[key]) / float(keys["yscale"][n]) for n,key in enumerate(row.keys())})
        sec += float(keys["oscale"])

name = keys["in"].split(".")[0]
outname = f"{name}-out"
if keys["out"] is str:
    outname = keys["out"]

if "csv" in keys["oo"]:
    with open(f"{outname}.csv", "w", newline="") as csvfile:
        fieldnames = [key for key in outvals[0].keys()]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in outvals:
            writer.writerow(row)

spine_offset = 0.2;
current_spine = 1;

fig, ax = plt.subplots()

twins = []

for i,key in enumerate(outvals[0].keys()):
    if key != keys["xlabel"]:
        if i > 1:
            twins.append(ax.twinx())
            twins[i-2].plot([row[keys["xlabel"]] for row in outvals], [row[key] for row in outvals], label=key)
        else:
            ax.plot([row[keys["xlabel"]] for row in outvals], [row[key] for row in outvals], label=key)

plt.title(name, fontsize=20)
plt.legend(loc='upper right')
if len(keys["ylabel"]) == 0:
    ax.set(xlabel=keys["xlabel"], ylabel="V")
else:
    ax.set(xlabel=keys["xlabel"], ylabel=keys["ylabel"][0])

for i in range(len(twins)):
    if i + 1 > len(keys["ylabel"]):
        continue
    else:
        twins[i].set(xlabel=keys["xlabel"], ylabel=keys["ylabel"][i + 1])

for oo in keys["oo"]:
    if oo == "csv":
        continue
    plt.savefig(f"{outname}.{oo}")

if "show" in sys.argv:
    pltstring = ""
    for key,val in keys.items():
        pltstring += f"{key}: {val}\n"
    pltstring += f"stepsize: {stepsize}\n"

    plt.text(0.91, 0.07, pltstring, fontsize=9, transform=plt.gcf().transFigure)

    plt.show()
