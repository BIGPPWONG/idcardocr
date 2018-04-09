FROM ubuntu:16.04
ADD . /idcardocr
ADD tessdata/. /usr/share/tesseract-ocr/tessdata
WORKDIR /idcardocr
RUN apt update&&apt install python python-pip tesseract-ocr tesseract-ocr-chi-sim tzdata libsm6 libxext6 python-tk -y
RUN pip install Pillow==5.0.0 numpy==1.14.1 opencv-contrib-python==3.4.0.12 pytesseract==0.2.0 matplotlib==2.1.2
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo "Asia/Shanghai" > /etc/timezone
EXPOSE 8080
CMD python /idcardocr/idcard_recognize.py
