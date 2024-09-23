import logging
import requests
import os
from utils import config
from utils import login
import traceback
import sys
from datetime import datetime
import shutil
import moviepy.video.io.ImageSequenceClip

def make_archive(source, destination, format='zip'):
    base, name = os.path.split(destination)
    archive_from = os.path.dirname(source)
    archive_to = os.path.basename(source.strip(os.sep))
    shutil.make_archive(name, format, archive_from, archive_to)
    shutil.move('%s.%s' % (name, format), destination)
    shutil.rmtree(source)

def create_video(source, destination, trans_id, logger):
    images_path = os.path.join(source, 'Frames')
    video_path = os.path.join(source, 'media.mp4')

    if os.path.exists(images_path):
        print("Creating Video of ",trans_id)
        images = [img for img in os.listdir(images_path) if img.endswith(".jpg")]
        images.sort(key=lambda x: int(x.split('.')[0]))
        frames = [os.path.join(images_path, image) for image in images]
        clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(frames, fps=10)
        clip.write_videofile(video_path, verbose=False, logger = None, bitrate = '2000k')
        os.system('rm -r {}'.format(images_path))
    
    if os.path.exists(video_path):
        print("Creating Archive of ",trans_id)
        os.makedirs(os.path.join(config.base_path, 'post_archive', trans_id), exist_ok= True)
        make_archive(source, destination)

def upload_video(trans_id, post_transid, logger):
    fileobj = open('post_archive/{}.zip'.format(trans_id), 'rb')
    logger.info("      Uploading Archive... {}".format(trans_id))

    base_url, machine_id, machine_token, machine_api_key = login.get_custom_machine_settings(config.vicki_app, logger)
    access_token = login.get_current_access_token(base_url, machine_id, machine_token, machine_api_key, logger)
    headers = {"Authorization": "Bearer {}".format(access_token)}
    print(headers)
    
    try:
        response_media = requests.post("{}/loyalty/upload-media/cv?media_event_type=COMPUTER_VISION&invoice_id={}".format(base_url, post_transid), files={'file': fileobj}, headers=headers)
        print(response_media.text)
    
        if response_media.status_code == 200:
            logger.info("      Uploading media-Success")
            os.system("rm -r post_archive/{}".format(trans_id))
            os.system("rm -r post_archive/{}.zip".format(trans_id))
            logger.info("      Cleaned Transaction")
        else:
            logger.info("      {}".format(response_media))
            logger.info("      Uploading media - FAILED")
            logger.info("      Archiving Transaction / For batch processing")
            logger.info("   Finished Current Transaction")
    except Exception as e:
        logger.info("      Uploading media-Failed")
        logger.info(traceback.format_exc())

def log_setup():
    logging.getLogger("pika").setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger("tensorflow").setLevel(logging.ERROR)

    log_folder = os.path.join(os.getcwd(), config.log_folder)
    os.makedirs(log_folder, exist_ok=True)
    log_path = os.path.join(log_folder, 'Upload-Module.log')

    if not os.path.exists(log_path):
        open(log_path, 'w').close()

    logging.basicConfig(filename=log_path, level=logging.DEBUG, format="%(asctime)-8s %(levelname)-8s %(message)s")
    logging.disable(logging.DEBUG)
    logger = logging.getLogger()
    logger.info("")
    sys.stderr.write = logger.error
    return logger

def main():
    logger = log_setup()
    current_hour = datetime.now().hour
    print(current_hour)
    if 0 <= current_hour < 5:
        archive_path = 'archive'
        post_archive_path = 'post_archive'
        if os.path.exists(archive_path):
            for trans_id in os.listdir(archive_path):
                create_video(os.path.join(archive_path, trans_id), 'post_archive/{}.zip'.format(trans_id), trans_id, logger)
        if os.path.exists(post_archive_path):
            for transid in os.listdir(post_archive_path):
                if '.zip' in transid:
                    trans_id = transid.split('.zip')[0]
                    if "____" in trans_id:
                        post_transid = trans_id.split("____")[0]
                    else:
                        post_transid = trans_id
                    upload_video(trans_id=trans_id, post_transid=post_transid, logger=logger)
        else:
            logger.info("No Failed Transaction found")
    else:
        logger.info("Script runs only between 12 AM and 5 AM")

if __name__ == "__main__":
    main()

