import os
from cvs import *
import aidlite_gpu
from utils import detect_postprocess, preprocess_img, draw_detect_res
import utils
import time
import cv2
import requests
from qiniu import Auth, put_file, BucketManager
from qiniu import CdnManager

# AidLite初始化：调用AidLite进行AI模型的加载与推理
aidlite = aidlite_gpu.aidlite()
model_path = 'best-fp16.tflite'

# 定义输入输出shape
in_shape = [1 * 640 * 640 * 3 * 4]
out_shape = [1 * 7 * 25200 * 4]

# 加载Aidlite检测模型：支持tflite, tnn, mnn, ms, nb格式的模型加载
aidlite.ANNModel(model_path, in_shape, out_shape, 4, 0)

# 配置七牛云存储相关信息
access_key = "Lri6FvWT-FHSDUfAdCKjC-5WBstieo2cfr4arbTg"
secret_key = "h0PC3H60IxD8ZdOk3TfV0b6a_J11tV5waoHRPr4O"
bucket_name = "wayhome1"
bucket_url = "si1tppa3l.hn-bkt.clouddn.com"
q = Auth(access_key, secret_key)
bucket = BucketManager(q)
cdn_manager = CdnManager(q)

# 将本地图片上传到七牛云中
def upload_img(bucket_name, file_name, file_path):
    # generate token
    token = q.upload_token(bucket_name, file_name, 3600)
    put_file(token, file_name, file_path)

# 生成上传云后返回file_name的图片外链
def get_img_url(bucket_url, file_name):
    img_url = 'http://%s/%s' % (bucket_url, file_name)
    return img_url

# 发送喵提醒消息
def send_alert(image_url):
    id = 'tLavDyT'  # 替换为你的喵提醒ID
    text = "检测结果：" + image_url
    ts = str(time.time())  # 时间戳
    type = 'json'  # 返回内容格式
    request_url = "http://miaotixing.com/trigger?"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.47'}

    result = requests.post(request_url + "id=" + id + "&text=" + text + "&ts=" + ts + "&type=" + type, headers=headers)
    print(result)

# 读取视频进行推理
cap = cvs.VideoCapture('10.mp4')#如果要使用摄像头则将括号内改为-1
frame_id = 0

while True:
    frame = cap.read()
    if frame is None:
        continue
    
    frame_id += 1
    if int(frame_id) % 2 == 0:
        continue
    
    # 预处理
    img = utils.preprocess_img(frame, target_shape=(640, 640), div_num=255, means=None, stds=None)

    # 数据转换
    aidlite.setInput_Float32(img)
    
    # 模型推理API
    aidlite.invoke()
    
    # 读取返回的结果
    pred = aidlite.getOutput_Float32(0)
    
    # 数据维度转换
    pred = pred.reshape(1, 25200, 7)[0]
   
    # 模型推理后处理
    pred = utils.detect_postprocess(pred, frame.shape, [640, 640, 3], conf_thres=0.85, iou_thres=0.45)
    
    # 绘制推理结果
    res_img = utils.draw_detect_res(frame, pred)
    
    # 如果检测到物体（即预测结果不为空）
    if any([len(p) > 0 for p in pred]):
        # 将推理结果保存为图片
        output_image_name = f"output_{frame_id}.jpg"
        cv2.imwrite(output_image_name, res_img)
        
        # 上传推理结果图片到七牛云
        upload_img(bucket_name, output_image_name, output_image_name)
        
        # 获取上传后图片的URL
        img_url = get_img_url(bucket_url, output_image_name)
        print(f"Image URL: {img_url}")

        #发送喵提醒
        send_alert(img_url)
        # 刷新CDN缓存
        urls = [img_url]
        refresh_url_result = cdn_manager.refresh_urls(urls)

        
        # 删除本地图片文件
        os.remove(output_image_name)
 

    # 显示推理结果
    cvs.imshow(res_img)  