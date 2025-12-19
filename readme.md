# Storypark Scraper

---

### What does this do?
Simply downloads all story photos from your child's story posts in storypark to put into a photo album or other tool. Please note this indescriminately downloads images so you will need to filter out pictures your child is not in after download.

### Installation & Run

#### venv (easymode)
Assuming you have installed python. You can run this on your machine by doing the following.
1. Open your Terminal
2. Run command: git clone https://github.com/AustralianSimon/storyparkScraper.git StoryParkScraper
3. Run command: cd StoryParkScraper
4. Run command: python -m venv venv
5. Run command: venv\Scripts\activate.bat or source venv/bin/activate
6. Run command: pip install -r requirements.txt
7. Run command: python main.py

#### docker
NB - there is a known issue with docker atm so I recommend you run via venv
There is a dockerfile for those that like to build and run them. I will assume you know how to access your machine running docker.
1. Open your Terminal
2. Run command: git clone https://github.com/AustralianSimon/storyparkScraper.git StoryParkScraper
3. Run command: cd StoryParkScraper
4. Run command: sudo docker build -t storyparkscraper:latest .
5. Run using docker-compose such as example in project.

### .env file (optional)
- Just create a .env file in the directory you clone the project to.

---

### Contributors

Written mostly in python by Simon Wise.

---

#### Open to pull requests
