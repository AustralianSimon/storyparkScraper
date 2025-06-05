import os, time, requests, piexif
from datetime import datetime

from PIL import Image
from PIL.ExifTags import TAGS

import config as cf
import util_playwright
import util_playwright as pw

def open_website(page, url):
    """
    Opens the website.
    """
    page.goto(url)
    if page.title() == 'Log in | Storypark':
        page.fill(cf.elems['user_field'], cf.creds['user'])
        page.fill(cf.elems['pass_field'], cf.creds['pass'])
        page.click(cf.elems['log_in_button'], timeout=60000)

def get_children(page):
    """
    Reads all available children names from the side menu.
    """
    print('get_children')
    open_website(page, cf.base_url)
    page.click(cf.elems['main_menu_button'], timeout=60000)
    page.wait_for_timeout(1000)
    elements = page.query_selector_all(cf.elems['child_menu_item'])
    for element in elements:
        name_element = element.query_selector(cf.elems['child_name_label'])
        child_name = name_element.inner_text().strip()

        href = element.get_attribute('href')
        child_code = None
        if href and href.startswith('#child-navigation'):
            child_code = href.replace('#child-navigation-', '')

        if child_code and child_name:
            print(f'Child: {child_code} - {child_name}')
            cf.children[child_name] = cf.stories_url.replace('CHILD_CODE', child_code)

def scroll_until_stable(page):
    """
    Scrolls the page down until the bottom of the page or if the recent only limit is reached.
    """
    previous_content = page.content()
    counter = 0
    while True:
        # Scroll to the bottom of the page
        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')

        # Wait for a brief period
        page.wait_for_timeout(cf.page_timeout)

        current_content = page.content()

        # Checking to see if the page content has changed or reached bottom of page
        if current_content == previous_content:
            print('Bottom of story page')
            break
        elif counter == 2:
            if not cf.get_all_images:
                print('Scroll limit reached')
                break
            print('Getting all images, this will take a while...')
        previous_content = current_content
        counter += 1

def collect_all_posts(page):
    """
    Gets all posts on the currently loaded parts of the page.
    """
    elements = page.query_selector_all(cf.elems['post'])
    storypark_ids = []
    for element in elements:
        storypark_id = element.get_attribute('storyparkid')
        storypark_ids.append(storypark_id)
    print(f'Storypark Post Count: {len(storypark_ids)}')
    return storypark_ids

def download_story_images(page, id, save_dir):
    """
    Downloads all story images from the post.
    Will first check if the story has already been downloaded and if so skip.
    Will then check if exif has been done if for some reason the date file is missing and skip.
    """
    if os.path.exists(os.path.join(save_dir,'date.txt')):
        print('Previously dated')
        return
    if os.path.exists(os.path.join(save_dir,'done.txt')):
        print('Previously downloaded')
        return
    print(save_dir)
    base_url = 'https://app.storypark.com/stories/'
    full_url = base_url + str(id)
    page.goto(full_url)
    time.sleep(20)
    page.wait_for_load_state('networkidle', timeout=cf.images_idle)

    date_value = page.query_selector(cf.elems['date'])
    if date_value:
        date_value_content = date_value.text_content().strip()
    else:
        date_value_content = ''
    print(date_value_content)
    with open(os.path.join(save_dir, 'date.txt'), 'w') as f:
        f.write(date_value_content)

    elements = page.query_selector_all(cf.elems['post_images'])
    print(f'Image count: {len(elements)}')
    for element in elements:
        print(f'Element: {element.get_attribute('src')}')
        src_value = element.get_attribute('src')
        try:
            response = requests.get(src_value)
            if response.status_code == 200:

                filename = src_value.split('/')[-2]
                full_filename = os.path.join(save_dir, filename) + '.jpg'

                with open(full_filename, 'wb') as file:
                    file.write(response.content)
                print(f"Downloaded: {full_filename}")
            else:
                print(response.status_code)
        except:
            pass

    with open(os.path.join(save_dir, 'done.txt'), 'w') as f:
        f.write('d')

def download_story_vids(page, id, save_dir):
    """
    Downloads all story videos from the post.
    Will first check if the story has already been downloaded and if so skip.
    Will then check if exif has been done if for some reason the date file is missing and skip.
    """
    if os.path.exists(os.path.join(save_dir,'date.txt')):
        print('Previously dated')
        return
    if os.path.exists(os.path.join(save_dir,'done.txt')):
        print('Previously downloaded')
        return
    print(save_dir)
    base_url = 'https://app.storypark.com/stories/'
    full_url = base_url + str(id)
    page.goto(full_url)
    time.sleep(20)
    page.wait_for_load_state('networkidle', timeout=cf.images_idle)

    date_value = page.query_selector(cf.elems['date'])
    if date_value:
        date_value_content = date_value.text_content().strip()
    else:
        date_value_content = ''
    print(date_value_content)
    with open(os.path.join(save_dir, 'date.txt'), 'w') as f:
        f.write(date_value_content)

    elements = page.query_selector_all(cf.elems['post_vids'])
    print(f'Vid count: {len(elements)}')
    for element in elements:
        print(f'Element: {element.get_attribute('src')}')
        src_value = element.get_attribute('src')
        try:
            response = requests.get(src_value)
            if response.status_code == 200:

                filename = src_value.split('/')[-2]
                full_filename = os.path.join(save_dir, filename) + '.mp4'

                with open(full_filename, 'wb') as file:
                    file.write(response.content)
                print(f"Downloaded: {full_filename}")
            else:
                print(response.status_code)
        except:
            pass

    with open(os.path.join(save_dir, 'done.txt'), 'w') as f:
        f.write('d')

