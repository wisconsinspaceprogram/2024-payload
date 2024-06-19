import time
import pandas as pd
import pygame, sys
import pygame_chart as pyc
from Plotter import Plotter
import matplotlib.pyplot as plt
import time
import scipy
import csv

def Buttonify(Picture, coords, size, surface):
    image = pygame.image.load(Picture)
    image = pygame.transform.scale(image, size)
    imagerect = image.get_rect()
    imagerect.topleft = coords
    surface.blit(image,imagerect)
    return (image,imagerect)

def rsquared(x, y):
    """ Return R^2 where x and y are array-like."""

    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x, y)
    return r_value**2

# Screen and window settings
background = (255, 255, 255)
pygame.init()
pygame.display.set_caption("2024 Payload Data Replay")
screen = pygame.display.set_mode((1920,1000))
screen.fill(background)

#Reading the data in
#file_path = 'Payload/Github Repo/2024-payload/Utility Scripts/Extractor/Logs/2024-06-14_22_52_52_593467_1.csv'
#file_path = 'Payload/Github Repo/2024-payload/Utility Scripts/Extractor/Logs/2024-06-17_00_35_51_353186_1.csv'
file_path = 'Payload/Github Repo/2024-payload/Utility Scripts/Extractor/Logs/2024-06-18_22_31_22_342847_1.csv'

###

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

#file_path = 'Payload/Github Repo/2024-payload/Utility Scripts/Extractor/Logs/2024-06-14_22_52_52_593467_1.csv'

df = pd.read_csv(file_path)

print(df['Time'])

