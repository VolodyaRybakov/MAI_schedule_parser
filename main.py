import os
from configparser import ConfigParser

import extract
import transform


def main():
    cfg = ConfigParser()
    cfg.read("globals.cfg", encoding='utf-8')
    middle_saving_csv = cfg.get("main", "middle_saving_csv")
    web_driver = cfg.get("main", "web_driver")

    tmp_path = os.path.dirname(os.path.abspath(middle_saving_csv))
    if not os.path.exists(tmp_path):
        os.makedirs(tmp_path)

    if not os.path.exists(os.path.dirname(os.path.abspath(web_driver))):
        print(f"ERROR: webdriver (web_driver) does not exists!")

    extract.run()
    transform.run()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
    else:
        print("Done")
