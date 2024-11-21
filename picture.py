from qiniu import Auth, put_file
from qiniu import BucketManager

# 配置七牛云存储相关信息
access_key = "Lri6FvWT-FHSDUfAdCKjC-5WBstieo2cfr4arbTg"
secret_key = "h0PC3H60IxD8ZdOk3TfV0b6a_J11tV5waoHRPr4O"
bucket_name = "wayhome1"
bucket_url = "si1tppa3l.hn-bkt.clouddn.com"
q = Auth(access_key, secret_key)
bucket = BucketManager(q)

# 将本地图片上传到七牛云中
def upload_img(bucket_name, file_name, file_path):
    # generate token
    token = q.upload_token(bucket_name, file_name, 3600)
    put_file(token, file_name, file_path)

# 生成上传云后返回file_name的图片外链
def get_img_url(bucket_url, file_name):
    img_url = 'http://%s/%s' % (bucket_url, file_name)
    return img_url

# 需要上传到七牛云上的图片的路径
image_up_name = "data/images/girl.jpg"
# 上传到七牛云后，云存储的文件名
image_qiniu_name = "girl_2022.jpg"
# 将本地图片上传到七牛云，云存储的文件名为image_qiniu_name
upload_img(bucket_name, image_qiniu_name, image_up_name)
# 获取云端image_qiniu_name上传后图片的url
url_receive = get_img_url(bucket_url, image_qiniu_name)
print(url_receive)
