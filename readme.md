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
There is a dockerfile for those that like to build and run them. I will assume you know how to access your machine running docker.
1. Open your Terminal
2. Run command: git clone https://github.com/AustralianSimon/storyparkScraper.git StoryParkScraper
3. Run command: cd StoryParkScraper
4. Run command: sudo docker build -t storyparkscraper:latest .
5. Run using docker-compose such as example in project.

### Captcha & MFA
Storypark now uses a captcha and MFA on login. When the scraper needs you to complete either, it prints a message and starts a login assist page at http://localhost:8000 (or http://<docker-host>:8000 for docker - make sure port 8000 is published as in the docker-compose example).
1. Open the page in your browser, you will see a live view of the scraper's browser.
2. Click on the screenshot to click in the scraper's browser (e.g. captcha image tiles, the MFA code field).
3. Type into the text box and press Type / Enter to send text such as your MFA code.
4. Once logged in the scraper continues automatically. If it does not, press "I'm logged in - continue".

The login session is saved to `session/storage_state.json` (mount `/app/session` in docker) so you should only need to do this when the session expires. Keep this file private, it grants access to your account.

Running outside docker you can also set `HEADLESS=0` to show the browser window and complete the login directly in it.

Note the login assist page has no password, only expose port 8000 on a trusted network.

### .env file (optional)
- Just create a .env file in the directory you clone the project to.

---

### Contributors

Written mostly in python by Simon Wise.

---

#### Open to pull requests