import customtkinter as ctk
from tkinter import filedialog
from recorder import record_audio
from eval import predict_audio


MODEL_PATH = "D:\PythonProjects\DeepFake_Audio_GUI\LibriSeVoc-1k\librifake_pretrained_lambda0.5_epoch_25.pth"   # change to your model path

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class DeepfakeGUI(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("Deepfake Audio Detector")
        self.geometry("600x500")

        title = ctk.CTkLabel(
            self,
            text="Deepfake Voice Detection",
            font=("Arial", 28)
        )
        title.pack(pady=30)

        self.record_btn = ctk.CTkButton(
            self,
            text="Record 10 Seconds Audio",
            command=self.record_audio
        )
        self.record_btn.pack(pady=10)

        self.upload_btn = ctk.CTkButton(
            self,
            text="Upload Audio File",
            command=self.upload_audio
        )
        self.upload_btn.pack(pady=10)

        self.result = ctk.CTkLabel(
            self,
            text="Result: Waiting...",
            font=("Arial", 22)
        )
        self.result.pack(pady=30)

        self.progress = ctk.CTkProgressBar(self, width=350)
        self.progress.pack(pady=10)

        self.progress.set(0)


    def record_audio(self):

        audio_file = record_audio(10)

        self.analyze(audio_file)


    def upload_audio(self):

        file = filedialog.askopenfilename(
            filetypes=[("Audio Files","*.wav")]
        )

        if file:
            self.analyze(file)


    def analyze(self, path):

        fake, real = predict_audio(path, MODEL_PATH)

        self.progress.set(fake)

        if fake > real:

            self.result.configure(
                text=f"FAKE VOICE DETECTED\nConfidence: {fake:.2f}",
                text_color="red"
            )

        else:

            self.result.configure(
                text=f"REAL VOICE\nConfidence: {real:.2f}",
                text_color="green"
            )


app = DeepfakeGUI()
app.mainloop()