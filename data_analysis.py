import pandas as pd
import matplotlib.pyplot as plt

def best_fit(X, Y):

    xbar = sum(X)/len(X)
    ybar = sum(Y)/len(Y)
    n = len(X) # or len(Y)

    numer = sum([xi*yi for xi,yi in zip(X, Y)]) - n * xbar * ybar
    denum = sum([xi**2 for xi in X]) - n * xbar**2

    b = numer / denum
    a = ybar - b * xbar

    print('best fit line:\ny = {:.5f} + {:.5f}x'.format(a, b))

    return a, b

file_path = 'Payload/Github Repo/2024-payload/Utility Scripts/Extractor/Logs/2024-06-14_22_52_52_593467_1.csv'

df = pd.read_csv(file_path)

print(df['Time'])

preLaunch = [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
launch = [0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0]

time = []
pdVal = []
pdChange = []
current = []

pdCount = 0
pdSum = 0

voltCount = 0
voltSum = 0

lastState = 0

startTime = 0

lastPd = 0

for index, row in df.iterrows():
  if row["State"] != lastState:
    if(pdSum > 0):
      if row["Launched"] == 1 or True:
        pdVal.append(pdSum / pdCount)
        current.append((voltSum / voltCount) / 3.4)
        time.append(startTime)
        pdChange.append(((pdSum / pdCount - lastPd) / lastPd * 100) if voltSum > 0 else 0)

    lastPd = pdSum / pdCount

    pdSum = 0
    pdCount = 0

    voltSum = 0
    voltCount = 0

    startTime = row["Time"]


  if((preLaunch[int(row["State"])] if (row["Launched"] == 0) else launch[int(row["State"])]) > 0):
    voltSum += row["Coil"]

  pdSum += row["PD"]
  voltCount += 1
  pdCount += 1

  lastState = row["State"]

field = []

for cur in current:
  field.append(cur * 132.55)

a, b = best_fit(field, pdChange)

#plt.plot(pdChange)
plt.scatter(field, pdChange)
yfit = [a + b * xi for xi in field]
plt.plot(field, yfit, color='red')
plt.xlabel("Field [Gauss]")
plt.ylabel("Optical Change [%]")
plt.suptitle("Ground Test Run Results")
plt.title("Limited Test Levels")
plt.show()