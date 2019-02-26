FROM ubuntu:18.10
ADD . /idcardocr
#ADD tessdata/. /usr/share/tesseract-ocr/tessdata
WORKDIR /idcardocr
RUN export DEBIAN_FRONTEND=noninteractive&&apt update&&apt install python3 python3-pip tesseract-ocr tesseract-ocr-chi-sim libsm6 libxext6 python3-tk -y
RUN pip3 install -r /idcardocr/requirements.txt
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo "Asia/Shanghai" > /etc/timezone
EXPOSE 8080
CMD PYTHONIOENCODING=utf-8 python3 -u /idcardocr/idcard_recognize.py