def collect_all_notes(page):
    """
    Gets all notes on the currently loaded parts of the page.
    """
    elements = page.query_selector_all(cf.elems['note'])
    storypark_ids = []
    for element in elements:
        storypark_id = element.get_attribute('data-post')
        storypark_ids.append(storypark_id)
    print(f'Storypark Note Count: {len(storypark_ids)}')
    return storypark_ids

def collect_all_community_posts(page):
    """
    Gets all notes on the currently loaded parts of the page.
    """
    elements = page.query_selector_all(cf.elems['note'])
    storypark_ids = []
    for element in elements:
        storypark_id = element.get_attribute('data-post')
        storypark_ids.append(storypark_id)
    print(f'Storypark Note Count: {len(storypark_ids)}')
    return storypark_ids

def download_note_images(page, id, save_dir):
    """
    Downloads all note images from the note.
    Will first check if the note has already been downloaded and if so skip.
    Will then check if exif has been done if for some reason the date file is missing and skip.
    """
    if os.path.exists(os.path.join(save_dir,'date.txt')):
        print('Previously dated')
        return
    if os.path.exists(os.path.join(save_dir,'done.txt')):
        print('Previously downloaded')
        return
    print(save_dir)
    base_url = 'https://app.storypark.com/activity/?note_id='
    full_url = base_url + str(id)
    page.goto(full_url)
    time.sleep(20)
    page.wait_for_load_state('networkidle', timeout=cf.images_idle)

    date_value = page.query_selector(cf.elems['date'])
    if date_value:
        date_value_content = date_value.text_content().strip()
    else:
        date_value_content = ''
    print(date_value_content)
    with open(os.path.join(save_dir, 'date.txt'), 'w') as f:
        f.write(date_value_content)

    elements = page.query_selector_all(cf.elems['post_images'])
    print(f'Image count: {len(elements)}')
    for element in elements:
        print(f'Element: {element.get_attribute('src')}')
        src_value = element.get_attribute('src')
        try:
            response = requests.get(src_value)
            if response.status_code == 200:

                filename = src_value.split('/')[-2]
                full_filename = os.path.join(save_dir, filename) + '.jpg'

                with open(full_filename, 'wb') as file:
                    file.write(response.content)
                print(f"Downloaded: {full_filename}")
            else:
                print(response.status_code)
        except:
            pass


def modify_exif_date(image_path, new_date):
    """
    Takes file path and date to modify the EXIF data to.
    """
    print(f'Modifying EXIF for {image_path}')
    image = Image.open(image_path)
    exif_data = image._getexif()

    try:
        for tag_id, value in exif_data.items():
            tag_name = TAGS.get(tag_id, tag_id)
            if tag_name == 'DateTimeOriginal':
                exif_data[tag_id] = new_date
        image.save(image_path, exif=image.info["exif"])
        return
    except Exception as e:
        print(f'No EXIF data: {e}')
        pass
    try:
        exif_dict = {}

        if "exif" in image.info:
            exif_dict = piexif.load(image.info["exif"])

        if "Exif" not in exif_dict:
            exif_dict["Exif"] = {}

        exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = new_date

        exif_bytes = piexif.dump(exif_dict)
        image.save(image_path, exif=exif_bytes)

    except:
        pass

def updateMetaData(folder):
    """
    Opens the subfolder and reads the date in the date.txt file.
    Applies the date to EXIF data for all files.
    """
    print(folder)
    date_new = ''
    if 'done.txt' in folder[-1]:
        print('Done.')
        return

    file_path = os.path.join(folder[0], 'date.txt')
    if 'date.txt' in folder[-1]:
        print('Has data.')
        with open(file_path,'r') as f:
            date_new = f.readlines()
    else:
        return
    print(date_new[0])
    datetime_new = datetime.strptime(date_new[0].strip(),'%d %B %Y')
    datetime_new = datetime_new.replace(hour=12, minute=0, second=0)
    print(datetime_new)
    for image_file in folder[-1]:
        if image_file.endswith('.txt') or image_file.endswith('.mp4'):
            continue
        modify_exif_date(os.path.join(folder[0],image_file),datetime_new.strftime("%Y:%m:%d %H:%M:%S"))
    with open(file_path, 'w') as f:
        f.write('d')

if __name__ == '__main__':
    """
    Performs all the logic.
    """
    browser = pw.create_browser_instance(False)
    page = pw.create_page_instance(browser)
    get_children(page)

    for key in cf.children:
        print(f'Getting images for: {key}')
        current_path = os.getcwd()
        temp_path = os.path.join(current_path, 'images')
        os.makedirs(name=temp_path, exist_ok=True)
        temp_path = os.path.join(temp_path, key)
        list_folders = os.walk(temp_path)

        open_website(page, cf.children[key])
        scroll_until_stable(page)
        time.sleep(10)
        id_list = collect_all_posts(page)

        for id in id_list:
            os.makedirs(os.path.join(temp_path,id), exist_ok=True)
            download_story_images(page, id, (os.path.join(temp_path,id)))
            download_story_vids(page, id, (os.path.join(temp_path, id)))

            with open(os.path.join((os.path.join(temp_path,id)), 'done.txt'), 'w') as f:
                f.write('d')

    time.sleep(10)
    util_playwright.close_instance(browser)

    for key in cf.children:
        print(f'Set metadata for: {key}')
        current_path = os.getcwd()
        temp_path = os.path.join(current_path, 'images')
        os.makedirs(name=temp_path, exist_ok=True)
        temp_path = os.path.join(temp_path, key)
        list_folders = os.walk(temp_path)
        for folder in list_folders:
            updateMetaData(folder)

        print('Ending')