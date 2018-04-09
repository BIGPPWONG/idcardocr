# -*- coding: utf-8 -*-
import numpy as np
import cv2, time
import idcardocr
from matplotlib import pyplot as plt

class findidcard:
    def __init__(self):
        pass

    #img1为身份证模板, img2为需要识别的图像
    def find(self, img1_name, img2_name):
        MIN_MATCH_COUNT = 10
        #idocr = idcardocr.idcardocr()
        img1 = cv2.UMat(cv2.imread(img1_name, 0)) # queryImage in Gray
        img1 = self.img_resize(img1, 640)
        #self.showimg(img1)
        #img1 = idocr.hist_equal(img1)
        img2 = cv2.UMat(cv2.imread(img2_name, 0))  # trainImage in Gray
        img2 = self.img_resize(img2, 1920)
        #img2 = idocr.hist_equal(img2)
        img_org = cv2.UMat(cv2.imread(img2_name))
        img_org = self.img_resize(img_org, 1920)
        #  Initiate SIFT detector
        t1 = round(time.time() * 1000)

        sift = cv2.xfeatures2d.SIFT_create()
        # find the keypoints and descriptors with SIFT
        kp1, des1 = sift.detectAndCompute(img1,None)
        kp2, des2 = sift.detectAndCompute(img2,None)

        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        search_params = dict(checks = 10)

        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(des1,des2,k=2)

        t2 = round(time.time()*1000)
        print 'time:%s'%(t2-t1)

        # store all the good matches as per Lowe's ratio test.
        #两个最佳匹配之间距离需要大于ratio 0.7,距离过于相似可能是噪声点
        good = []
        for m,n in matches:
            if m.distance < 0.7*n.distance:
                good.append(m)
        #reshape为(x,y)数组
        if len(good)>MIN_MATCH_COUNT:
            src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
            dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
            #用HomoGraphy计算图像与图像之间映射关系, M为转换矩阵
            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
            matchesMask = mask.ravel().tolist()
            #使用转换矩阵M计算出img1在img2的对应形状
            h,w = cv2.UMat.get(img1).shape
            pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
            dst = cv2.perspectiveTransform(pts,M)

            img2 = cv2.polylines(img2,[np.int32(dst)],True,255,3, cv2.LINE_AA)
            #self.showimg(img2)
            #进行图像矫正（透视变换）
            M_r, mask_r = cv2.findHomography(dst, pts, 0,5.0)
            im_r = cv2.warpPerspective(img_org, M_r, (w,h))
            #self.showimg(im_r)
        else:
            print "Not enough matches are found - %d/%d" % (len(good),MIN_MATCH_COUNT)
            matchesMask = None

        #draw_params = dict(matchColor = (0,255,0), # draw matches in green color
        #           singlePointColor = None,
        #           matchesMask = matchesMask, # draw only inliers
        #           flags = 2)
        #img3 = cv2.drawMatches(img1,kp1,img2,kp2,good,None,**draw_params)
        #plt.imshow(img3, 'gray'),plt.show()
        return im_r


    def showimg(self, img):
        cv2.namedWindow("contours", 0);
        #cv2.resizeWindow("contours", 1600, 1200);
        cv2.imshow("contours", img)
        cv2.waitKey()

    def img_resize(self, imggray, dwidth):
        # print 'dwidth:%s' % dwidth
        crop = imggray
        size = crop.get().shape
        height = size[0]
        width = size[1]
        height = height * dwidth / width
        crop = cv2.resize(src=crop, dsize=(dwidth, height), interpolation=cv2.INTER_CUBIC)
        return crop

if __name__=="__main__":
    idfind = findidcard()
    result = idfind.find('idcard_mask.jpg', '9.jpg')
    idfind.showimg(result)
