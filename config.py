from os import getenv
from dotenv import load_dotenv

load_dotenv()

get_all_images = bool(getenv('ALL_IMAGES', 0))

page_timeout = int(getenv('PAGE_TIMEOUT', 60000))
images_idle = int(getenv('IMAGE_IDLE', 200000))

headless = getenv('HEADLESS', '1') != '0'
session_file = getenv('SESSION_FILE', 'session/storage_state.json')
auth_assist_host = getenv('AUTH_ASSIST_HOST', '0.0.0.0')
auth_assist_port = int(getenv('AUTH_ASSIST_PORT', 8000))
auth_timeout = int(getenv('AUTH_TIMEOUT', 600))

base_url = 'https://app.storypark.com/users/sign_in'
stories_url = 'https://app.storypark.com/children/CHILD_CODE/stories'

elems = {
    'story_page_button':"//span[contains(@class, 'sp-u--is-hidden-tablet-lg') and contains(text(), 'Stories')]",
    'log_in_button':"button[data-action='signin']",
    'user_field':"#user_email",
    'pass_field':"#user_password",
    'post':'div[data-action="show-post"]',
    'post_images':'img[alt="Story media"]',
    'post_vids':'video[controls]',
    'note':"//a[@data-action='show-post' and @data-collection='stories' and @data-type='story']",
    'community_post':"//a[contains(@href, 'community_posts')]",
    'note_images':'img[data-action="zoom-media"]',
    'date':'div.flex-shrink-0.text-h6.grey2--text.text--darken-1.font-weight-regular',
    'story_title':'h1.wysiwyg-font-size-title',
    'story_text':'div.wysiwyg-font-size-medium',
    'main_menu_button':'//button[contains(@class, "v-btn") and not(ancestor::nav) and .//span[contains(., "Menu")]]',
    'child_menu_item':'div[data-action="child-menu"] .v-list-group__header',
    'child_name_label':'.v-list-item__title[data-action="open-child-menu"]',
}

children = {

}

creds = {
    'user':getenv('SP_USER'),
    'pass':getenv('SP_PASS')
}