from datetime import datetime
from tkinter.constants import *
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode
from playsound import playsound
import sqlite3
import tkinter as tk
import argparse
import cv2
import os

class Application:
    def __init__(self, output_path = "./"):
        """ Initialize application which uses OpenCV + Tkinter. It displays
            a video stream in a Tkinter window and stores current snapshot on disk """
        self.vs = cv2.VideoCapture(0) 
        self.output_path = output_path
        self.current_image = None

        self.root = tk.Tk()
        self.root.title("QR Guests")
        self.root.wm_iconbitmap("resources\qr_icon.ico")
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)

        self.panel = tk.Label(self.root)
        self.panel.pack(expand=1, padx=10, pady=30)

        self.label = tk.Label(self.root, text="Welcome!")
        self.label.config(font=("helvetica", 36, "bold"))
        self.label.pack(pady=80)

        btn = tk.Button(self.root, text="Snapshot!", command=self.take_snapshot)
        btn.pack(side=BOTTOM, fill=X)

        self.database = Database()
        self.attended = []
        self.hashes = Database().hashes()
        self.detected = False

        self.video_loop()

    def video_loop(self):
        """ Get frame from the video stream and show it in Tkinter """
        ok, frame = self.vs.read() 
        if ok:  
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA) 
            self.current_image = Image.fromarray(cv2image) 
            imgtk = ImageTk.PhotoImage(image=self.current_image)
            self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
            self.panel.config(image=imgtk)

            for barcode in decode(frame):
                decoded = barcode.data.decode('utf-8')
                if decoded in self.database.hashes():
                    if not decoded in self.attended:
                        self.attended.append(decoded)
                        self.database.update_presence(decoded)
                        self.database.update_time(decoded)
                        name = self.database.hash_name(decoded)
                        self.label.config(text=f"Selamat datang, {name}")
        self.root.after(30, self.video_loop)

    def take_snapshot(self):
        """ Take snapshot and save it to the file """
        playsound("C:/Users/Omen/Downloads/Music/shutter.mp3", block=False)
        ts = datetime.now()
        filename = f"{ts.strftime('%Y-%m-%d_%H-%M-%S')}.png"
        path = os.path.join(self.output_path, filename)
        self.current_image.save(path, "PNG")
        print("[INFO] saved {}".format(filename))

    def destructor(self):
        """ Destroy the root object and release all resources """
        print("[INFO] closing...")
        self.root.destroy()
        self.vs.release()  # release web camera
        cv2.destroyAllWindows()

class Database:
    def __init__(self):
        self.connection = sqlite3.connect("database.db")
        self.cursor = self.connection.cursor()
        self.table = "guest_list"

    def update_presence(self, hash):
        self.cursor.execute(f"UPDATE {self.table} SET presence=1 WHERE hash='{hash}';")
        self.connection.commit()

    def update_time(self, hash):
        self.cursor.execute(f"UPDATE {self.table} SET time='{datetime.now().strftime('%I:%M:%S %p')}' WHERE hash='{hash}';")
        self.connection.commit()

    def hashes(self):
        hashes = []
        self.cursor.execute(f"SELECT hash FROM {self.table};")
        for hash in self.cursor.fetchall():
            hashes.append(hash[0])
        return hashes

    def hash_name(self, hash):
        self.cursor.execute(f"SELECT fullname FROM {self.table} WHERE hash='{hash}';")
        return self.cursor.fetchone()[0]


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", default="./gui/SnapShots",
    help="path to output directory to store snapshots (default: current folder")
args = vars(ap.parse_args())

# start the app
print("[INFO] starting...")
pba = Application(args["output"])
pba.root.mainloop()