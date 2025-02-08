import json
import pyttsx3
import datetime
import speech_recognition as sr
from difflib import get_close_matches
import smtplib
from email.mime.text import MIMEText
import time
from datetime import datetime

DEFAULT_RESPONSES_PATH = "default_responses.json"
EMERGENCY_CODE = "help me"
SENDER_EMAIL = "crazyhairdontcarelol@gmail.com"
SENDER_PASSWORD = "ihpl hvdg ujrs rbmw"
RELATIVE_EMAIL = "suhani.fgc@gmail.com"
RELATIVE_PHONE_SMS = "9458162244@vtext.com"

# Load and save default responses
def load_default_responses(filepath):
    try:
        with open(filepath, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Default responses file not found at {filepath}. Starting with an empty response set.")
        return {}

def save_default_responses(responses, filepath):
    with open(filepath, "w") as file:
        json.dump(responses, file, indent=4)

# TalkBot Class
class TalkBot:
    def __init__(self, default_responses_path):
        self.memory = {}
        self.default_responses = load_default_responses(default_responses_path)
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 150)
        self.recognizer = sr.Recognizer()

    def speak(self, text):
        print(f"Bot: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        try:
            with sr.Microphone() as source:
                self.speak("I'm listening...")
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source)
                user_input = self.recognizer.recognize_google(audio)
                print(f"You: {user_input}")
                return user_input.lower().strip()
        except sr.UnknownValueError:
            self.speak("Sorry, I didn't catch that. Could you repeat?")
            return ""
        except sr.RequestError:
            self.speak("It seems there is an issue with the speech recognition service.")
            return ""

    def find_best_match(self, user_input):
        matches = get_close_matches(user_input, self.default_responses.keys(), n=1, cutoff=0.75)
        if matches:
            return matches[0]
        return None

    def respond(self, user_input):
        best_match = self.find_best_match(user_input)
        if best_match:
            response = self.default_responses[best_match]
            response = response.replace("{current_time}", datetime.now().strftime("%H:%M"))
            response = response.replace("{current_date}", datetime.now().strftime("%Y-%m-%d"))
            response = response.replace("{current_day}", datetime.now().strftime("%A"))
            self.speak(response)
        elif user_input in self.memory:
            self.speak(self.memory[user_input])
        else:
            self.speak("I don't know the answer to that. Can you teach me?")
            new_response = self.listen()
            if new_response:
                self.memory[user_input] = new_response
                self.speak("Got it! I'll remember that for next time.")

    def run(self):
        self.speak("Hello! How can I assist you today?")
        while True:
            user_input = self.listen()
            if not user_input:
                continue
            if user_input in ["exit", "quit"]:
                self.speak("Goodbye! Have a great day.")
                break
            self.respond(user_input)

# Emergency Alert Functionality
def send_emergency_alert():
    try:
        subject = "Emergency Alert!"
        body = "This is an emergency! Please check on me immediately."
        message = MIMEText(body)
        message["Subject"] = subject
        message["From"] = SENDER_EMAIL
        message["To"] = f"{RELATIVE_EMAIL}, {RELATIVE_PHONE_SMS}"
        print("Connecting to the SMTP server...")
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(message)
            print("Emergency alert sent successfully!")
    except Exception as e:
        print(f"Error sending alert: {e}")

def listen_for_emergency_code():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    print("Listening for the emergency code...")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        while True:
            try:
                print("Please speak...")
                audio = recognizer.listen(source)
                detected_text = recognizer.recognize_google(audio).lower()
                print(f"You said: {detected_text}")
                if EMERGENCY_CODE in detected_text:
                    print("Emergency code detected!")
                    send_emergency_alert()
                    break
            except sr.UnknownValueError:
                print("Sorry, I didn't catch that. Please try again.")
            except sr.RequestError as e:
                print(f"Speech recognition error: {e}")
                break

# Reminder System
def time_to_minutes(period, time_input):
    time_obj = datetime.strptime(time_input, "%I:%M")
    hour = time_obj.hour
    minutes = time_obj.minute
    if period.lower() == "p" and hour != 12:
        hour += 12
    elif period.lower() == "a" and hour == 12:
        hour = 0
    return hour * 60 + minutes

def add_reminder(reminders):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for the time of the reminder (e.g., 2:30 a/p)...")
        audio = recognizer.listen(source)
        time_with_period = recognizer.recognize_google(audio).lower()
        if " " in time_with_period:
            time_input, period = time_with_period.split()
            period = period[0]
        time_in_minutes = time_to_minutes(period, time_input)
        print("Listening for the task description...")
        audio = recognizer.listen(source)
        task_input = recognizer.recognize_google(audio).upper()
        reminders.append({"time": time_in_minutes, "task": task_input})
        print(f"Reminder added: {task_input} at {time_in_minutes} minutes from midnight")

def check_reminders(reminders):
    notified_tasks = set()
    while True:
        now = datetime.now()
        current_minutes = now.hour * 60 + now.minute
        for reminder in reminders:
            if current_minutes == reminder["time"] and reminder["time"] not in notified_tasks:
                print(f"Reminder: {reminder['task']}")
                notified_tasks.add(reminder["time"])
        time.sleep(30)

if __name__ == "__main__":
    bot = TalkBot(DEFAULT_RESPONSES_PATH)
    reminders = []

    print("Starting Integrated Assistant...")
    while True:
        print("Menu: 1. Chatbot  2. Emergency Alert  3. Reminder System  4. Exit")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            bot.run()
        elif choice == "2":
            listen_for_emergency_code()
        elif choice == "3":
            add_reminder(reminders)
            check_reminders(reminders)
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")