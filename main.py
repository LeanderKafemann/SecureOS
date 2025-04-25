import threading, time, pyautogui, shutil, smtplib, os
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from tkinter import PhotoImage, Tk, Canvas, Button
import pygame.camera
from image_similarity_measures.evaluate import evaluation

active = True
locked = False
end = False
pin = "0000"
fenster = None

with open("./login_credentials.txt", "r", encoding="utf-8") as f:
    NAME, PWD = f.read().split("#*#")
with open("./send_to.txt", "r", encoding="utf-8") as f:
    SEND_TO = f.read()

def countDif(list1: list, list2: list):
    dif = 0
    for i in range(len(list1)):
        if list1[i] != list2[i]:
            dif += 1
    return dif

def getallpixels(bild):
    pixellist = []
    for x in range(bild.width()):
        for y in range(bild.height()):
            aktpxl = bild.get(x, y)
            pixellist.append(aktpxl)
    print("Finished GAP")
    return pixellist

def takePhoto():
    pygame.camera.init()
    camlist = pygame.camera.list_cameras()
    cam = pygame.camera.Camera(camlist[len(camlist)-2],(800, 450))
    cam.start()
    time.sleep(1)
    img = cam.get_image()
    pygame.image.save(img, "./aktPhoto.png")

def abgleich():
    akt = PhotoImage(file="./aktPhoto.png")
    last = PhotoImage(file="./lastPhoto.png")
    dif = countDif(getallpixels(akt), getallpixels(last))
    eval_ = evaluation(org_img_path="./aktPhoto.png", pred_img_path="./lastPhoto.png", metrics=["ssim", "fsim", "rmse", "psnr", "issm", "sre", "sam"])
    log_ = "(similaritys: {})".format(str(dif)+"|"+str(eval_))
    print(log_)
    if dif > 360000 or eval_["ssim"] < 0.8 or eval_["sam"] == 0:#or eval_["psnr"] > 40
        sendPhoto("./lastPhoto.png", "lastPhoto")
        sendPhoto("./aktPhoto.png", "aktPhoto"+log_)
    os.remove("./lastPhoto.png")
    shutil.move("./aktPhoto.png", "./lastPhoto.png")

def sendPhoto(path: str, message: str = "Sicherheitsfoto"):
    with open(path, 'rb') as f:
        img_data = f.read()
    s = smtplib.SMTP("smtp.IONOS.de", 587)
    s.starttls()
    s.login(NAME, PWD)
    nachricht = MIMEMultipart()
    nachricht["From"] = "Security-Bot <update-bot@lk.kafemann.berlin>"
    nachricht["Subject"] = "Sicherheitsfoto"
    nachricht["To"] = "Owner <{}>".format(SEND_TO)
    text_content = message
    text = MIMEText(text_content)
    nachricht.attach(text)
    image = MIMEImage(img_data, name=os.path.basename(path))
    nachricht.attach(image)
    s.sendmail("Security-Bot <update-bot@lk.kafemann.berlin>", "Owner <{}>".format(SEND_TO), nachricht.as_string())
    s.quit()

def abgleichAgent():
    global active
    while True:
        if not end:
            if active:
                takePhoto()
                abgleich()
            time.sleep(30)
        else:
            pyautogui.alert("Beendigung eingeleitet!", "Beenden")
            quit()

fenster = Tk()
fenster.title("SecureOS")

threading.Thread(target=abgleichAgent).start()

def main():
    global locked, pin, active, end
    while True:
        if locked:
            buttons = ["Oberfläche entsperren"]
        else:
            buttons = ["Oberfläche sperren", "Foto senden", "Prüfen", "Initialisieren", "Beenden"]
            buttons += ["Deaktivieren"] if active else ["Aktivieren"]
        match pyautogui.confirm("Welche Aktion wollen Sie ausführen?", "Menü V0.5.0-BETA", buttons=buttons):
            case "Oberfläche sperren":
                pin = pyautogui.password("PIN erstellen:", "PIN")
                locked = True
            case "Oberfläche entsperren":
                if pin == pyautogui.password("PIN eingeben:", "PIN"):
                    locked = False
                else:
                    pyautogui.alert("Falsche PIN!", "PIN")
            case "Prüfen":
                takePhoto()
                abgleich()
            case "Initialisieren":
                takePhoto()
                shutil.move("./aktPhoto.png", "./lastPhoto.png")
            case "Foto senden":
                sendPhoto("./lastPhoto.png")
            case "Deaktivieren":
                active = False
            case "Aktivieren":
                active = True
            case "Beenden" | _:
                pyautogui.alert("Dies kann bis zu 45 Sekunden dauern.", "Beenden")
                end = True
                fenster.destroy()
                quit()
threading.Thread(target=main).start()

c = Canvas(fenster, width=400, height=200)
c.configure(bg="light blue")
c.pack()

c.create_text(200, 50, text="SecureOS Pro", font=("Verdana", "30", "bold"), anchor="center")
c.create_text(200, 150, text="More window functions coming soon...", font=("Verdana", "12"), anchor="center")
c.create_window(200, 120, anchor="center", window=Button(master=fenster, text="Beenden", relief="ridge", command=quit, background="light blue"))
c.create_text(200, 180, text="Version 0.5.0--BETA - Copyright Leander Kafemann 2025", font=("Verdana", "7"), anchor="center")

fenster.mainloop()