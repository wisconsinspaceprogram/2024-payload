import matplotlib.pyplot as plt
import numpy as np

# R is coil radius
# X is coil location from center (0 is where diamond will be)
# I is current
# z is location along field
# Output is in gauss

def FieldStrengthSingleCoil(R, x, I, z):
  pi = 3.14159
  mu_not = 4 * pi * 10 ** -7
  epsilon = (1 + ((x-z)/R)**2)**(-3/2)

  B = epsilon * mu_not * I / (2 * R)

  return B * 10000

#=============== Setting up different plot configuration =======
fig, (ax1, ax2, ax3) = plt.subplots(1, 3)

# ============ Plots simple helmzholt coil setup ==============#
# x = []
# y_1 = []
# y_2 = []
# y_3 = []

# for i in range(100):
#   x_loc = i / 1000 - 0.05
#   x.append(x_loc)
#   y_1.append(FieldStrengthSingleCoil(0.01, 0.005, 1, x_loc))
#   y_2.append(FieldStrengthSingleCoil(0.01, -0.005, 1, x_loc))
#   y_3.append(y_1[-1] + y_2[-1])

# plt.plot(x, y_1)
# plt.plot(x, y_2)
# plt.plot(x, y_3)
# plt.show()

# ================== Plots field along axis for out setup ========================#
show_all = False      #Plot every individual coil
wire_width = 0.000812   #Diameter of wire, [m]
min_dist = 0.006       #Inner distance between closest coils [m]
width_cnt = 17        #number of coils stacked side by side
height_cnt = 15       #number of coils stacked on top of one another
inner_radius = 0.008  #radius of inner coil
I = 3                 #Current [A]
res = .0000000168
A = 3.14159 * (wire_width / 2) ** 2


# show_all = True      #Plot every individual coil
# wire_width = 0.00044   #Diameter of wire, [m]
# min_dist = 0.014       #Inner distance between closest coils [m]
# width_cnt = 20        #number of coils stacked side by side
# height_cnt = 15       #number of coils stacked on top of one another
# inner_radius = 0.01  #radius of inner coil
# I = 1                #Current [A]
# res = .0000000168
# A = 3.14159 * (wire_width / 2) ** 2

#Coil size calcs
total_thickness = min_dist + 2 * width_cnt * wire_width
total_diameter = 2 * (inner_radius + wire_width * height_cnt)

#Vars to store all the shit
z = list(np.arange(-0.06, 0.06, 0.0005))
coils = []

#Looping through every coil
#Starting width wise
for i in range(width_cnt):
  x1 = (min_dist / 2) + i * wire_width
  x2 = -x1
  
  #Looping through height now
  for j in range(height_cnt):
    r = inner_radius + j * wire_width

    #Looping along the inner axis to find shtuff
    pos_coil = []
    neg_coil = []
    for k in range(len(z)):
      x = z[k]
      pos_coil.append(FieldStrengthSingleCoil(r, x1, I, x))
      neg_coil.append(FieldStrengthSingleCoil(r, x2, I, x))
    
    #Adding these coils to cnt
    coils.append(pos_coil)
    coils.append(neg_coil)


#Plotting all these fields
total_field = [0] * len(z)
for i in range(len(coils)):
  if show_all:
    ax1.plot(z, coils[i])
  
  #Summin shit up
  for j in range(len(coils[i])):
    total_field[j] += coils[i][j]
  
fig.suptitle('Helmholtz coil: Wire Width: {}m, Center Dist: {}m, Width #:{}, Height #{}, Inner Radius{}m, Current:{}A'.format(wire_width, min_dist, width_cnt, height_cnt, inner_radius, I))

ax1.set_title("Individual field contributions")
ax1.set(xlabel = "Distance along center axis [m]", ylabel="Field Strength [G]")

ax2.plot(z, total_field)
ax2.axvline(x=total_thickness/2)
ax2.axvline(x=-total_thickness/2)
ax2.set_title("Center: " + str(round(total_field[int(len(total_field)/2)], 2)) + "[G]")
ax2.set(xlabel = "Distance along center axis [m]", ylabel = "Field Strength [G]")
# plt.show()

#====================Finds the field in middle given whatever values passed ===============================
# wire: wire width
# min_d: dist between center coils 
# w_cnt: cnt of coils stacked side by side
# h_cnt: cnt of coils stacked on top
# ir: innermost radius
# cur: current
def FieldStrength(wire, min_d, w_cnt, h_cnt, ir, cur):
  field = 0
  total_wire_length = 0
  #Looping through every coil
  #Starting width wise
  for i in range(w_cnt):
    x1 = (min_d / 2) + i * wire
    x2 = -x1
    
    #Looping through height now
    for j in range(h_cnt):
      r = ir + j * wire

      #Looping along the inner axis to find shtuff
      field += FieldStrengthSingleCoil(r, x1, cur, 0)
      field += FieldStrengthSingleCoil(r, x2, cur, 0)

      total_wire_length += 4 * 3.14159 * r


  print("Length:", total_wire_length, "Resistance: ", total_wire_length * res / A)
  return field

print(FieldStrength(0.0005, 0.014, 20, 15, 0.01, 4))

#=============== showing current vs field strength ================
curs = list(np.arange(0, 5, 0.01))
fields = []

for i in range(len(curs)):
  fields.append(FieldStrength(wire_width, min_dist, width_cnt, height_cnt, inner_radius, curs[i]))
  
print("Thickness: ", total_thickness, "Diameter: ", total_diameter)

ax3.plot(curs, fields)
ax3.set(xlabel="Current [A]", ylabel="Center Field Strength [G]")
ax3.scatter([I], [total_field[int(len(total_field)/2)]])
plt.show()
