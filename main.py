import os, time, requests, piexif
from datetime import datetime

from PIL import Image
from PIL.ExifTags import TAGS

import config as cf
import util_playwright
import util_playwright as pw

def open_website(page, url):
    page.goto(url)
    #print(page.title())
    if page.title() == 'Log in | Storypark':
        #print('Log in')
        page.fill(cf.elems['user_field'], cf.creds['user'])
        page.fill(cf.elems['pass_field'], cf.creds['pass'])
        page.click(cf.elems['log_in_button'])
    #page.click(cf.elems['story_page_button'])

def get_children(page):
    print('get_children')
    open_website(page, cf.base_url)
    page.click(cf.elems['main_menu_button'])
    page.wait_for_timeout(1000)
    elements = page.query_selector_all(cf.elems['child_menu_item'])
    print(elements)
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
    print(cf.children)

def scroll_until_stable(page):
    previous_content = page.content()
    counter = 0
    while True:
        # Scroll to the bottom of the page
        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')

        # Wait for a brief period
        page.wait_for_timeout(60000)  # Adjust the timeout value as needed

        current_content = page.content()

        # Check if the page content has changed
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
    elements = page.query_selector_all(cf.elems['post'])

    storypark_ids = []
    for element in elements:
        storypark_id = element.get_attribute('storyparkid')
        storypark_ids.append(storypark_id)
    print(f'Storypark Post Count: {len(storypark_ids)}')
    return storypark_ids

def download_story_images(page, id, save_dir):
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
    page.wait_for_load_state('networkidle', timeout=200000)

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



        except Exception as e:
            print(e)
            pass

    with open(os.path.join(save_dir, 'done.txt'), 'w') as f:
        f.write('d')

def modify_exif_date(image_path, new_date):
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
        #no EXIF data
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

    except Exception as e:
        #issue with adding EXIF
        print(f'Broken during add: {e}')
        pass

def updateMetaData(folder):
    print(folder)
    date_new = ''
    if 'date.txt' in folder[-1]:
        print('Has data.')
        file_path = os.path.join(folder[0], 'date.txt')
        with open(file_path,'r') as f:
            date_new = f.readlines()
    else:
        return
    print(date_new[0])
    datetime_new = datetime.strptime(date_new[0].strip(),'%d %B %Y')
    datetime_new = datetime_new.replace(hour=12, minute=0, second=0)
    print(datetime_new)
    for image_file in folder[-1]:
        if image_file.endswith('.txt'):
            continue
        modify_exif_date(os.path.join(folder[0],image_file),datetime_new.strftime("%Y:%m:%d %H:%M:%S"))


if __name__ == '__main__':

        browser = pw.create_browser_instance(False)
        page = pw.create_page_instance(browser)
        get_children(page)

        for key in cf.children:
            print(f'Getting images for: {key}')
            os.makedirs(name=key,exist_ok=True)
            current_path = os.getcwd()
            temp_path = os.path.join(current_path, 'images')
            temp_path = os.path.join(temp_path, key)
            list_folders = os.walk(temp_path)

            open_website(page, cf.children[key])
            scroll_until_stable(page)
            time.sleep(10)
            id_list = collect_all_posts(page)

            for id in id_list:
                os.makedirs(os.path.join(temp_path,id), exist_ok=True)
                download_story_images(page, id, (os.path.join(temp_path,id)))

        time.sleep(10)
        util_playwright.close_instance(browser)

        for key in cf.children:
            print(f'Set metadata for: {key}')
            os.makedirs(name=key,exist_ok=True)
            current_path = os.getcwd()
            temp_path = os.path.join(current_path, key)
            list_folders = os.walk(temp_path)
            for folder in list_folders:
                updateMetaData(folder)

        print('Ending')