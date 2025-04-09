import tkinter as tk
from tkinter import simpledialog
import threading
import socket
import queue

class App:
    def __init__(self, master):
        self.master = master
        master.withdraw()

        self.userName = simpledialog.askstring("Name Request", "Enter your name:")
        if self.userName:
            master.title("Client " + self.userName)
            master.deiconify()
        else:
            master.destroy()
            return

        self.message_list = []
        self.label_list = []
        self.selfMessage = False

        self.message_frame = tk.Frame(master)
        self.message_frame.pack(fill="both", expand=True)

        self.input_box = tk.Text(master, height=2)#, width=30)
        self.input_box.pack()

        self.submit_button = tk.Button(master, text="Send Message", command=self.on_submit)
        self.submit_button.pack()

        self.data_queue = queue.Queue()
        self.running = True

        self.socket_thread = threading.Thread(target=self.read_socket)
        self.socket_thread.daemon = True  # Allow program to exit even if thread is running
        self.socket_thread.start()

        self.update_gui()

    def on_submit(self):
        text = self.input_box.get("1.0", "end-1c")
        self.selfMessage = True
        self.data_queue.put(text)
        self.s.sendall((self.userName + ": " + text).encode())
        self.input_box.delete("1.0", tk.END)

    def read_socket(self):
        host = '127.0.0.1'  # Or "localhost"
        port = 5123

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.s:
                self.s.connect((host, port))
                while self.running:
                    data = self.s.recv(1024)
                    if not data:
                        break
                    self.data_queue.put(data.decode())
        except Exception as e:
             self.data_queue.put(f"Error: {e}")

    def update_gui(self):
        try:
            data = self.data_queue.get_nowait()
            self.message_list.append(data)
            message = tk.StringVar()
            message.set(data)
            if (self.selfMessage):
                label = tk.Label(self.message_frame, textvariable=message, anchor="w", justify="left", fg="green")
                self.selfMessage = False
            else:
                label = tk.Label(self.message_frame, textvariable=message, anchor="w", justify="left")
            label.pack(anchor="w")
            self.label_list.append(message)
        except queue.Empty:
            pass  # No data yet, ignore
        if self.running:
            self.master.after(100, self.update_gui) # Check every 100 ms

    def close(self):
        self.running = False
        self.master.destroy()

def main():
    root = tk.Tk()
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()

if __name__ == "__main__":
    main()
