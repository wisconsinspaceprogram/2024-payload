import serial
import time
import csv
import datetime
import os

def send_data(ser, data):
    """Send data to the Arduino."""
    if ser.is_open:
        ser.write(data.encode())
        print(f"Sent: {data}")
    else:
        print("Serial port not open")

ser = serial.Serial('COM5', 256000, timeout=1) 

time.sleep(1)

filename_blank = os.path.dirname(__file__)+'/Logs/' + str(datetime.datetime.now()).replace(" ", "_").replace(".", "_").replace(":", "_")

filename_1 = filename_blank + '_1.csv'
filename_2 = filename_blank + '_2.csv'

try:

    send_data(ser, "1")

    time.sleep(1)

    while True:
      if ser.in_waiting > 0:

            line = ser.readline().decode('utf-8', errors='ignore').rstrip()
            #print(line)

            if(line == "Done"):
                break

            data = line.split(",")
            print(data)

            with open(filename_1, 'a', newline='', errors='ignore') as csvfile:
              csv_writer = csv.writer(csvfile)
              csv_writer.writerow(data)

    time.sleep(1)

    print("read 1")


    send_data(ser, "2")

    while True:
      if ser.in_waiting > 0:

            line = ser.readline().decode('utf-8', errors='ignore').rstrip()
            #print(line)

            if(line == "Done"):
                break

            data = line.split(",")
            print(data)

            with open(filename_2, 'a', newline='', errors='ignore') as csvfile:
              csv_writer = csv.writer(csvfile)
              csv_writer.writerow(data)

    print("read 2")

        
except KeyboardInterrupt:
    print("Program terminated.")

finally:
    ser.close()  # Always close the serial connection when done
