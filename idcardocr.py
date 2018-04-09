# -*- coding: utf-8 -*-
from PIL import Image
import pytesseract
import cv2
import numpy as np
import re
from multiprocessing import Pool, Queue, Lock, Process, freeze_support
import time

#pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'
x = 1280.00 / 3840.00
pixel_x = int(x * 3840)
print x, pixel_x

def idcardocr(imgname):
        # generate_mask(x)
        img_data_gray, img_org = img_resize_gray(imgname)
        result_dict = dict()
        name_pic = find_name(img_data_gray, img_org)
        #showimg(name_pic)
        # print 'name'
        result_dict['name'] = get_name(name_pic)
        # print result_dict['name']

        sex_pic = find_sex(img_data_gray, img_org)
        #showimg(sex_pic)
        # print 'sex'
        result_dict['sex'] = get_sex(sex_pic)
        # print result_dict['sex']

        nation_pic = find_nation(img_data_gray, img_org)
        #showimg(nation_pic)
        # print 'nation'
        result_dict['nation'] = get_nation(nation_pic)
        # print result_dict['nation']

        year_pic, month_pic, day_pic = find_birth(img_data_gray, img_org)
        #showimg(birth_pic)
        # print 'birth'
        year, month, day = get_birth(year_pic, month_pic, day_pic)
        #print year,month,day
        result_dict['birth'] = "%s年%s月%s日"%(year.encode('utf8'), month.encode('utf8'), day.encode('utf8'))
        # print result_dict['birth']


        address_pic = find_address(img_data_gray, img_org)
        #showimg(address_pic)
        # print 'address'
        result_dict['address'] = get_address(address_pic)
        # print result_dict['address']

        idnum_pic = find_idnum(img_data_gray, img_org)
        #showimg(idnum_pic)
        # print 'idnum'
        result_dict['idnum'] = get_idnum(idnum_pic)
        # print result_dict['idnum']

        #showimg(img_data_gray)
        return result_dict

def generate_mask(x):
        name_mask_pic = cv2.UMat(cv2.imread('name_mask.jpg'))
        sex_mask_pic = cv2.UMat(cv2.imread('sex_mask.jpg'))
        nation_mask_pic = cv2.UMat(cv2.imread('nation_mask.jpg'))
        birth_mask_pic = cv2.UMat(cv2.imread('birth_mask.jpg'))
        year_mask_pic = cv2.UMat(cv2.imread('year_mask.jpg'))
        month_mask_pic = cv2.UMat(cv2.imread('month_mask.jpg'))
        day_mask_pic = cv2.UMat(cv2.imread('day_mask.jpg'))
        address_mask_pic = cv2.UMat(cv2.imread('address_mask.jpg'))
        idnum_mask_pic = cv2.UMat(cv2.imread('idnum_mask.jpg'))
        name_mask_pic = img_resize_x(name_mask_pic)
        sex_mask_pic = img_resize_x(sex_mask_pic)
        nation_mask_pic = img_resize_x(nation_mask_pic)
        birth_mask_pic = img_resize_x(birth_mask_pic)
        year_mask_pic = img_resize_x(year_mask_pic)
        month_mask_pic = img_resize_x(month_mask_pic)
        day_mask_pic = img_resize_x(day_mask_pic)
        address_mask_pic = img_resize_x(address_mask_pic)
        idnum_mask_pic = img_resize_x(idnum_mask_pic)
        cv2.imwrite('name_mask_%s.jpg'%pixel_x, name_mask_pic)
        cv2.imwrite('sex_mask_%s.jpg' %pixel_x, sex_mask_pic)
        cv2.imwrite('nation_mask_%s.jpg' %pixel_x, nation_mask_pic)
        cv2.imwrite('birth_mask_%s.jpg' %pixel_x, birth_mask_pic)
        cv2.imwrite('year_mask_%s.jpg' % pixel_x, year_mask_pic)
        cv2.imwrite('month_mask_%s.jpg' % pixel_x, month_mask_pic)
        cv2.imwrite('day_mask_%s.jpg' % pixel_x, day_mask_pic)
        cv2.imwrite('address_mask_%s.jpg' %pixel_x, address_mask_pic)
        cv2.imwrite('idnum_mask_%s.jpg' %pixel_x, idnum_mask_pic)

#用于生成模板
def img_resize_x(imggray):
        # print 'dheight:%s' % dheight
        crop = imggray
        size = crop.get().shape
        dheight = int(size[0]*x)
        dwidth = int(size[1]*x)
        crop = cv2.resize(src=crop, dsize=(dwidth, dheight), interpolation=cv2.INTER_CUBIC)
        return crop

