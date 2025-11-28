import csv
import matplotlib.pyplot as plt
import sys

if len(sys.argv) == 1:
    print("filename scale end ifshow")
    sys.exit()

maxi = 0
vals = []
with open(sys.argv[1], newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for i,row in enumerate(reader):
        vals.append({"V": row["CH1V"]})
        maxi = i

outvals = []
scale = int(sys.argv[2]) if len(sys.argv) >= 3 else 1000
sec = 0
end = int(sys.argv[3]) if len(sys.argv) >= 4 else maxi
for i,row in enumerate(vals):
    if i == end:
        break
    if (i % scale == 0):
        outvals.append({"t": sec, "V": row["V"]})
        sec += 1 * (scale / 1000)

with open("out.csv", "w", newline="") as csvfile:
    fieldnames = ["t", "V"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in outvals:
        writer.writerow(row)

plt.plot([float(row["t"]) for row in outvals], [float(row["V"]) for row in outvals])
plt.savefig('plot.png')
plt.savefig('plot.pdf')

if len(sys.argv) >= 5 and sys.argv[4] == "show":
    plt.show()
