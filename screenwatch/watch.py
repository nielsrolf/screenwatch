import os
import time
import datetime as dt
import click

@click.command()
@click.argument('target_dir', default='.')
def main(target_dir):
    while True:
        t = str(dt.datetime.now())[:-7].replace(":", "-").replace(" ", "--")
        os.system(f"screencapture -D 1 {target_dir}/{t}-screen1.jpg")
        os.system(f"screencapture -D 2 {target_dir}/{t}-screen2.jpg")
        time.sleep(60)


if __name__ == "__main__":
    main()
