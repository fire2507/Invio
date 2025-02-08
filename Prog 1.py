import streamlit as st
import threading
import subprocess

from nevigation import navigation_system
from integratedass import TalkBot, listen_for_emergency_code
from integratedcam import integrate_system

def start_navigation():
    st.write("Starting navigation system...")
    threading.Thread(target=navigation_system).start()

def start_voice_assistant():
    st.write("Starting voice assistant...")
    bot = TalkBot("default_responses.json")
    threading.Thread(target=bot.run).start()

def start_object_detection():
    st.write("Starting object detection and sentiment analysis system...")
    threading.Thread(target=integrate_system).start()

def start_emergency_alert():
    st.write("Listening for emergency alert trigger...")
    threading.Thread(target=listen_for_emergency_code).start()

def main():
    st.title("Smart Navigation System for Visually Impaired")
    st.markdown(
        """This application integrates multiple features to assist visually impaired individuals:
        - **Navigation System**: Voice-based navigation.
        - **Voice Assistant**: Provides assistance through voice commands.
        - **Object Detection and Sentiment Analysis**: Detects objects, reads text, and analyzes sentiment in real-time.
        - **SOS Alerts**: Sends emergency alerts when triggered."
        """
    )

    st.sidebar.title("Features")
    feature = st.sidebar.selectbox("Choose a feature to use:", [
        "Navigation System",
        "Voice Assistant",
        "Object Detection and Sentiment Analysis",
        "SOS Emergency Alert"
    ])

    if feature == "Navigation System":
        st.header("Navigation System")
        st.write("Start the voice-controlled navigation system.")
        if st.button("Start Navigation"):
            start_navigation()

    elif feature == "Voice Assistant":
        st.header("Voice Assistant")
        st.write("Interact with the AI-based voice assistant.")
        if st.button("Start Voice Assistant"):
            start_voice_assistant()

    elif feature == "Object Detection and Sentiment Analysis":
        st.header("Object Detection and Sentiment Analysis")
        st.write("Start the camera-based system for real-time analysis.")
        if st.button("Start System"):
            start_object_detection()

    elif feature == "SOS Emergency Alert":
        st.header("SOS Emergency Alert")
        st.write("Activate emergency alert monitoring.")
        if st.button("Start SOS Alert System"):
            start_emergency_alert()

if __name__ == "__main__":
    main()