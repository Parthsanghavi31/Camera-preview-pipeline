import threading
import time
import requests
import os
import cv2
from utils import config
import shutil
from utils import login
import sys
import traceback
import moviepy.video.io.ImageSequenceClip


def make_archive(source, destination, format='zip'):
    base, name = os.path.split(destination)
    archive_from = os.path.dirname(source)
    archive_to = os.path.basename(source.strip(os.sep))
    shutil.make_archive(name, format, archive_from, archive_to)
    shutil.move('%s.%s' % (name, format), destination)
    shutil.rmtree(source)

def upload_video(logger, trans_id, post_transid, images_path, video_path, customer_trans):
    if not os.path.exists(images_path):
        logger.info("      No DoorOpened Message")
        return 0
    images = [img for img in os.listdir(images_path) if img.endswith(".jpg")]
    images.sort(key=lambda x: int(x.split('.')[0]))
    frames = [os.path.join(images_path, image) for image in images]
    # self.logger.info("Total Frames Before "+str(len(frames)))
    # frames = self.reduce_frames(frames)
    # self.info("Total Frames After "+str(len(frames)))
    clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(frames, fps=10)
    clip.write_videofile(video_path, verbose=False, logger = None, bitrate = '2000k')

            
    logger.info("	Video created: {} frames".format(len(images)))
    
    os.makedirs(os.path.join(config.base_path, 'post_archive', trans_id), exist_ok= True)
    frames_path = '{}archive/{}/Frames'.format(config.base_path, trans_id)

    if os.path.exists(frames_path):os.system('rm -r {}'.format(frames_path))
    
    make_archive('archive/{}'.format(trans_id), 'post_archive/{}.zip'.format(post_transid))
    
    fileobj = open('post_archive/{}.zip'.format(post_transid), 'rb')
    logger.info("      Uploading Archive...")

    base_url, machine_id, machine_token, machine_api_key = login.get_custom_machine_settings(config.vicki_app, logger)
    access_token = login.get_current_access_token(base_url, machine_id, machine_token, machine_api_key, logger)
    headers = {"Authorization": "Bearer {}".format(access_token)}
    
    try:
        if customer_trans == 'False':
            url = "{}/loyalty/upload-media/cv?media_event_type=TECHNICIAN_MODE&invoice_id={}".format(base_url,post_transid)
        else: 
            url = "{}/loyalty/upload-media/cv?media_event_type=COMPUTER_VISION&invoice_id={}".format(base_url,post_transid)
        response_media = requests.post(url, files = {'file':fileobj}, headers=headers)
        print(response_media.text)
    
        if response_media.status_code == 200:
            logger.info("      Uploading media-Success")
            os.system("rm -r post_archive/{}".format(post_transid))
            os.system("rm -r post_archive/{}.zip".format(post_transid))
            logger.info("      Cleaned Transaction")
        else:
            logger.info("      {}".format(response_media))
            logger.info("      Uploading media - FAILED")
            logger.info("      Archiving Transaction / For batch processing")
            logger.info("   Finished Current Transaction")
    except Exception as e:
        logger.info("      Uploading media-Failed")
        logger.info(response_media.json())
        logger.info(traceback.format_exc())      