import time
import pandas as pd
import pygame, sys
import pygame_chart as pyc
from Plotter import Plotter
import matplotlib.pyplot as plt
import time
import scipy
import csv
from datetime import datetime, timedelta

def time_from_seconds(seconds):
    # Starting time 6:29:29 AM
    start_time = datetime.strptime("06:29:29 AM", "%I:%M:%S %p")
    
    # Calculate the new time by adding the seconds
    new_time = start_time + timedelta(seconds=seconds)
    
    # Format the new time as a string with AM/PM
    return new_time.strftime("%I:%M:%S %p")

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
pygame.display.set_caption("2024 UW-Madison Payload Data Replay")
screen = pygame.display.set_mode((1920,1000))
screen.fill(background)

#Reading the data in
#file_path = 'Payload/Github Repo/2024-payload/Utility Scripts/Extractor/Logs/2024-06-14_22_52_52_593467_1.csv'
#file_path = 'Payload/Github Repo/2024-payload/Utility Scripts/Extractor/Logs/2024-06-17_00_35_51_353186_1.csv'

file_path = 'Payload/Github Repo/2024-payload/Utility Scripts/Extractor/Logs/2024-06-19_15_20_09_926906_1.csv'
#file_path = 'Payload/Github Repo/2024-payload/Utility Scripts/Extractor/Logs/CompFlightLaunchOnly.csv'

###

def best_fit(X, Y):
  if len(X) > 0 and len(Y) > 0:
    xbar = sum(X)/len(X)
    ybar = sum(Y)/len(Y)
    n = len(X) # or len(Y)

    numer = sum([xi*yi for xi,yi in zip(X, Y)]) - n * xbar * ybar
    denum = sum([xi**2 for xi in X]) - n * xbar**2

    b = numer / denum
    a = ybar - b * xbar

    print('best fit line:\ny = {:.5f} + {:.5f}x'.format(a, b))

    return a, b
  return 0, 0

#file_path = 'Payload/Github Repo/2024-payload/Utility Scripts/Extractor/Logs/2024-06-14_22_52_52_593467_1.csv'

df = pd.read_csv(file_path)

print(df['Time'])

