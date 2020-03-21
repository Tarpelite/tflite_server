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
from .models import Score

label_colours = [(128, 0, 0), (0, 128, 0), (0, 0, 128), (0, 0, 0)]
label_class = {'wire_opening': 0, 'nest': 1, 'grass': 2}

interpreter = tf.lite.Interpreter(model_path='model.tflite')

tmp_image_path = "/var/www/tmp.jpg"

def decode(mask):
    img = Image.new('RGB', (128, 128))
    pixels = img.load()
    for j_, j in enumerate(mask[0, :, :, 0]):
        for k_, k in enumerate(j):
            pixels[k_, j_] = label_colours[k]
    outputs = np.array(img)
    return outputs
# Create your views here.

@api_view(["GET", "POST"])
def handle_image(request):
    if request.method == "GET":
        try:
            with open(tmp_image_path, "rb") as f:
                return HttpResponse(f.read(), content_type="image/jpeg")
        except IOError:
            red = Image.new('RGBA', (1, 1), (255,0,0,0))
            response = HttpResponse(content_type="image/jpeg")
            red.save(response, "JPEG")
            return response

    if request.method == "POST":
        image = request.FILES['file']
        with open("rb", image) as f_in:
            data = f_in.read()
        with open(tmp_image_path,"w+") as f:
            f.write(data)
        return Response({"result":"ok"}, status=status.HTTP_200_OK)

@api_view(["POST", "GET"])
def score(request):
    if request.method == "POST":
        local_state = {}
        local_state["wire_opening"] = request["wire_opening"]
        local_state["nest"] = request["nest"]
        local_state["grass"] = request["grass"]
        result = max(local_state)
        scores = Score.objects.all()
        if len(scores) == 0:
            score = Score(score1=str(local_state["wire_opening"]), score2=str(local_state["nest"]), score3=str(local_state["grass"]), result=result)
            score.save()
        else:
            score = scores[0]
            score.score1 = str(local_state["wire_opening"])
            score.score2 = str(local_state["nest"])
            score.score3 = str(local_state["grass"])
            score.result = result
            score.save()
        return Response({"result":"successfully update"}, status=status.HTTP_200_OK)

    if request.method == "GET":
        score = Score.objects.all()
        score = score[0]
        local_state = {}
        local_state["wire_opening"] = score.score1
        local_state["nest"] = score.score2
        local_state["grass"] = score.score3
        local_state["result"] = score.result
        return Response(local_state, status=status.HTTP_200_OK)

            

@api_view(["POST"])
def post_image(request):
    if request.method == "POST":
        image = request.FILES['file']
        with open("rb", image) as f_in:
            data = f_in.read()
        with open("w+", tmp_image_path) as f:
            f.write(data)
        
        return Response({"result":"ok"}, status=status.HTTP_200_OK)


@api_view(["POST"])
def infer_mask(request):
    if request.method == "POST":
        image = request.FILES['file']

        images = np.zeros((1, 1024,1024, 3), dtype=np.float32)
        interpreter.allocate_tensors()
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

@api_view(["POST"])
def infer_class(request):
    if request.method == "POST":
        image = request.FILES['file']

        images = np.zeros((1, 1024,1024, 3), dtype=np.float32)

        interpreter.allocate_tensors()

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
        
        result_name = list(label_class.keys())[list(label_class.values()).index(value)]
        filename = "{}.jpg".format(result_name)
        result = {}
        result["result"] = result_name
        
        return Response(result, status=status.HTTP_200_OK)
        