preLaunch = [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
launch = [0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0]

_time = []
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
      if (row["Launched"] == 1 or True) and voltSum > 0:
        pdVal.append(pdSum / pdCount)
        current.append((voltSum / voltCount) / 3.4)
        _time.append(startTime)
        pdChange.append(((pdSum / pdCount - lastPd) / lastPd * 100) if voltSum > 0 else 0)

    lastPd = pdSum / pdCount

    pdSum = 0
    pdCount = 0

    voltSum = 0
    voltCount = 0

    startTime = row["Time"]


  #if((preLaunch[int(row["State"])] if (row["Launched"] == 0) else launch[int(row["State"])]) > 0):
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
plt.title("R-Squared: " + str(rsquared(field, pdChange)))
plt.savefig("TestDataImage.png")

filename = 'output.csv'

# Writing to the CSV file
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    for name, age in zip(field, pdChange):
        writer.writerow([name, age])


####




df = pd.read_csv(file_path)

timeList = list(df["Time"])
stateList = list(df["State"])
pdList = list(df["PD"])
accXList = list(df["AccX"])
accYList = list(df["AccY"])
accZList = list(df["AccZ"])
mainBatList = list(df["MainBat"])
coilBatList = list(df["CoilBat"])
coilList = list(df["Coil"])
launchedList = list(df["Launched"])
sd1List = list(df["SD1"])
sd2List = list(df["SD2"])
tempList = list(df["Temp"])


#Tracking for our "Replay"
lastLoopTime = 0
index = 0
startTime = 2000
refillBuffers = True
lookback = 200 #Seconds
clickedScrubber = False

#Buffers for plots :)
timeBuffer = []
pdBuffer = []
accXBuffer = []
accYBuffer = []
accZBuffer = []
fieldBuffer = []


#Plotters

accXPlotter = Plotter(screen, "Acceleration X [m/s]", "", 50, 50, 400, 200, 1, (255, 0, 255), 5)
accYPlotter = Plotter(screen, "Acceleration Y [m/s]", "", 50, 275, 400, 200, 1, (0, 150, 0), 5)
accZPlotter = Plotter(screen, "Acceleration Z [m/s]", "", 50, 500, 400, 200, 1, (0, 0, 200), 5)

pdPlotter = Plotter(screen, "Photo Diode", "", 550, 50, 600, 300, 6, (255, 0, 0), 5)
fieldPlotter = Plotter(screen, "Field Strength [Gauss]", "", 550, 400, 600, 300, 20, (0, 150, 255), 1)

#Other window setup
mediumBlackFont = pygame.font.SysFont("Ariel", 24)
largeBlackFont = pygame.font.SysFont("Ariel", 36)

#Buttonify("Payload/Github Repo/2024-payload/Images/BatteryOutline.png", (420, 350), (50, 100), screen)
#Buttonify("Payload/Github Repo/2024-payload/Images/BatteryOutline.png", (520, 350), (50, 100), screen)

Buttonify("TestDataImage.png", (1200, 122), (640, 480), screen)
Buttonify("BadgerBallisticslogo_B.png", (1400, 700), (400, 400), screen)

sliderPos = 800

#Finding all the times when we launched to highlight
launchTimes = []

curLaunch = [0, 0]
for i in range(len(launchedList)):
  if i > 0:
    if launchedList[i] == 1 and launchedList[i-1] == 0:
      curLaunch[0] = timeList[i]
    if (launchedList[i] == 0 and launchedList[i-1] == 1) or i == len(launchedList) - 1:
      curLaunch[1] = timeList[i-1]
      launchTimes.append(curLaunch)
      curLaunch = [0, 0]
print(launchTimes)
while True:

  events = pygame.event.get()
  mousex, mousey = pygame.mouse.get_pos()

  for event in events:
    # Window exit
    if event.type == pygame.QUIT:
      pygame.quit()
      sys.exit()

    if event.type == pygame.MOUSEBUTTONDOWN:
      if mousey > sliderPos - 20 and mousey < sliderPos + 20:
        startTime = ((mousex - 100) / 1720) * max(timeList)
        clickedScrubber = True

    if event.type == pygame.MOUSEBUTTONUP:
      if clickedScrubber:
        refillBuffers = True

        if (((mousex - 100) / 1720) * max(timeList)) >= startTime:
          lookback = max(((mousex - 100) / 1720) * max(timeList) - startTime, 1)
          startTime = ((mousex - 100) / 1720) * max(timeList)
        else:
          lookback = startTime - ((mousex - 100) / 1720) * max(timeList)

        timeBuffer = []
        pdBuffer = []
        accXBuffer = []
        accYBuffer = []
        accZBuffer = []
        fieldBuffer = []

        clickedScrubber = False

        index = 0

  #Stop once we hit end of data
  if index < len(timeList):

    #Waiting if we are running too quick
    #if index > 0:
    #  if ((time.time() - lastLoopTime)) < (timeList[index] - timeList[index - 1]):
    #    time.sleep((timeList[index] - timeList[index - 1] - (time.time() - lastLoopTime)))

    #Calculations
    field = coilList[index] / 3.85 * 132

    #Updating buffers with fresh data
    if not refillBuffers:
      timeBuffer.append(timeList[index])
      pdBuffer.append(pdList[index])
      accXBuffer.append(accXList[index])
      accYBuffer.append(accYList[index])
      accZBuffer.append(accZList[index])
      fieldBuffer.append(field)# if field < 345 else 0)


    #If we change the starttime, we need to refresh the buffers
    if refillBuffers:
      index = 0
      refillBuffers = False
      while index < len(timeList) and timeList[index] < startTime:
        if timeList[index] > (startTime - lookback):
          field = coilList[index] / 3.85 * 132

          timeBuffer.append(timeList[index])
          pdBuffer.append(pdList[index])
          accXBuffer.append(accXList[index])
          accYBuffer.append(accYList[index])
          accZBuffer.append(accZList[index])
          fieldBuffer.append(field)# if field < 345 else 0)

        index += 1

    #Deleting values if they are from too long ago!
    while (len(timeBuffer) > 0) and (timeBuffer[-1] - timeBuffer[0]) > lookback:
      timeBuffer.pop(0)
      pdBuffer.pop(0)
      accXBuffer.pop(0)
      accYBuffer.pop(0)
      accZBuffer.pop(0)
      fieldBuffer.pop(0)

    #Updating graphs and data
    pdPlotter.set_data(timeBuffer, pdBuffer)
    accXPlotter.set_data(timeBuffer, accXBuffer)
    accYPlotter.set_data(timeBuffer, accYBuffer)
    accZPlotter.set_data(timeBuffer, accZBuffer)
    fieldPlotter.set_data(timeBuffer, fieldBuffer)



    pdPlotter.update()
    accXPlotter.update()
    accYPlotter.update()
    accZPlotter.update()
    fieldPlotter.update()



    #Updating battery info ever once in a while
    if index % 4 == 0:
      pygame.draw.rect(screen, background, pygame.Rect(650, 800, 600, 100))

      text_surface = largeBlackFont.render("Main:" + str(mainBatList[index]) + "V", False, (0, 0, 0), background)
      screen.blit(text_surface, (650, 885))

      batteryColor = (0, 200, 0)
      if(mainBatList[index] < 12.5):
        batteryColor = (200, 200, 0)
      elif(mainBatList[index] < 12):
        batteryColor = (200, 0, 0)

      pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(845, 880, 130, 40))
      pygame.draw.rect(screen, batteryColor, pygame.Rect(850, 885, min((mainBatList[index] - 11) / 2 * 120, 120), 30))


      text_surface = largeBlackFont.render("Coil: " + str(coilBatList[index]) + "V", False, (0, 0, 0), background)
      screen.blit(text_surface, (650, 935))

      batteryColor = (0, 200, 0)
      if(coilBatList[index] < 12.5):
        batteryColor = (200, 200, 0)
      elif(coilBatList[index] < 12):
        batteryColor = (200, 0, 0)

      pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(845, 930, 130, 40))
      pygame.draw.rect(screen, batteryColor, pygame.Rect(850, 935, min((coilBatList[index] - 11) / 2 * 120, 120), 30))


    text_surface = largeBlackFont.render("Launch State: " + ("Flight" if launchedList[index] == 1 else "Idle"), False, (0, 0, 0), background)
    screen.blit(text_surface, (650, 835))

    text_surface = largeBlackFont.render("SD #1: " + ("Connected" if sd1List[index] == 1 else "Disconnected"), False, (0, 0, 0), background)
    screen.blit(text_surface, (250, 835))

    text_surface = largeBlackFont.render("SD #2: " + ("Connected" if sd2List[index] == 1 else "Disconnected"), False, (0, 0, 0), background)
    screen.blit(text_surface, (250, 885))

    text_surface = largeBlackFont.render("IMU: " + ("Connected" if (abs(accXList[index]) > 0.5 or abs(accYList[index]) > 0.5 or abs(accZList[index]) > 0.5) else "Disconnected"), False, (0, 0, 0), background)
    screen.blit(text_surface, (250, 935))

    text_surface = largeBlackFont.render("Temperature: " + str(tempList[index]) + "C", False, (0, 0, 0), background)
    screen.blit(text_surface, (1100, 835))

    #Drawing visible window on scrubber
    scrubberRect = pygame.Rect(100, sliderPos-5, 1720, 10)
    pygame.draw.rect(screen, (100, 100, 100), scrubberRect)
    
    #Drawing launch times
    if len(launchTimes) > 0:
      for j in range(len(launchTimes)):
        launchRect = pygame.Rect(launchTimes[j][0] / max(timeList) * 1720 + 100, sliderPos-5, max((launchTimes[j][1] - launchTimes[j][0]) / max(timeList) * 1720, 2), 10)
        pygame.draw.rect(screen, (0, 200, 0), launchRect)

    visibleRect = pygame.Rect(max(timeList[index] - lookback, 0) / max(timeList) * 1720 + 100, sliderPos-3, lookback / max(timeList) * 1720, 6)
    pygame.draw.rect(screen, (250, 100, 100), visibleRect)

    #Mainting the loop and time tracking feature
    lastLoopTime = time.time()
    index += 1

  pygame.display.update()
