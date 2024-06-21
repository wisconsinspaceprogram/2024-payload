#import pygame, sys
import pygame_chart as pyc

class Plotter:
  
  def __init__(self, screen, name, xlab, ylab, x, y, width, height, margin, color, linewidth, acc_plot):
    self.name = name
    self.datax = []
    self.datay = []
    self.x = x
    self.y = y
    self.width = width
    self.height = height
    self.ylab = ylab
    self.xlab = xlab
    self.margin = margin
    self.color = color
    self.linewidth = linewidth
    self.acc_plot = acc_plot

    self.fig = pyc.Figure(screen, x, y, width, height, bg_color=(255, 255, 255))
    self.fig.add_gridlines()
    self.fig.add_title(self.name)
    self.fig.add_yaxis_label(self.ylab)
    self.fig.add_xaxis_label(self.xlab)

  def new_data(self, x, y):
    self.datax.append(float(x))
    self.datay.append(float(y))

    if len(self.datax) > 100:
      self.datax.pop(0)
      self.datay.pop(0)

  def update(self):
    if len(self.datax) > 4 and len(self.datay) > 4:
      self.fig.line(self.name, self.datax, self.datay, self.color, self.linewidth)

      if self.acc_plot:
        self.fig.set_ylim((-45, 45))
      else:
        self.fig.set_ylim((min(self.datay)-self.margin, max(self.datay)+self.margin))
      self.fig.draw() 
    
    else:
      self.fig.line(self.name, [0, 1], [0, 1])
      self.fig.draw() 

  def set_data(self, datax, datay):
    self.datax = datax
    self.datay = datay

  def clear(self):
    self.datax = []
    self.datay = []

