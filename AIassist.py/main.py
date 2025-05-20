import tkinter as tk
from PIL import Image, ImageTk
import pyttsx3 as p
import speech_recognition as sr
import webbrowser
import time
import requests
from datetime import datetime
import pyautogui
import subprocess
from bs4 import BeautifulSoup
import random
import os
import threading

# Global variable to keep track of whether the assistant is running
running = True

# Initialize the main window
root = tk.Tk()
root.title("Voice Assistant")
root.attributes('-fullscreen', True)  # Set the window to full screen
root.configure(bg='#7DCEF5')  # Set a light blue background

# Create a frame to hold all the components
main_frame = tk.Frame(root, bg='#7DCEF5')
main_frame.pack(expand=True)  # Use expand to center the frame in the window

# Function to load GIF frames
def load_gif_frames(file_path, size):
    frames = []
    try:
        gif = Image.open(file_path)
        for frame in range(gif.n_frames):
            gif.seek(frame)  # Move to the frame
            frame_image = gif.copy().convert("RGBA").resize(size, Image.LANCZOS)
            frames.append(ImageTk.PhotoImage(frame_image))
    except Exception as e:
        print(f"Error loading GIF: {e}")
    return frames

# Function to animate the GIF
def animate_gif(label, frames, frame_index, speed):
    label.config(image=frames[frame_index])
    frame_index = (frame_index + 1) % len(frames)
    root.after(speed, lambda: animate_gif(label, frames, frame_index, speed))  # Change frame based on speed

# Load and animate the GGenie.gif (larger size, faster animation)
genie_frames = load_gif_frames(r"C:\Users\HP\Desktop\GGenie.gif", (500, 500))  # Larger size
genie_label = tk.Label(main_frame, bg='#7DCEF5')  # Match label background with window
genie_label.pack(pady=20)  # Add vertical padding

if genie_frames:
    animate_gif(genie_label, genie_frames, 0, 100)  # Start animating the genie GIF at a faster speed

# Add a welcome message
welcome_label = tk.Label(main_frame, text="Your Wish is my Command", font=("Palatino Linotype", 40), bg='#7DCEF5')
welcome_label.pack(pady=20)  # Add vertical padding

# Load and animate the MIC.gif (smaller size, slower animation)
mic_frames = load_gif_frames(r"C:\Users\HP\Desktop\MIC.gif", (150, 150))  # Smaller size
mic_label = tk.Label(main_frame, bg='#7DCEF5')
mic_label.pack(pady=20)  # Add vertical padding

if mic_frames:
    animate_gif(mic_label, mic_frames, 0, 200)  # Start animating the mic GIF at a slower speed

# Function to start the countdown and show mic
def start_countdown_and_show_mic():
    root.after(4000, show_mic)  # Show the mic GIF after 4 seconds

# Function to show the microphone GIF
def show_mic():
    mic_label.pack()  # Show the mic label
    animate_gif(mic_label, mic_frames, 0, 200)  # Start animating the microphone GIF

# Set Firefox as the default browser
webbrowser.register('firefox', None, webbrowser.BackgroundBrowser("C:/Program Files/Mozilla Firefox/firefox.exe"))

# Text-to-Speech Initialization
engine = p.init()
rate = engine.getProperty('rate')
engine.setProperty('rate', 130)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Function to toggle full screen
def toggle_fullscreen(event=None):
    root.attributes("-fullscreen", not root.attributes("-fullscreen"))

root.bind("<Escape>", toggle_fullscreen)  # Bind the Escape key to toggle full screen

# Bind the Ctrl + Q key to exit the application
def exit_application(event=None):
    global running
    running = False  # Set the flag to False to stop the assistant
    root.quit()  # Close the GUI

root.bind("<Control-q>", exit_application)  # Bind Ctrl + Q to exit the application

# Speech Recognition Initialization
r = sr.Recognizer()

def speak(text):
    mic_label.pack_forget()  # Hide mic label before speaking
    engine.say(text)
    engine.runAndWait()  # Wait until speaking is finished
    start_countdown_and_show_mic()  # Start the countdown and show mic after speaking

def listen_and_recognize():
    with sr.Microphone() as source:
        r.energy_threshold = 3000  # You may want to lower this value
        r.adjust_for_ambient_noise(source, duration=1.0)  # Adjust ambient noise
        print("Listening...")
        show_mic()  # Show mic GIF while listening
        try:
            audio = r.listen(source, timeout=5)  # Increase timeout if necessary
            text = r.recognize_google(audio)
            mic_label.pack_forget()  # Hide mic label after listening
            return text
        except sr.WaitTimeoutError:
            speak("I didn't hear you. Can you repeat again?")
            return None
        except sr.UnknownValueError:
            speak("I didn't hear you. Can you please repeat?")
            return listen_and_recognize()  # Recursive call to listen again
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            speak("There was an error with the speech recognition service.")
            return None

