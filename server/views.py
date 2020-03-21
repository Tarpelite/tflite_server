from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
import os

import cv2
import numpy as np
from PIL import Image
import tensorflow as tf
import os
import matplotlib as mpl


mpl.use('Agg')
from matplotlib import pyplot as plt

abel_colours = [(128, 0, 0), (0, 128, 0), (0, 0, 128), (0, 0, 0)]
label_class = {'wire_opening': 0, 'nest': 1, 'grass': 2}

interpreter = tf.lite.Interpreter(model_path='model.tflite')

def decode(mask):
    img = Image.new('RGB', (128, 128))
    pixels = img.load()
    for j_, j in enumerate(mask[0, :, :, 0]):
        for k_, k in enumerate(j):
            pixels[k_, j_] = label_colours[k]
    outputs = np.array(img)
    return outputs
# Create your views here.

@api_view(["POST"])
def infer(request):
    if request.method == "POST":
        image = request.FILES['file']

        images = np.zeros((1, 1024,1024, 3))

        with Image.open(image) as img:
            im = img.convert("RGB")
            im = im.resize((1024, 1024))
        
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        interpreter.set_tensor(input_details[0]['index'], images)

        interpreter.invoke()

        cls_logit = interpreter.get_tensor(output_details[0]['index'])
        seg_logit = interpreter.get_tensor(output_details[1]['index'])

        pred_label = np.array(cls_logit[0, :])
        value = np.argmax(pred_label)

        # seg_result
        seg_pred_classes = np.expand_dims(np.argmax(seg_logit, axis=3), axis=3)
        decode_mask = decode(seg_pred_classes)
        result_name = list(label_class.keys())[list(label_class.values()).index(value)]
        filename = "{}.jpg".format(result_name)
        pred_mask = Image.fromarray(decode_mask)
        pred_mask = pred_mask.resize((img.size[0], img.size[1]))
        plt.rcParams['savefig.dpi'] = 300
        plt.title(result_name)
        plt.subplot(121)
        plt.axis('off')
        plt.imshow(img)
        plt.subplot(122)
        plt.axis('off')
        plt.imshow(pred_mask)
       
        plt.savefig(filename, bbox_inches='tight')
        plt.close()
        try:
        with open(filename, "rb") as f:
            return HttpResponse(f.read(), content_type="image/jpeg")
        except IOError:
            red = Image.new('RGBA', (1, 1), (255,0,0,0))
            response = HttpResponse(content_type="image/jpeg")
            red.save(response, "JPEG")
            return response
        



