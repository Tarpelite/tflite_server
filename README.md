# tflite_server

## Introduction

This repo is for the deployment of MobileNet on Android platform.

## PLAN A

To use docker to deploy, follow these steps:

1. install linux deploy on your android system.
2. install docker.io
3. run the following code
    ```
    docker run -it tarpeite/tflite:ubuntu # the image size is about 3.35GB
    cd ~
    git clone https://github.com/Tarpelite/tflite_server.git
    cd tflite_server/server
    pip install [whaterver you miss] 
    ```
4. download the tflite model and remember its path 
5. modify tflite/server/views.py, change the existing code to
   ```py
      interpreter = tf.lite.Interpreter(model_path='ABSOLUTE_PATH OF YOUR MODEL')
   ```
6. save views.py, cd tflite_server/server
   ```
   python manage.py runserver 0.0.0.0:5000
   ```
7. then the you can call apis on your localhost:5000, for cURL example:
   ```
   curl --location --request POST 'localhost:5000/infer_class/' --form 'file=@nest10.jpg'
   ```
   the server will return infer results like
   ```json
   {"result":"nest"}
   ```

## PLAN B

To run model on android and use pc web browser as client, YOU NEED:

1. minmum Android SDK 26
2. deploy server to your pc as in PLAN A

The following steps:

1. use Android studio to compile android_deploy to .apk and install on your platform, remember to change the ip address in android_deploy/src/main/MainActivity.java 
2. use NPM to complie the client folder into react html, for development, start your npm sever locally.

### client Usage

1. open your complied html and upload an image.
2. start your app on android, click on analyze, this will task seconds to do inference.
3. refresh your web browser.