# Function to open a specified file
def open_file():
    speak("Please provide the file name you want to open from your desktop.")
    file_name = listen_and_recognize()  # Listen for the file name
    if file_name:
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        extensions = ["", ".txt", ".docx", ".pdf", ".pptx", ".xlsx"]  # Add other extensions as needed

        for ext in extensions:
            file_path = os.path.join(desktop_path, file_name + ext)
            if os.path.isfile(file_path):
                try:
                    subprocess.Popen([file_path], shell=True)
                    speak(f"I have opened the file {file_name}{ext} from your desktop.")
                    return
                except Exception as e:
                    speak("I couldn't open that file. Please check the file name and try again.")
                    print(f"Error: {e}")

        speak("That file does not exist on your desktop. Please try again.")

# Class for fetching information
class Infow():
    def get_info(self, query):
        print(f"Fetching information for: {query}")  # Debugging print statement
        url = f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"  # Format the query for URL
        webbrowser.get('firefox').open(url)  # Open in Firefox
        speak(f"I have opened Wikipedia for {query}.")
        
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        try:
            first_paragraph = soup.find('p').text
            speak(first_paragraph)  # Speak the first paragraph
        except Exception as e:
            speak("I couldn't find the information to read.")
            print(f"Error: {e}")

        speak(f"I have fetched information about {query}. You can check it on Wikipedia.")
        
    def play_video(self, video_title):
        print(f"Playing video: {video_title}")  # Debugging print statement
        search_url = f"https://www.youtube.com/results?search_query={video_title.replace(' ', '+')}"  # Format the video title for URL
        webbrowser.get('firefox').open(search_url)  # Open in Firefox
        speak(f"I have opened YouTube for {video_title}.")
        speak("Please select the video you want to play from the search results.")

def get_latest_news():
    api_key = "b8cd8a08bdde4d1e9e0816093bc9e637"  # Replace with your NewsAPI key
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"

    response = requests.get(url)
    
    if response.status_code == 200:
        news_data = response.json()
        articles = news_data.get("articles", [])
        
        if articles:
            speak("Here are the latest news headlines:")
            for article in articles[:5]:  # Read the top 5 articles
                title = article.get("title")
                speak(title)  # Read the title of each article
                print(title)  # Print to console for debugging
        else:
            speak("No news articles found.")
    else:
        speak("There was an error fetching the news.")

# Function to open Notepad and type the recognized text
def open_notepad_and_type():
    subprocess.Popen(['notepad.exe'])
    time.sleep(1)  

    speak("I will now type everything you say. Say 'stop typing' when you want me to stop.")

    while True:
        additional_text = listen_and_recognize()
        if additional_text:
            if "stop" in additional_text.lower():
                speak("Okay, I have stopped typing. How do you want me to save this file as?")
                file_name = listen_and_recognize()  # Listen for the file name
                if file_name:
                    pyautogui.hotkey('ctrl', 's')
                    time.sleep(1)  # Wait for the save dialog to open

                    pyautogui.typewrite(f"{file_name}.txt")  # Save as a .txt file
                    time.sleep(1)  # Wait a moment before hitting Enter

                    pyautogui.press('enter')
                    speak(f"I have saved your file as {file_name}.")
                    
                    pyautogui.hotkey('alt', 'f4')
                break
            else:
                pyautogui.typewrite(additional_text)  

# Global variable to keep track of told jokes
told_jokes = []

def tell_joke():
    jokes = [
        "Poppaa key nuveru, 5 + 5 yeathuu?????? . ayai kuu Raampa, key nuveyy, Daadaa Maarayyaa ... Avoolaa gotthoojja?, Calculator kanala.... Yaan panpeyy.",
        "Sompey : Yaanu thaara yida marakku, meethu phodu thoonda, manipaal hostel dhaa, ponnu lu thoju veru, gothoo undaa nikku, Rampey : aathe naa...? nadutu, kayi budu du thoola gey, Manipal Hospital dah nursoo naku loo, thoju veru",
        "Police:: Ee, akash naah watch, daaaye kann dini?.  ayik Kaluvey:, Yan kandu  diji, aaye ney kori ini. ayiku, Police: Aaye nikku yeapa kori ini?,  ayiku Kaluvey panupey: Yan bee satthi, thojaa naga"
    ]

    if len(told_jokes) >= len(jokes):
        told_jokes.clear()  # Reset the list if all jokes have been told

    available_jokes = [joke for joke in jokes if joke not in told_jokes]
    joke = random.choice(available_jokes)
    told_jokes.append(joke)  # Add the chosen joke to the list of told jokes

    speak(joke)

