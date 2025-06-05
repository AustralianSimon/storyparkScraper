from os import getenv
from dotenv import load_dotenv

load_dotenv()

get_all_images = bool(getenv('ALL_IMAGES', 0))

page_timeout = int(getenv('PAGE_TIMEOUT', 60000))
images_idle = int(getenv('IMAGE_IDLE', 200000))

base_url = 'https://app.storypark.com/users/sign_in'
stories_url = 'https://app.storypark.com/children/CHILD_CODE/stories'

elems = {
    'story_page_button':"//span[contains(@class, 'sp-u--is-hidden-tablet-lg') and contains(text(), 'Stories')]",
    'log_in_button':".sp-c-btn.sp-c-btn--med.sp-c-primary-btn.sp-c-primary-btn--lg.sp-u-padding-horizontal--med[data-action='signin']",
    'user_field':"#user_email",
    'pass_field':"#user_password",
    'post':'div[data-action="show-post"]',
    'post_images':'div[class="rounded-lg mb-3 image-container"] img',
    'post_vids':"//video[@controls='controls' and contains(@class, 'mb-3 rounded-lg black')]",
    'note':"//a[@data-action='show-post' and @data-collection='stories' and @data-type='story']",
    'community_post':"//a[contains(@href, 'community_posts')]",
    'note_images':'img[data-action="zoom-media"]',
    'date':'div[class="date-box"] div[class="text-h6 grey2--text text--darken-1 font-weight-regular"]',
    'main_menu_button':'a[data-action="open-menu"]',
    'child_menu_item':'a.sp-c-nav-drawer__link.accordion-toggle[data-toggle="menu"]',
    'child_name_label':'span.sp-c-nav-drawer__link-label',
}

children = {

}

creds = {
    'user':getenv('SP_USER'),
    'pass':getenv('SP_PASS')
}