#idcardocr里面resize以高度为依据, 用于get部分
def img_resize(imggray, dheight):
        # print 'dheight:%s' % dheight
        crop = imggray
        size = crop.get().shape
        height = size[0]
        width = size[1]
        width = width * dheight / height
        crop = cv2.resize(src=crop, dsize=(width, dheight), interpolation=cv2.INTER_CUBIC)
        return crop

def img_resize_gray(imgorg):
        
        #imgorg = cv2.imread(imgname)
        crop = imgorg
        size = cv2.UMat.get(crop).shape
        # print size
        height = size[0]
        width = size[1]
        # 参数是根据3840调的
        height = int(height * 3840 * x / width)
        # print height
        crop = cv2.resize(src=crop, dsize=(int(3840 * x), height), interpolation=cv2.INTER_CUBIC)
        return hist_equal(cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)), crop

def find_name(crop_gray, crop_org):
        template = cv2.UMat(cv2.imread('name_mask_%s.jpg'%pixel_x, 0))
        # showimg(crop_org)
        w, h = cv2.UMat.get(template).shape[::-1]
        res = cv2.matchTemplate(crop_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        print max_loc
        top_left = (max_loc[0] + w, max_loc[1] - int(20*x))
        bottom_right = (top_left[0] + int(700*x), top_left[1] + int(300*x))
        result = cv2.UMat.get(crop_org)[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        cv2.rectangle(crop_gray, top_left, bottom_right, 255, 2)
        # showimg(result)
        return cv2.UMat(result)

def find_sex(crop_gray, crop_org):
        template = cv2.UMat(cv2.imread('sex_mask_%s.jpg'%pixel_x, 0))
        # showimg(template)
        w, h = cv2.UMat.get(template).shape[::-1]
        res = cv2.matchTemplate(crop_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        top_left = (max_loc[0] + w, max_loc[1] - int(20*x))
        bottom_right = (top_left[0] + int(300*x), top_left[1] + int(300*x))
        result = cv2.UMat.get(crop_org)[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        cv2.rectangle(crop_gray, top_left, bottom_right, 255, 2)
        #showimg(crop_gray)
        return cv2.UMat(result)

def find_nation(crop_gray, crop_org):
        template = cv2.UMat(cv2.imread('nation_mask_%s.jpg'%pixel_x, 0))
        #showimg(template)
        w, h = cv2.UMat.get(template).shape[::-1]
        res = cv2.matchTemplate(crop_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        top_left = (max_loc[0] + w - int(20*x), max_loc[1] - int(20*x))
        bottom_right = (top_left[0] + int(500*x), top_left[1] + int(300*x))
        result = cv2.UMat.get(crop_org)[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        cv2.rectangle(crop_gray, top_left, bottom_right, 255, 2)
        #showimg(crop_gray)
        return cv2.UMat(result)

def find_birth(crop_gray, crop_org):
        template = cv2.UMat(cv2.imread('birth_mask_%s.jpg'%pixel_x, 0))
        # showimg(template)
        w, h = cv2.UMat.get(template).shape[::-1]
        res = cv2.matchTemplate(crop_gray, template, cv2.TM_CCOEFF_NORMED)
        #showimg(crop_gray)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        top_left = (max_loc[0] + w, max_loc[1] - int(20*x))
        bottom_right = (top_left[0] + int(1500*x), top_left[1] + int(300*x))
        # 提取result需要在rectangle之前
        date_org = cv2.UMat.get(crop_org)[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        date = cv2.cvtColor(date_org, cv2.COLOR_BGR2GRAY)
        cv2.rectangle(crop_gray, top_left, bottom_right, 255, 2)
        # cv2.imwrite('date.png',date)

        # 提取年份
        template = cv2.UMat(cv2.imread('year_mask_%s.jpg'%pixel_x, 0))
        year_res = cv2.matchTemplate(date, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(year_res)
        bottom_right = (max_loc[0]+int(20*x), int(300*x))
        top_left = (0, 0)
        year = date_org[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        # cv2.imwrite('year.png',year)
        cv2.rectangle(crop_gray, top_left, bottom_right, 255, 2)

        # 提取月
        template = cv2.UMat(cv2.imread('month_mask_%s.jpg'%pixel_x, 0))
        month_res = cv2.matchTemplate(date, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(month_res)
        bottom_right = (max_loc[0]+int(40*x), int(300*x))
        top_left = (max_loc[0] - int(220*x), 0)
        month = date_org[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        # cv2.imwrite('month.png',month)
        cv2.rectangle(crop_gray, top_left, bottom_right, 255, 2)

        # 提取日
        template = cv2.UMat(cv2.imread('day_mask_%s.jpg'%pixel_x, 0))
        day_res = cv2.matchTemplate(date, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(day_res)
        bottom_right = (max_loc[0]+int(20*x), int(300*x))
        top_left = (max_loc[0] - int(220*x), 0)
        day = date_org[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        # cv2.imwrite('day.png',day)
        cv2.rectangle(crop_gray, top_left, bottom_right, 255, 2)
        #showimg(crop_gray)
        return cv2.UMat(year), cv2.UMat(month), cv2.UMat(day)

def find_address(crop_gray, crop_org):
        template = cv2.UMat(cv2.imread('address_mask_%s.jpg'%pixel_x, 0))
        # showimg(template)
        #showimg(crop_gray)
        w, h = cv2.UMat.get(template).shape[::-1]
        #t1 = round(time.time()*1000)
        res = cv2.matchTemplate(crop_gray, template, cv2.TM_CCOEFF_NORMED)
        #t2 = round(time.time()*1000)
        #print 'time:%s'%(t2-t1)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        top_left = (max_loc[0] + w, max_loc[1] - int(20*x))
        bottom_right = (top_left[0] + int(1700*x), top_left[1] + int(550*x))
        result = cv2.UMat.get(crop_org)[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        cv2.rectangle(crop_gray, top_left, bottom_right, 255, 2)
        #showimg(crop_gray)
        return cv2.UMat(result)

def find_idnum(crop_gray, crop_org):
        template = cv2.UMat(cv2.imread('idnum_mask_%s.jpg'%pixel_x, 0))
        # showimg(template)
        #showimg(crop_gray)
        w, h = cv2.UMat.get(template).shape[::-1]
        res = cv2.matchTemplate(crop_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        top_left = (max_loc[0] + w, max_loc[1] - int(20*x))
        bottom_right = (top_left[0] + int(2300*x), top_left[1] + int(300*x))
        result = cv2.UMat.get(crop_org)[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        cv2.rectangle(crop_gray, top_left, bottom_right, 255, 2)
        #showimg(crop_gray)
        return cv2.UMat(result)


def showimg(img):
        cv2.namedWindow("contours", 0);
        cv2.resizeWindow("contours", 1280, 720);
        cv2.imshow("contours", img)
        cv2.waitKey()

#psm model:
#  0    Orientation and script detection (OSD) only.
#  1    Automatic page segmentation with OSD.
#  2    Automatic page segmentation, but no OSD, or OCR.
#  3    Fully automatic page segmentation, but no OSD. (Default)
#  4    Assume a single column of text of variable sizes.
#  5    Assume a single uniform block of vertically aligned text.
#  6    Assume a single uniform block of text.
#  7    Treat the image as a single text line.
#  8    Treat the image as a single word.
#  9    Treat the image as a single word in a circle.
#  10    Treat the image as a single character.
#  11    Sparse text. Find as much text as possible in no particular order.
#  12    Sparse text with OSD.
#  13    Raw line. Treat the image as a single text line,
# 			bypassing hacks that are Tesseract-specific

def get_name(img):
        #    cv2.imshow("method3", img)
        #    cv2.waitKey()
        _, _, red = cv2.split(img) #split 会自动将UMat转换回Mat
        red = cv2.UMat(red)
        red = hist_equal(red)
        red = cv2.adaptiveThreshold(red, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 151, 50)
        #    red = cv2.medianBlur(red, 3)
        red = img_resize(red, 150)
        # cv2.imwrite('name.png', red)
        #    img2 = Image.open('address.png')
        img = Image.fromarray(cv2.UMat.get(red).astype('uint8'))
        return punc_filter(pytesseract.image_to_string(img, lang='chi_sim', config='-psm 13').replace(" ",""))

def get_sex(img):
        _, _, red = cv2.split(img)
        red = cv2.UMat(red)
        red = hist_equal(red)
        red = cv2.adaptiveThreshold(red, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 151, 50)
        #    red = cv2.medianBlur(red, 3)
        #    cv2.imwrite('address.png', img)
        #    img2 = Image.open('address.png')
        red = img_resize(red, 150)
        # cv2.imwrite('sex.png', red)
        img = Image.fromarray(cv2.UMat.get(red).astype('uint8'))
        #return pytesseract.image_to_string(img, lang='sex', config='interactive -c tessedit_char_whitelist=男女 -psm 8')
        return pytesseract.image_to_string(img, lang='sex', config='-psm 10').replace(" ","")

def get_nation(img):
        _, _, red = cv2.split(img)
        red = cv2.UMat(red)
        red = hist_equal(red)
        red = cv2.adaptiveThreshold(red, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 151, 50)
        red = img_resize(red, 150)
        # cv2.imwrite('nation.png', red)
        img = Image.fromarray(cv2.UMat.get(red).astype('uint8'))
        return pytesseract.image_to_string(img, lang='nation', config='-psm 13').replace(" ","")

def get_birth(year, month, day):
        _, _, red = cv2.split(year)
        red = cv2.UMat(red)
        red = hist_equal(red)
        red = cv2.adaptiveThreshold(red, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 151, 50)
        red = img_resize(red, 150)
        # cv2.imwrite('year_red.png', red)
        year_red = Image.fromarray(cv2.UMat.get(red).astype('uint8'))

        _, _, red = cv2.split(month)
        red = cv2.UMat(red)
        red = hist_equal(red)
        red = cv2.adaptiveThreshold(red, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 151, 50)
        #red = cv2.erode(red,kernel,iterations = 1)
        red = img_resize(red, 150)
        # cv2.imwrite('month_red.png', red)
        month_red = Image.fromarray(cv2.UMat.get(red).astype('uint8'))

        _, _, red = cv2.split(day)
        red = cv2.UMat(red)
        red = hist_equal(red)
        red = cv2.adaptiveThreshold(red, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 151, 50)
        red = img_resize(red, 150)
        # cv2.imwrite('day_red.png', red)
        day_red = Image.fromarray(cv2.UMat.get(red).astype('uint8'))
        # return pytesseract.image_to_string(img, lang='birth', config='-psm 7')
        return pytesseract.image_to_string(year_red, lang='eng', config='-c tessedit_char_whitelist=0123456789 -psm 13').replace(" ",""), \
               pytesseract.image_to_string(month_red, lang='eng', config='-c tessedit_char_whitelist=0123456789 -psm 13').replace(" ",""), \
               pytesseract.image_to_string(day_red, lang='eng', config='-c tessedit_char_whitelist=0123456789 -psm 13').replace(" ","")


def get_address(img):
        #_, _, red = cv2.split(img)
        #red = cv2.medianBlur(red, 3)
        _, _, red = cv2.split(img)
        red = cv2.UMat(red)
        red = hist_equal(red)
        red = cv2.adaptiveThreshold(red, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 151, 50)
        red = img_resize(red, 300)
        # cv2.imwrite('address_red.png', red)
        img = Image.fromarray(cv2.UMat.get(red).astype('uint8'))
        return punc_filter(pytesseract.image_to_string(img, lang='chi_sim', config='-psm 3').replace(" ",""))

def get_idnum(img):
        #    cv2.imshow("method3", img)
        #    cv2.waitKey()
        _, _, red = cv2.split(img)
        red = cv2.UMat(red)
        red = hist_equal(red)
        red = cv2.adaptiveThreshold(red, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 151, 50)
        red = img_resize(red, 150)
        # cv2.imwrite('idnum_red.png', red)
        img = Image.fromarray(cv2.UMat.get(red).astype('uint8'))
        return pytesseract.image_to_string(img, lang='idnum', config='-psm 13').replace(" ","")

def punc_filter(str):
        temp = str
        xx      =   u"([\u4e00-\u9fff0-9]+)"
        pattern =   re.compile(xx)
        results =   pattern.findall(temp)
        string = ""
        for result in results:
            string += result
        return string

#这里使用直方图拉伸，不是直方图均衡
def hist_equal(img):
        # clahe_size = 8
        # clahe = cv2.createCLAHE(clipLimit=1.0, tileGridSize=(clahe_size, clahe_size))
        # result = clahe.apply(img)
        #test

        #result = cv2.equalizeHist(img)

        image = img.get() #UMat to Mat
        # result = cv2.equalizeHist(image)
        lut = np.zeros(256, dtype = image.dtype )#创建空的查找表
        #lut = np.zeros(256)
        hist= cv2.calcHist([image], #计算图像的直方图
                            [0], #使用的通道
                            None, #没有使用mask
                           [256], #it is a 1D histogram
                           [0,256])
        minBinNo, maxBinNo = 0, 255
        #计算从左起第一个不为0的直方图柱的位置
        for binNo, binValue in enumerate(hist):
            if binValue != 0:
                minBinNo = binNo
                break
        #计算从右起第一个不为0的直方图柱的位置
        for binNo, binValue in enumerate(reversed(hist)):
            if binValue != 0:
                maxBinNo = 255-binNo
                break
        #print minBinNo, maxBinNo
        #生成查找表
        for i,v in enumerate(lut):
            if i < minBinNo:
                lut[i] = 0
            elif i > maxBinNo:
                lut[i] = 255
            else:
                lut[i] = int(255.0*(i-minBinNo)/(maxBinNo-minBinNo)+0.5)
        #计算,调用OpenCV cv2.LUT函数,参数 image --  输入图像，lut -- 查找表
        #print lut
        result = cv2.LUT(image, lut)
        #print type(result)
        #showimg(result)
        return cv2.UMat(result)

if __name__=="__main__":
    idocr = idcardocr()
    idocr.idcardocr(cv2.imread('9.jpg'))
