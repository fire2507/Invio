import speech_recognition as sr
import pyttsx3

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speed of speech

# Function to speak text
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to listen for voice input
def listen(prompt):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak(prompt)
        print(prompt)  # Debugging output
        try:
            audio = recognizer.listen(source, timeout=10)
            response = recognizer.recognize_google(audio)
            print(f"User said: {response}")  # Debugging output
            return response.lower()
        except sr.UnknownValueError:
            speak("Sorry, I didn't understand that. Could you please repeat?")
            return None
        except sr.RequestError:
            speak("There seems to be an issue with the microphone or recognition service.")
            return None

# Predefined locations and routes
locations = {
    "malviya nagar": "A residential and commercial area in Jaipur.",
    "vaishali nagar": "A posh locality in Jaipur known for its vibrant markets.",
    "tonk road": "A major road connecting various parts of Jaipur.",
    "ajmer road": "A highway leading to Ajmer from Jaipur.",
    "delhi": "The capital city of India.",
    "jaipur": "The Pink City and the capital of Rajasthan.",
    "niwai": "A small town near Jaipur.",
    "banasthali vidyapith": "A renowned women's university near Tonk."
}

routes = {
    ("delhi", "jaipur"): [
        "Start from Delhi.",
        "Take NH48 and continue on the Jaipur-Delhi Highway.",
        "Drive for approximately 260 kilometers.",
        "Follow signs for Jaipur and take the exit towards the city center.",
        "You have arrived in Jaipur."
    ],
    ("niwai", "jaipur"): [
        "Start from Niwai.",
        "Take the NH52 road towards Jaipur.",
        "Continue straight for about 65 kilometers.",
        "Enter Jaipur via Tonk Road.",
        "You have arrived in Jaipur."
    ],
    ("banasthali vidyapith", "delhi"): [
        "Start from Banasthali Vidyapith.",
        "Head towards Tonk and join NH52.",
        "Drive north to Jaipur and merge onto NH48.",
        "Continue on NH48 towards Delhi for approximately 260 kilometers.",
        "You have arrived in Delhi."
    ]
}

# Nearby train stations and bus stands
travel_options = {
    "train station": {
        "malviya nagar": "Gandhinagar Jaipur Railway Station",
        "vaishali nagar": "Jaipur Junction Railway Station",
        "niwai": "Niwai Railway Station",
        "banasthali vidyapith": "Banasthali Niwai Railway Station",
        "delhi": "New Delhi Railway Station",
        "jaipur": "Jaipur Junction Railway Station"
    },
    "bus stand": {
        "malviya nagar": "Malviya Nagar Bus Stand",
        "vaishali nagar": "Vaishali Nagar Bus Stand",
        "niwai": "Niwai Bus Depot",
        "banasthali vidyapith": "Tonk Bus Depot",
        "delhi": "ISBT Kashmiri Gate",
        "jaipur": "Sindhi Camp Bus Stand"
    }
}

# Function to provide nearby travel options
def get_travel_option(location, option_type):
    if location not in locations or option_type not in travel_options:
        speak("Sorry, I couldn't find the information you requested.")
        return None

    option = travel_options[option_type].get(location)
    if option:
        speak(f"The nearest {option_type} is {option}.")
        print(f"The nearest {option_type} is {option}.")  # Debugging output
    else:
        speak(f"Sorry, no {option_type} information is available for {location}.")
        print(f"No {option_type} information for {location}.")  # Debugging output

# Function to navigate between two points
def navigate(start, destination):
    if start not in locations or destination not in locations:
        speak("Sorry, I couldn't find one of the locations you mentioned.")
        return

    route = routes.get((start, destination))
    if not route:
        speak(f"Sorry, I don't have a predefined route from {start} to {destination}.")
        return

    speak(f"Starting navigation from {start.capitalize()} to {destination.capitalize()}.")
    for step in route:
        speak(step)
        print(step)  # Debugging output
    speak(f"You have arrived at {destination.capitalize()}. Thank you for using this navigation system.")

# Main function for the navigation system
def navigation_system():
    while True:
        speak("Welcome to the voice-controlled navigation system.")
        action = listen("What would you like to do? You can say 'navigate', 'find train station', 'find bus stand', or 'exit'.")
        if action is None:
            continue

        if "navigate" in action:
            start = None
            while not start:
                start = listen("Please tell me your current location.")
            destination = None
            while not destination:
                destination = listen("Where would you like to go?")
            navigate(start.lower(), destination.lower())

        elif "train station" in action:
            location = listen("Please tell me your location to find the nearest train station.")
            if location:
                get_travel_option(location.lower(), "train station")

        elif "bus stand" in action:
            location = listen("Please tell me your location to find the nearest bus stand.")
            if location:
                get_travel_option(location.lower(), "bus stand")

        elif "exit" in action:
            speak("Thank you for using the navigation system. Have a great day!")
            break

        else:
            speak("Sorry, I didn't understand that. Please try again.")

# Run the navigation system
if __name__ == "__main__":
    navigation_system()