preLaunch = [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
launch = [0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0]

#Tracking for our "Replay"
lastLoopTime = 0
index = 0
startTime = 31633.53#22078.27
refillBuffers = True
lookback = 31633.87 #Seconds
clickedScrubber = False

def update_scatter():
  _time = []
  pdVal = []
  pdChange = []
  current = []
  _temp = []
  cols = []

  pdCount = 0
  pdSum = 0

  voltCount = 0
  voltSum = 0

  lastState = 0

  t = 0

  lastPd = 0

  for index, row in df.iterrows():
    if row["State"] != lastState:
      if(pdSum > 0):
        if t >= (startTime - lookback) and t <= startTime:
          if (row["Launched"] == 1 or True) and voltSum > 0:
            pdVal.append(pdSum / pdCount)
            current.append((voltSum / voltCount) / 3.4)
            _time.append(startTime)
            pdChange.append(((pdSum / pdCount - lastPd) / lastPd * 100) if voltSum > 0 else 0)
            cols.append(((row["Temp"] - 20) / 40, 0,(1 - (row["Temp"] - 20) / 40)))
      lastPd = pdSum / max(pdCount, 1)

      pdSum = 0
      pdCount = 0

      voltSum = 0
      voltCount = 0

      t = row["Time"]


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
  plt.clf()
  plt.scatter(field, pdChange, color="blue")#, color=cols)
  yfit = [a + b * xi for xi in field]
  plt.plot(field, yfit, color='red', label=str(round(a, 5)) + " + " + str(round(b, 5)) + "x")
  plt.xlabel("Field [Gauss]")
  plt.ylabel("Optical Change [%]")
  plt.suptitle("Optical Response to Varying Magnetic Field")
  plt.title("R-Squared: " + str(round(rsquared(field, pdChange), 3)))
  plt.legend(loc="upper right")
  plt.savefig("TestDataImage.png")

  Buttonify("TestDataImage.png", (1200, 200), (640, 480), screen)

  return a, b

# filename = 'output.csv'

# # Writing to the CSV file
# with open(filename, mode='w', newline='') as file:
#     writer = csv.writer(file)
#     for name, age in zip(field, pdChange):
#         writer.writerow([name, age])


####
a, b = update_scatter()


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


#Buffers for plots :)
timeBuffer = []
pdBuffer = []
accXBuffer = []
accYBuffer = []
accZBuffer = []
fieldBuffer = []
tempBuffer = []

#Plotters

accXPlotter = Plotter(screen, "Acceleration X [m/s^2]", "Time After Activation [s]", "", 50, 25, 400, 250, 1, (255, 0, 255), 5, True)
accYPlotter = Plotter(screen, "Acceleration Y [m/s^2]", "Time After Activation [s]", "", 50, 275, 400, 250, 1, (0, 150, 0), 5, True)
accZPlotter = Plotter(screen, "Acceleration Z [m/s^2]", "Time After Activation [s]", "", 50, 525, 400, 250, 1, (0, 0, 200), 5, True)

pdPlotter = Plotter(screen, "Photo Diode Output", "Time After Activation [s]", "", 550, 25, 600, 250, 6, (255, 0, 0), 5, False)
fieldPlotter = Plotter(screen, "Field Strength [Gauss]", "Time After Activation [s]", "", 550, 275, 600, 250, 20, (0, 150, 255), 1, False)
tempPlotter = Plotter(screen, "Internal Temperature [C]", "Time After Activation [s]", "",550, 525, 600, 250, 20, (255,159,0), 1, False)

#Other window setup
mediumBlackFont = pygame.font.SysFont("Ariel", 24)
largeBlackFont = pygame.font.SysFont("Ariel", 36)

#Buttonify("Payload/Github Repo/2024-payload/Images/BatteryOutline.png", (420, 350), (50, 100), screen)
#Buttonify("Payload/Github Repo/2024-payload/Images/BatteryOutline.png", (520, 350), (50, 100), screen)

sliderPos = 800

#Finding all the times when we launched to highlight
launchTimes = []

curLaunch = [0, 0]
for i in range(len(launchedList)):
  if i > 0:
    if launchedList[i] == 1 and launchedList[i-1] == 0:
      curLaunch[0] = timeList[i]
    if (launchedList[i] == 0 and launchedList[i-1] == 1) or (i == len(launchedList) - 1 and curLaunch[1] != 0):
      curLaunch[1] = timeList[i-1]
      launchTimes.append(curLaunch)
      curLaunch = [0, 0]
print(launchTimes)


pause = False


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
        startTime = ((mousex - 100) / 1720) * (max(timeList) - min(timeList)) + min(timeList)
        clickedScrubber = True

    if event.type == pygame.MOUSEBUTTONUP:
      if clickedScrubber:
        refillBuffers = True

        if (((mousex - 100) / 1720) * (max(timeList) - min(timeList)) + min(timeList)) >= startTime:
          lookback = max(((mousex - 100) / 1720) * (max(timeList) - min(timeList)) + min(timeList) - startTime, 1)
          startTime = ((mousex - 100) / 1720) * (max(timeList) - min(timeList)) + min(timeList)
        else:
          lookback = startTime - ((mousex - 100) / 1720) * (max(timeList) - min(timeList))+ min(timeList)

        timeBuffer = []
        pdBuffer = []
        accXBuffer = []
        accYBuffer = []
        accZBuffer = []
        fieldBuffer = []
        tempBuffer = []

        clickedScrubber = False

        index = 0

        pause = False

      a, b = update_scatter()

  #Stop once we hit end of data
  if index < len(timeList) and not pause:

    #Waiting if we are running too quick
    if index > 0:
      if ((time.time() - lastLoopTime)) < (timeList[index] - timeList[index - 1]):
        time.sleep((timeList[index] - timeList[index - 1] - (time.time() - lastLoopTime)))
      pause = True

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
      tempBuffer.append(tempList[index])


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
          tempBuffer.append(tempList[index])

        index += 1

    #Deleting values if they are from too long ago!
    while (len(timeBuffer) > 0) and (timeBuffer[-1] - timeBuffer[0]) > lookback:
      timeBuffer.pop(0)
      pdBuffer.pop(0)
      accXBuffer.pop(0)
      accYBuffer.pop(0)
      accZBuffer.pop(0)
      fieldBuffer.pop(0)
      tempBuffer.pop(0)

    #Updating graphs and data
    pdPlotter.set_data(timeBuffer, pdBuffer)
    accXPlotter.set_data(timeBuffer, accXBuffer)
    accYPlotter.set_data(timeBuffer, accYBuffer)
    accZPlotter.set_data(timeBuffer, accZBuffer)
    fieldPlotter.set_data(timeBuffer, fieldBuffer)
    tempPlotter.set_data(timeBuffer, tempBuffer)



    pdPlotter.update()
    accXPlotter.update()
    accYPlotter.update()
    accZPlotter.update()
    fieldPlotter.update()
    tempPlotter.update()

    offset = 375

    #Updating battery info ever once in a while
    if index % 1 == 0:
      pygame.draw.rect(screen, background, pygame.Rect(650, 800, 1200, 300))

      text_surface = largeBlackFont.render("Main:" + str(mainBatList[index]) + "V", False, (0, 0, 0), background)
      screen.blit(text_surface, (650 + offset, 885))

      batteryColor = (0, 200, 0)
      if(mainBatList[index] < 12.5):
        batteryColor = (200, 200, 0)
      elif(mainBatList[index] < 12):
        batteryColor = (200, 0, 0)

      pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(845 + offset, 880, 130, 40))
      pygame.draw.rect(screen, batteryColor, pygame.Rect(850 + offset, 885, min((mainBatList[index] - 11) / 2 * 120, 120), 30))


      text_surface = largeBlackFont.render("Coil: " + str(coilBatList[index]) + "V", False, (0, 0, 0), background)
      screen.blit(text_surface, (650 + offset, 935))

      batteryColor = (0, 200, 0)
      if(coilBatList[index] < 12.5):
        batteryColor = (200, 200, 0)
      elif(coilBatList[index] < 12):
        batteryColor = (200, 0, 0)

      pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(845 + offset, 930, 130, 40))
      pygame.draw.rect(screen, batteryColor, pygame.Rect(850 + offset, 935, min((coilBatList[index] - 11) / 2 * 120, 120), 30))


    text_surface = largeBlackFont.render("Launch State: " + ("Flight" if (launchedList[index] == 1 or launchedList[max(index-1, 1)] == 1) else "Idle"), False, (0, 0, 0), background)
    screen.blit(text_surface, (650 + offset, 835))

    text_surface = largeBlackFont.render("SD #1: " + ("Connected" if sd1List[index] == 1 else "Disconnected"), False, (0, 0, 0), background)
    screen.blit(text_surface, (250 + offset, 835))

    text_surface = largeBlackFont.render("SD #2: " + ("Connected" if sd2List[index] == 1 else "Disconnected"), False, (0, 0, 0), background)
    screen.blit(text_surface, (250 + offset, 885))

    text_surface = largeBlackFont.render("IMU: " + ("Connected" if (abs(accXList[index]) > 0.5 or abs(accYList[index]) > 0.5 or abs(accZList[index]) > 0.5) else "Disconnected"), False, (0, 0, 0), background)
    screen.blit(text_surface, (250 + offset, 935))

    pygame.draw.rect(screen, background, pygame.Rect(1200, 50, 1000, 100))
    text_surface = largeBlackFont.render("Time range: " + time_from_seconds(startTime-lookback) + " - " + time_from_seconds(startTime), False, (0, 0, 0), background)
    screen.blit(text_surface, (1300, 100))

    #Drawing visible window on scrubber
    scrubberRect = pygame.Rect(100, sliderPos-5, 1720, 10)
    pygame.draw.rect(screen, (100, 100, 100), scrubberRect)
    
    print(launchTimes)
    #Drawing launch times
    if len(launchTimes) > 0:
      for j in range(len(launchTimes)):
        launchRect = pygame.Rect(launchTimes[j][0] / (max(timeList) - min(timeList)) * 1720 + 100, sliderPos-5, max((launchTimes[j][1] - launchTimes[j][0]) / (max(timeList) - min(timeList)) * 1720, 2), 10)
        pygame.draw.rect(screen, (0, 200, 0), launchRect)

    visibleRect = pygame.Rect(max(timeList[index] - lookback, 0) / (max(timeList) - min(timeList)) * 1720 + 100, sliderPos-3, lookback / (max(timeList) - min(timeList)) * 1720, 6)
    pygame.draw.rect(screen, (250, 100, 100), visibleRect)

    Buttonify("BadgerBallisticslogo_B.png", (1400, 700), (400, 400), screen)

    #Mainting the loop and time tracking feature
    lastLoopTime = time.time()
    index += 1

  pygame.display.update()
