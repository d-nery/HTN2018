import time
import requests
import subprocess
import firebase_admin

from firebase_admin import firestore, credentials, storage

DENSEPOSE = '/home/sadi_neto/densepose'
IMAGE_PATH = DENSEPOSE + '/DensePoseData/image.jpg'

docker_cmd = "nvidia-docker run --rm -v "+DENSEPOSE+"/DensePoseData:/denseposedata -it densepose:c2-cuda9-cudnn7-wdata python2 tools/infer_simple.py --cfg configs/DensePose_ResNet101_FPN_s1x-e2e.yaml --output-dir DensePoseData/infer_out --image-ext jpg --wts DensePoseData/DensePose_ResNet101_FPN_s1x-e2e.pkl "

# Gets the firestone client
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

if __name__ == '__main__':
    fire_client = start_firestore()
    images_collection = fire_client.collection('images')
    images_bucket = storage.bucket()

    try:
        # Keep listening for new images until KeyboardInterrupt
        while True:
            try:
                # Get one new database record at a time
                for doc in images_collection.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1).get():
                    data = doc.to_dict()
                    if data['processed']:
                        continue

                    img_data = requests.get(data['uri']).content
                    with open(IMAGE_PATH, 'wb') as f:
                        f.write(img_data)

                    subprocess.run(docker_cmd + 'DensePoseData/image.jpg', shell=True)
                    img_blob = images_bucket.blob(data['uri'].split('/')[-1].split('.')[0] + '-proc.png')

                    with open(DENSEPOSE + '/DensePoseData/infer_out/image_IUV.png', 'rb') as f:
                        img_blob.upload_from_file(f)

                    img_blob.make_public()

                    images_collection.document(doc.id).update({
                        u'processed': True,
                        u'processed_uri': img_blob.media_link,
                    })

                # Don't disturb the server too much
                time.sleep(1)
            except AttributeError:
                continue
    except KeyboardInterrupt:
        pass
