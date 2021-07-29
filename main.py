import json
import threading
import time
import re
import pyttsx3
import requests
import speech_recognition as sr
import tkinter as tk
import webbrowser



API_KEY = "tWSPbOMpGCdT"
PROJECT_TOKEN = "tRRT_YiRFaMs"
RUN_TOKEN = "taVzMLqyQmff"



window = tk.Tk()
window.geometry("590x400")


window.title("Covid Voice Assistant")
window.configure(background= "black")
photo1 = tk.PhotoImage(file="covid png.png")
w = tk.Label(window, image = photo1)
w.grid(row = 0, column = 0)


tk.Label(window, image = photo1, bg="black").grid(row = 0, column = 0)
tk.Label(window, text = "Press the speak button to enter voice input", bg= "black", fg="white", font = "none 12 bold").grid(row = 1, column = 0)
tk.Label(window, text = "Commands: Update, Total Cases, Total Deaths, Country specific data, Stop", bg= "black", fg="white", font = "none 12 bold").grid(row = 2, column = 0)

new = 1
url = "https://linktr.ee/mhVaccineTracker"

def openweb():
    webbrowser.open(url, new=new)


tk.Label(window, text = "Click here to get vaccine notification", bg= "black", fg="white", font = "none 12 bold").grid(row = 5, column = 0)
btn = tk.Button(window, text = "Go To Page", command = openweb, bg = "grey").grid(row = 6, column = 0)



class Data:
	def __init__(self, api_key, project_token):
		self.api_key = api_key
		self.project_token = project_token
		self.params = {
			"api_key": self.api_key
		}
		self.data = self.get_data()

	def get_data(self):
		response = requests.get(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/last_ready_run/data', params={"api_key" : API_KEY})
		data = json.loads(response.text)
		return data

	def get_total_cases(self):
		data = self.data['total']

		for content in data:
			if content['name'] == "Coronavirus Cases:":
				return content['value']

	def get_total_deaths(self):
		data = self.data['total']

		for content in data:
			if content['name'] == "Deaths:":
				return content['value']

		return "0"

	def get_country_data(self, country):
		data = self.data["country"]

		for content in data:
			if content['name'].lower() == country.lower():
				return content

		return "0"

	def get_list_of_countries(self):
		countries = []
		for country in self.data['country']:
			countries.append(country['name'].lower())

		return countries

	def update_data(self):
		response = requests.post(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/run', params=self.params)

		def poll():
			time.sleep(0.1)
			old_data = self.data
			while True:
				new_data = self.get_data()
				if new_data != old_data:
					self.data = new_data
					print("Data updated")
					break
				time.sleep(5)


		t = threading.Thread(target=poll)
		t.start()


def speak(text):
	engine = pyttsx3.init()
	engine.say(text)
	engine.runAndWait()


def get_audio():
	r = sr.Recognizer()
	with sr.Microphone() as source:
		audio = r.listen(source)
		said = ""


		# if try does not work said will return blank string
		try:
			said = r.recognize_google(audio)
		except Exception as e:
			print("Exception: Please give valid input", str(e))

	return said.lower()




def main():
	print("Started Program")
	data = Data(API_KEY, PROJECT_TOKEN)
	END_PHRASE = "stop"
	country_list = data.get_list_of_countries()


	# regex patterns for matching input
	# \w\s means any number of words
	TOTAL_PATTERNS = {
					re.compile("[\w\s]+ total [\w\s]+ cases"):data.get_total_cases,
					re.compile("[\w\s]+ total cases"): data.get_total_cases,
                    re.compile("[\w\s]+ total [\w\s]+ deaths"): data.get_total_deaths,
                    re.compile("[\w\s]+ total deaths"): data.get_total_deaths
					}

	COUNTRY_PATTERNS = {
					re.compile("[\w\s]+ cases [\w\s]+"): lambda country: data.get_country_data(country)['total_cases'],
                    re.compile("[\w\s]+ deaths [\w\s]+"): lambda country: data.get_country_data(country)['total_deaths'],
					}

	UPDATE_COMMAND = "update"

	while True:
		print("Listening...")
		text = get_audio()
		print(text)
		result = None

		for pattern, func in COUNTRY_PATTERNS.items():
			if pattern.match(text):
				words = set(text.split(" "))    # query broken down into set of words
				for country in country_list:
					if country in words:
						result = func(country)   # if country matches call associated func
						break

		for pattern, func in TOTAL_PATTERNS.items():
			if pattern.match(text):
				result = func()  # calling function associated with matched pattern
				break

		if text == UPDATE_COMMAND:
			result = "Data is being updated. This may take a moment!"
			data.update_data()

		# if result exists speak result
		if result:
			speak(result)
			print(result)


		if text.find(END_PHRASE) != -1:  # stop loop
			print("Exit")
			break


myButton = tk.Button(window, text = "SPEAK", command = main, bg= "grey").grid(row = 3, column = 0)


window.mainloop()





