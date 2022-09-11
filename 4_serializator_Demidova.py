# Transforming input data to binary package according to Modbus TCP protocol (reading of several analog inputs)

import tkinter as tk 

transaction_num = 0
protocol_id = "00000000"
unit_id = "0001"
moist = None
water_level = None
text_1 = "AI0: moisture = {} %\n"
text_2 = "AI1: water level = {} liters\n\n"
text_3 = "Serialized Modbus TCP message for reading analog inputs AI0 and AI1:\n "

# Writing Modbus TCP package:
def serializer(moist, water_level):    
    global transaction_num
    transaction_id = "{:08b}".format(transaction_num)
    total_length = "{:08b}".format(7)
    functional_code = "{:04b}".format(3)
    msg_length = "{:04b}".format(4)
    AI0 = "{:08b}".format(moist)
    AI1 = "{:08b}".format(water_level)
    serialized_msg = transaction_id + protocol_id + total_length + unit_id + functional_code + msg_length + AI0 + AI1
    transaction_num+=1
    return serialized_msg

# Get data and serialize
def clicked():
    result_binary.delete(0, tk.END)  
    global moist, water_level
    input_1=AI0.get()
    input_2=AI1.get()
    AI0.delete(0, tk.END)
    AI1.delete(0, tk.END)
# Moisture:
    try:
        moist = int(input_1)
        if (moist < 0) or (moist > 100):
            moist = 255
    except:
            moist = 255
# Water level:
    try:
        water_level = int(input_2)
        if (water_level < 0) or (water_level > 100):
            water_level = 255
    except:
        water_level = 255
# Serialize        
    result = serializer(moist, water_level)  
    text_1 = "AI0: moisture = " + str(moist) + " %\n"
    text_2 = "AI1: water level = " + str(water_level) + " liters\n\n"
    text_3 = "Serialized Modbus TCP message for reading analog inputs AI0 and AI1:\n "
    result_lbl.configure(text=text_1 + text_2 + text_3)
    result_binary.insert(0, result)
    
    
# interface 
window = tk.Tk()
window.title("Modbus TCP: read several analog inputs")
window.geometry('450x320')

hello_world = "This app is based on watering machine emulator: it helps to serialize data \n(moisture and water level) according to Modbus TCP protocol.\n"
lbl = tk.Label(window, text=hello_world, font=("Times New Roman", 11), pady=10, width=300, justify=tk.LEFT,  anchor="w")
lbl.pack()

input_frame = tk.Frame()
input_frame.pack(anchor = "w")
frame_A0 = tk.Frame(input_frame)
frame_A0.grid(column = 0, row = 0, sticky="w")
lbl_moist = tk.Label(frame_A0, text="Moisture (from 0 to 100), AI0: ", font=("Times New Roman", 11), justify=tk.LEFT,  anchor="w")
lbl_moist.pack(side=tk.RIGHT)
AI0 = tk.Entry(input_frame, width=20)
AI0.grid(column=1, row=0)

frame_A1 = tk.Frame(input_frame)
frame_A1.grid(column = 0, row = 1)
lbl_water_lvl = tk.Label(frame_A1, text="Water level (from 0 to 100), AI1: ", font=("Times New Roman", 11), justify=tk.LEFT,  anchor="w")
lbl_water_lvl.pack(side=tk.LEFT)
AI1 = tk.Entry(input_frame, width=20)
AI1.grid(column=1, row=1)

attention = tk.Label (window, text="In case of invalid input data the value of 255 will be used", font=("Times New Roman", 11), justify=tk.LEFT,  anchor="w")
attention.pack(anchor="w", pady=5)

btn_frame = tk.Frame()
btn_frame.pack()
btn = tk.Button(btn_frame, text="Serialize", command=clicked)
btn.grid(column=0, row =0)

result_lbl = tk.Label(window, text=text_1.format(moist) + text_2.format(water_level) + text_3, font=("Times New Roman", 11), justify=tk.LEFT,  anchor="w")
result_lbl.pack(anchor="w")

result_binary = tk.Entry(window, width=60)
result_binary.pack()

window.mainloop()
 
