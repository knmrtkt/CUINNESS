import os
import sys
import math
import csv
import pprint
import pandas as pd
import cv2
import glob
import numpy as np
import matplotlib.pyplot as plt
import datetime
from IPython.display import SVG

class gen_line_image():
    def __init__(self):
        pass
    def generate_point(self, W, H, r):
        if(0 <= r < W):
            x =  r
            y = 0
        elif(0 <= r< (W+H)):
            x = W
            y = r-W
        elif((W+H) <= r < (2*W+H)):
            x = (2*W+H)-r
            y = W
        elif((2*W+H) <= r < (2*W+2*H)):
            x = 0
            y = (2*W+2*H)-r
        else:
          print("Error")
        return x, y

    def get_domain_from_coord(self, W, H, r, domain_num_W, domain_num_H):
        if(0 <= r < W):
            domain = int(r/(W/domain_num_W))
        elif(0 <= r < (W + H)):
            domain = domain_num_W + int((r-W)/(W/domain_num_H))
        elif((W + H) <= r < (2*W + H)):
            domain = domain_num_W + domain_num_H + int((r-W-H)/(W/domain_num_W))
        else:
            domain = 2*domain_num_W + domain_num_H + int((r-2*W-H)/(H/domain_num_H))
        return domain

    def begin_or_end(self, a, b, domain_a, domain_b):
        if(a[1] <= b[1]):
              begin = a
              end = b
              domain_begin = domain_a
              domain_end = domain_b 
        else:
            begin = b
            end = a
            domain_begin = domain_b
            domain_end = domain_a 
        # print('begin=' + str(begin) + ', ' + 'end=' + str(end))
        # print('domain_begin=' + str(domain_begin) + ', ' + 'domain_end=' + str(domain_end))
        return begin, end, domain_begin, domain_end

    def get_label_from_domain(self, domain_begin, domain_end):
        if(domain_begin==0):
            # if(4<=domain_end<=8):
            if(domain_end==4):
              drawable = True
              # label = "left"
              label = "not1"
            elif(domain_end==3 or domain_end==9):
              # drawable = True
              drawable = False
              # label = "straight"
              label = "none"
            else:
              drawable = False
              label = "none"
              # print('invalid line')
        elif(domain_begin==1):
            # if(3<=domain_end<=9):
            if(domain_end==6):
              drawable = True
              label = "straight"
            else:
              drawable = False
              label = "none"
              # print('invalid line')
        elif(domain_begin==2):
            # if(4<=domain_end<=8):
            if(domain_end==8):
              drawable = True
              label = "not2"
            elif(domain_end==3 or domain_end==9):
              # drawable = True
              drawable = False
              # label = "straight"
              label = "none"
            else:
              drawable = False
              label = "none"
              # print('invalid line')
        elif(domain_begin==3):
            if(5<=domain_end<=8):
              # drawable = True
              drawable = False
              label = "right"
            else:
              drawable = False
              label = "none"
              # print('invalid line')
        elif(domain_begin==9):
            if(4<=domain_end<=7):
              # drawable = True
              drawable = False
              label = "left"
            else:
              drawable = False
              label = "none"
              # print('invalid line')
        else:
            drawable = False
            label = "none"
            # print('invalid line')
        # print(drawable, label)
        return drawable, label

    def generate_image(self, W, H, domain_num_W, domain_num_H, dst_dir, csv_name, img_num, line_width, class_label):
        # straight_num = img_num//3
        # left_num = img_num//3
        # right_num = img_num//3
        straight_num = img_num//3
        not1_num = img_num//3
        not2_num = img_num//3

        for dir_no in class_label.values():
          os.makedirs(dst_dir + dir_no, exist_ok=True)
        with open(dst_dir + csv_name, 'w') as f:
          writer = csv.writer(f)
          writer.writerow(['path','label'])
          # straight_generated = 0
          # left_generated = 0
          # right_generated = 0
          straight_generated = 0
          not1_generated = 0
          not2_generated = 0

          # while(straight_generated + left_generated + right_generated < img_num):
          while(straight_generated + not1_generated + not2_generated  < img_num):
            image = np.zeros((H,W,1), dtype=np.uint8)
            image.fill(255)
            color=0
            r_a = np.random.randint(0, 2*W + 2*H)
            r_b = np.random.randint(0, 2*W + 2*H)
            a = self.generate_point(W, H, r_a)
            b = self.generate_point(W, H, r_b,)
            domain_a = self.get_domain_from_coord(W, H, r_a, domain_num_W, domain_num_H)
            domain_b = self.get_domain_from_coord(W, H, r_b, domain_num_W, domain_num_H)
            begin, end, domain_begin, domain_end = self.begin_or_end(a, b, domain_a, domain_b)
            drawable, label = self.get_label_from_domain(domain_begin, domain_end) 

            if((label=="straight") and (straight_generated < straight_num)):
              cv2.line(image, begin, end ,color, line_width)
              cv2.imwrite(dst_dir + class_label[label] + "/" + str(straight_generated) + ".png", image)
              writer.writerow(['./'+dst_dir +class_label[label] + "/" + str(straight_generated) + ".png",class_label[label]])
              # print(straight_generated)
              straight_generated = straight_generated + 1
            
            elif((label=="not1") and (not1_generated < not1_num)):
              cv2.line(image, begin, end ,color, line_width)
              cv2.imwrite(dst_dir + class_label[label] + "/" + str(not1generated) + ".png", image)
              writer.writerow(['./'+dst_dir +class_label[label] + "/" + str(not1_generated) + ".png",class_label[label]])
              # print(notstraight_generated)
              not1_generated = not1_generated + 1

            elif((label=="not2") and (not2_generated < not2_num)):
              cv2.line(image, begin, end ,color, line_width)
              cv2.imwrite(dst_dir + class_label[label] + "/" + str(notstraight_generated) + ".png", image)
              writer.writerow(['./'+dst_dir +class_label[label] + "/" + str(not2_generated) + ".png",class_label[label]])
              # print(notstraight_generated)
              not2_generated = not2_generated + 1
            # elif((label=="left") and (left_generated < left_num)):
            #   cv2.line(image, begin, end ,color, line_width)
            #   cv2.imwrite(dst_dir + class_label[label] + "/" + str(left_generated) + ".png", image)
            #   writer.writerow(['./'+dst_dir +class_label[label] + "/" + str(left_generated) + ".png",class_label[label]])
            #   print(left_generated)
            #   left_generated = left_generated + 1
            # elif((label=="right") and (right_generated < right_num)):
            #   cv2.line(image, begin, end ,color, line_width)
            #   cv2.imwrite(dst_dir + class_label[label] + "/" + str(right_generated) + ".png", image)
            #   writer.writerow(['./'+dst_dir +class_label[label] + "/" + str(right_generated) + ".png",class_label[label]])
            #   print(right_generated)
            #   right_generated = right_generated + 1 
            # print("-------------------------")