def get_current_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    speak(f"The current time is {current_time}.")

def get_current_date():
    now = datetime.now()
    current_date = now.strftime("%B %d, %Y")  # Format: Month Day, Year
    speak(f"The current date is {current_date}")

def basic_calculator(expression):
    try:
        expression = expression.replace("plus", "+").replace("minus", "-").replace("times", "*").replace("divided by", "/")
        expression = expression.replace("x", "*").replace("/", "/")  # Handle 'x' as multiplication
        expression = expression.replace("negative", "-")  # Allow saying "negative" for "-"
        
        number_words = {
            "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
            "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
            "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
            "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
            "eighteen": 18, "nineteen": 19, "twenty": 20
        }

        for word, number in number_words.items():
            expression = expression.replace(word, str(number))

        result = eval(expression)
        speak(f"The result of {expression} is {result}.")
        return True  # Indicate that the calculation was successful
    except Exception as e:
        speak("I couldn't calculate that. Please try again.")
        return False  # Indicate that the calculation failed

# Main Assistant Functionality
def main_assistant():
    global running  # Use the global variable
    speak("Hello, I'm your VoiceGenie. daada sahaaya manu phodu?")

    video_playing = False  # Flag to track if a video is being played

    while running:  # Keep running while the flag is True
        user_response = listen_and_recognize()

        if user_response:
            if "open" in user_response.lower() or "files" in user_response.lower():
                open_file()  # Call the function to open a file
                speak("Is there anything else you want me to help with?")

            elif "tulu" in user_response.lower() or "joke" in user_response.lower():
                tell_joke()
                speak("Is there anything else you want me to help with?")

            elif "time" in user_response.lower():
                get_current_time()
                speak("Is there anything else you want me to help with?")

            elif "date" in user_response.lower():
                get_current_date()  # Call the new function for date
                speak("Is there anything else you want me to help with?")

            elif "current date time" in user_response.lower():
                get_current_date()  
                speak("Is there anything else you want me to help with?")

            elif "calculate" in user_response.lower() or "calculation" in user_response.lower():
                speak("What calculation do you want me to perform? You can say something like 'four times four' or 'four x four'.")
                expression = listen_and_recognize()
                if expression:
                    basic_calculator(expression)
                    speak("Is there anything else you want me to help with?")

            elif "video" in user_response.lower() or "play" in user_response.lower():
                speak("Which video do you want me to play?")
                topic = listen_and_recognize()
                
                if topic:
                    print(f"Searching YouTube for video on: {topic}")  # Debugging print statement
                    assist = Infow()  # Create an instance of the Infow class
                    assist.play_video(topic)  # Call the play_video method with the topic
                    video_playing = True  # Set the flag to indicate a video is playing
                    speak("Is there anything you want me to help with?")

            elif "latest" in user_response or "news" in user_response or "todays" in user_response.lower():
                get_latest_news()  # Call the function to get latest news
                speak("Is there anything else you want me to help with?")

            elif "information" in user_response.lower() or "wikipedia" in user_response.lower():
                speak("You need information related to which topic?")
                topic = listen_and_recognize()
                
                if topic:
                    print(f"Searching for information on: {topic}")  # Debugging print statement
                    assist = Infow()  # Create an instance of the Infow class
                    assist.get_info(topic)  # Call the get_info method with the topic
                    speak("Is there anything you want me to help with?")

            elif "assistance" in user_response.lower() or "thank you" in user_response.lower() or "assistant" in user_response.lower():
                speak("You're welcome! Have a great day!")
                break

            elif "stop Speaking" in user_response.lower():
                speak("You're welcome! Have a great day!")
                break

            elif "notepad" in user_response.lower() or "type" in user_response.lower():
                open_notepad_and_type()
                speak("Is there anything you want me to help with?")
                
            else:
                if not video_playing:  # Only ask to repeat if not playing a video
                    speak("I'm sorry, I didn't understand that. What else can I help you with?")
        
        # Reset the video playing flag after checking user response
        if video_playing:
            video_playing = False

# Start the assistant in a separate thread
def start_assistant():
    main_assistant()

# Create a thread for the voice assistant
assistant_thread = threading.Thread(target=start_assistant)
assistant_thread.start()

# Start the GUI main loop
print("Starting the GUI...")
root.mainloop()

# Ensure the assistant thread has finished before closing the program
assistant_thread.join()  # Wait for the assistant thread to finish
print("Assistant has stopped. Closing application.")