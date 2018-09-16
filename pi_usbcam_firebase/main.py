#! /usr/bin/env python

import pygame
import pygame.camera
import datetime
import time

import firebase_admin
from firebase_admin import firestore, credentials, storage

DEVICE = '/dev/video0'
SIZE = (640, 480)
FILENAME = 'capture.png'

def start_firestore():
    cred = credentials.Certificate('prv_key.json')
    app = firebase_admin.initialize_app(cred, {
        "apiKey": "AIzaSyAFD4YJFxMlyEEfWnes7qd_leYlO807CaI",
        "databaseURL": "https://htn2018-ff451.firebaseio.com",
        "storageBucket": "htn2018-ff451.appspot.com",
        "authDomain": "htn2018-ff451.firebaseapp.com",
        "messagingSenderId": "500705094365",
        "projectId": "htn2018-ff451",
    })

    return firestore.client(app)

# Take a shot with the webcam
def take_shot():
    pygame.init()
    pygame.camera.init()
    camera = pygame.camera.Camera(DEVICE, SIZE)
    camera.start()

    # Stabilize the image
    for i in range(10):
        screen = camera.get_image()

    pygame.image.save(screen, FILENAME)

    camera.stop()
    pygame.quit()

    return screen

if __name__ == '__main__':
    fire_client = start_firestore()
    images_collection = fire_client.collection('images')
    images_bucket = storage.bucket()

    try:
        while True:
            img = take_shot()
            img_timestamp = datetime.datetime.now()
            filename = img_timestamp.strftime("%Y-%m-%d-%H-%M-%S.png")
            img_blob = images_bucket.blob(filename)

            with open(FILENAME, 'rb') as f:
                img_blob.upload_from_file(f)

            img_blob.make_public()

            images_collection.add({
                u"processed": False,
                u"timestamp": img_timestamp,
                u"uri": img_blob.media_link,
            })

            time.sleep(3)
    except KeyboardInterrupt:
        pass
