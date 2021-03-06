#!/usr/bin/env python
# -*- coding:utf-8 -*-

# --------------------------------------------------------
# Tensorflow Faster R-CNN
# 检测视频里的物体
# --------------------------------------------------------

"""
Demo script showing detections in sample images.

See README.md for installation instructions before running.
"""


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import _init_paths
from model.config import cfg
from model.test import im_detect
from model.nms_wrapper import nms

from utils.timer import Timer
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
import os, cv2
import argparse

from nets.vgg16 import vgg16
from nets.resnet_v1 import resnetv1

CLASSES = ('__background__',
           'aeroplane', 'bicycle', 'bird', 'boat',
           'bottle', 'bus', 'car', 'cat', 'chair',
           'cow', 'diningtable', 'dog', 'horse',
           'motorbike', 'person', 'pottedplant',
           'sheep', 'sofa', 'train', 'tvmonitor')

NETS = {'vgg16': ('vgg16_faster_rcnn_iter_70000.ckpt',),'res101': ('res101_faster_rcnn_iter_110000.ckpt',)}
DATASETS= {'pascal_voc': ('voc_2007_trainval',),'pascal_voc_0712': ('voc_2007_trainval+voc_2012_trainval',)}

def vis_detections(class_name, dets, thresh=0.5):
    inds = np.where(dets[:, -1] >= thresh)[0]
    if len(inds) == 0:
        return
    retRightDect=[]
    for i in inds:
        bbox = dets[i, :4]
        score = dets[i, -1]
        dictScoreBox={'class':class_name,'box':bbox,'score':score}
        retRightDect.append(dictScoreBox)
    return retRightDect

#-----------------------------------------------------
# 函数名：im_Detect_Highscore
# 内容：返回image图片里面识别分数高于CONF_THRESH的classbox
# 输出：一个列表，列表元素为字典{'class','box','score'}
#-----------------------------------------------------
def im_Detect_Highscore(sess, net, image,CONF_THRESH = 0.8,NMS_THRESH = 0.3):
    """Detect object classes in an image using pre-computed object proposals."""
    im=image
    # Detect all object classes and regress object bounds
    timer = Timer()
    timer.tic()
    scores, boxes = im_detect(sess, net, im)
    timer.toc()
    #print('Detection took {:.3f}s for {:d} object proposals'.format(timer.total_time, boxes.shape[0]))
    #print('okokzzqtestgithub')

    # get a list of all high score classbox
    # if the classbox's score > CONF_THRESH, than this classbox will add the imageAllClass
    imageAllClass=[]
    for cls_ind, cls in enumerate(CLASSES[1:]):
        cls_ind += 1 # because we skipped background
        cls_boxes = boxes[:, 4*cls_ind:4*(cls_ind + 1)]
        cls_scores = scores[:, cls_ind]
        dets = np.hstack((cls_boxes,
                          cls_scores[:, np.newaxis])).astype(np.float32)
        keep = nms(dets, NMS_THRESH)
        dets = dets[keep, :]
        rightDect = vis_detections(cls, dets, thresh=CONF_THRESH)
        if rightDect is None:
            pass
        else:
            for iti in rightDect:
                imageAllClass.append(iti)

    return imageAllClass


#func
def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Tensorflow Faster R-CNN demo')
    parser.add_argument('--net', dest='demo_net', help='Network to use [vgg16 res101]',
                        choices=NETS.keys(), default='res101')
    parser.add_argument('--dataset', dest='dataset', help='Trained dataset [pascal_voc pascal_voc_0712]',
                        choices=DATASETS.keys(), default='pascal_voc_0712')
    args = parser.parse_args()

    return args


####### main #######

if __name__ == '__main__':
    cfg.TEST.HAS_RPN = True  # Use RPN for proposals
    args = parse_args()

    # model path
    demonet = args.demo_net
    dataset = args.dataset
    # zzq must add "os.getcwd()/.." in pycharm
    tfmodel = os.path.join(os.getcwd(),'..','output', demonet, DATASETS[dataset][0], 'default',
                              NETS[demonet][0])

    if not os.path.isfile(tfmodel + '.meta'):
        raise IOError(('{:s} not found.\nDid you download the proper networks from '
                       'our server and place them properly?').format(tfmodel + '.meta'))

    # set config
    tfconfig = tf.ConfigProto(allow_soft_placement=True)
    tfconfig.gpu_options.allow_growth=True

    # init session
    sess = tf.Session(config=tfconfig)
    # load network
    if demonet == 'vgg16':
        net = vgg16()
    elif demonet == 'res101':
        net = resnetv1(num_layers=101)
    else:
        raise NotImplementedError
    net.create_architecture("TEST", 21,
                          tag='default', anchor_scales=[8, 16, 32])
    saver = tf.train.Saver()
    saver.restore(sess, tfmodel)

    print('Loaded network {:s}'.format(tfmodel))


    #获得视频以及格式
    cap = cv2.VideoCapture('/home/kk/视频/ai4.avi')
    # 获得视频格式
    fps = cap.get(cv2.CAP_PROP_FPS)
    size = (
        int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    )
    print('视频FPS=', fps)
    print('视频分辨率=', size)

    # 定义视频输出
    vdOutSize=(1280,720)
    videoWriter = cv2.VideoWriter(
        "/home/kk/视频/output_ai4.avi",
        cv2.VideoWriter_fourcc("D", "I", "V", "X"),  # 编码器
        fps,
        vdOutSize
    )

    # 开始计算
    ret, frame = cap.read()
    i = 0
    while ret:
        # get the class,box and score in this image
        thresh_score = 0.8
        imgclassbox = im_Detect_Highscore(sess, net, frame, thresh_score)

        # show the image and the classes
        img=frame
        for i_classbox in imgclassbox:

            cv2.rectangle(img,
                          (i_classbox['box'][0], i_classbox['box'][1]),
                          (i_classbox['box'][2], i_classbox['box'][3]),
                          (0, 0, 255),
                          3)
            # 将文字框加入到图片中，(5,20)定义了文字框左顶点在窗口中的位置，最后参数定义文字颜色
            cv2.putText(img,i_classbox['class'],(i_classbox['box'][0], i_classbox['box'][1]),
                        cv2.FONT_HERSHEY_PLAIN,
                        2.0,
                        (0,255,0),
                        2
                        )
        img=cv2.resize(img,vdOutSize)
        cv2.imshow("out",img)
        cv2.waitKey(1)
        videoWriter.write(img)
        ret, frame = cap.read()
        i = i + 1
        if i % 30 == 0:
            print("已完成", i / 30, "s")
    print("视频转换完成")


