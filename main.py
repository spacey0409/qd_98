import random
import re
from time import sleep
from playwright.sync_api import sync_playwright
import yaml
from apscheduler.schedulers.blocking import BlockingScheduler

import utils


class SehuatangJob:

    def __init__(self):
        self.url = "https://www.sehuatang.net/"
        # 浏览器设置
        self.isHeadless = True  # 是否无头模式

        self.mod_url = (
            "https://www.sehuatang.net/forum.php?mod=forumdisplay&fid=103"
        )

        self.sign_in_url = (
            "https://www.sehuatang.net/plugin.php?id=dd_sign"
        )

        self.view_url = (
            "https://www.sehuatang.net/forum.php?mod=viewthread&tid="
        )



    # 随机等待时间
    def random_sleep(self):
        """
        随机等待时间
        """
        sleep_time = round(random.uniform(2, 4), 2)
        sleep(sleep_time)

    def start(self):
        with sync_playwright() as p:
            self.browser = p.chromium.launch(headless=self.isHeadless, proxy={"server": self.proxy})
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
            self.get_page()
            self.page.close()
            self.context.close()
            self.browser.close()


    def get_page(self):
        try:
            self.page.goto(self.mod_url)
            self.random_sleep()

            # 确认
            utils.logger.info('---正在确认---')
            self.confirm()

            # 登录
            utils.logger.info('---正在登录---')
            self.login()

            # 签到
            utils.logger.info('---正在签到---')
            dd_sign_str = self.sign_in()

            if '今日已签到' in str(dd_sign_str):
                return
            if ('请至少发表或回复一个帖子后再来签到' == str(dd_sign_str)):
                self.page.goto(self.mod_url)
                sleep(2)
                # 回复帖子
                utils.logger.info('---正在回复帖子---')
                self.do_reply()
                # 签到
                utils.logger.info('---正在签到---')
                dd_sign_str = self.sign_in()
        except Exception as e:
            utils.logger.info(e)

    def read_config(self, file_path):
        utils.logger.info('---正在启动---')
        with open(file_path, "r") as f:
            config = yaml.safe_load(f)
            self.proxy = config['proxy']
            self.username = config['username']
            self.password = config['password']
            self.cron_hour = config['cron_hour']
            self.cron_minute = config['cron_minute']
            self.comments = config['comments']

    def do_reply(self):
        with self.context.expect_page() as view_page:
            self.page.click('//*[@id="threadlisttableid"]/tbody[11]/tr/td[1]')
        new_page = view_page.value
        self.page.wait_for_load_state()
        new_page.click('//*[@id="post_reply"]')
        message_input = new_page.locator('//*[@id="postmessage"]')
        randint = random.randint(0, len(self.comments) - 1)
        comment = self.comments[randint]
        utils.logger.info(f'---回复内容:[ {comment} ]---')
        message_input.fill(comment)
        new_page.click('//*[@id="postsubmit"]')

    def sign_in(self):
        self.page.goto(self.sign_in_url)
        button_str = self.page.query_selector('//*[@id="wp"]/div[2]/div[1]/div[1]').text_content()
        if '今日已签到' in str(button_str):
            utils.logger.info('---今日已签到---')
            return '今日已签到'
        self.page.click('//*[@id="wp"]/div[2]/div[1]/div[1]')
        self.random_sleep()
        # 获取签到updatesecqaa_id
        textboxValue = self.page.locator('//*[@id="fwin_content_pc_click_ddsign"]').all_text_contents()
        self.random_sleep()
        # 计算结果
        match = re.search(r"updatesecqaa\('([A-Za-z0-9]+)", str(textboxValue[0]))
        updatesecqaa_id = match.group(0).replace('updatesecqaa(\'', '')
        calc_str = self.page.locator(
            '//*[@id="secqaa_' + updatesecqaa_id + '"]/div/table/tbody/tr/td').inner_text()
        calc_str = calc_str.replace('换一个\n', '').replace('= ?', '')
        calc_result = eval(calc_str)
        calc_result_input = self.page.locator('//*[@id="secqaaverify_' + updatesecqaa_id + '"]')
        calc_result_input.fill(str(calc_result))
        self.page.click('//button[contains(@class,"pn")]')
        # 判断是否回复过帖子
        dd_sign_str = self.page.locator('//*[@id="ntcwin"]/table/tbody/tr/td[2]/div/i').inner_text()
        return dd_sign_str

    def confirm(self):
        self.page.get_by_text('满18岁，请点此进入').click()
        self.random_sleep()

    def login(self):
        username_input = self.page.locator('//*[@id="ls_username"]')
        password_input = self.page.locator('//*[@id="ls_password"]')
        username_input.fill(self.username)
        password_input.fill(self.password)
        self.page.click('//*[@id="lsform"]/div/div/table/tbody/tr[2]/td[3]/button')
        self.random_sleep()

    def my_job(self):
        self.start()



if __name__ == "__main__":
    sched = BlockingScheduler()
    play = SehuatangJob()
    play.read_config("conf.yaml")
    sched.add_job(play.my_job, 'cron', hour=play.cron_hour, minute=play.cron_minute)

    sched.start()
