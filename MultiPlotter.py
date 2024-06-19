import pygame, sys
import pygame_chart as pyc

class MultiPlotter:
  
  def __init__(self, screen, name, ylab, x, y, width, height, margin):
    self.name = name
    self.datax = []
    self.datay = []
    self.x = x
    self.y = y
    self.width = width
    self.height = height
    self.ylab = ylab
    self.margin = margin

    self.fig = pyc.Figure(screen, x, y, width, height, bg_color=(250, 250, 250))
    self.fig.add_gridlines()
    self.fig.add_title(self.name)
    self.fig.add_yaxis_label(self.ylab)

  # def new_data(self, x, y):
  #   self.datax.append(float(x))
  #   self.datay.append(float(y))

  #   if len(self.datax) > 100:
  #     self.datax.pop(0)
  #     self.datay.pop(0)

  def update(self):
    maxVal = 0
    minVal = 0
    for data in range(len(self.datax)):
      if len(self.datax[data]) > 2 and len(self.datay[data]) > 2:
        self.fig.line(self.name, self.datax[data], self.datay[data], color=(100, 100, 80 * (data+1)))

        if data == 0 or (max(self.datay[data]) > maxVal):
          maxVal = max(self.datay[data])
        if data == 0 or (min(self.datay[data]) < minVal):
          minVal = min(self.datay[data])
    
      else:
        self.fig.line(self.name, [0, 1], [0, 1])

    
    if(len(self.datax) > 0):
      if(len(self.datax[0]) > 0):
        self.fig.set_ylim((minVal-self.margin, maxVal+self.margin))
        self.fig.draw() 

  def set_data(self, datax, datay):
    self.datax = datax
    self.datay = datay

  def clear(self):
    self.datax = []
    self.datay = []

