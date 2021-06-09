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
        print('begin=' + str(begin) + ', ' + 'end=' + str(end))
        print('domain_begin=' + str(domain_begin) + ', ' + 'domain_end=' + str(domain_end))
        return begin, end, domain_begin, domain_end

    def get_label_from_domain(self, domain_begin, domain_end):
        if(domain_begin==0):
            if(4<=domain_end<=8):
                drawable = True
                label = "left"
            elif(domain_end==3 or domain_end==9):
                drawable = True
                label = "straight"
            else:
                drawable = False
                label = "none"
                print('invalid line')
        elif(domain_begin==1):
            if(3<=domain_end<=9):
                drawable = True
                label = "straight"
            else:
                drawable = False
                label = "none"
                print('invalid line')
        elif(domain_begin==2):
            if(4<=domain_end<=8):
                drawable = True
                label = "right"
            elif(domain_end==3 or domain_end==9):
                drawable = True
                label = "straight"
            else:
                drawable = False
                label = "none"
                print('invalid line')
        elif(domain_begin==3):
            if(5<=domain_end<=8):
                drawable = True
                label = "right"
            else:
                drawable = False
                label = "none"
                print('invalid line')
        elif(domain_begin==9):
            if(4<=domain_end<=7):
                drawable = True
                label = "left"
            else:
                drawable = False
                label = "none"
                print('invalid line')
        else:
            drawable = False
            label = "none"
            print('invalid line')
        print(drawable, label)
        return drawable, label

    def generate_image(self, W, H, domain_num_W, domain_num_H, dst_dir, csv_name, img_num, line_width, class_label):
        straight_num = img_num//3
        left_num = img_num//3
        right_num = img_num//3
        for dir_no in class_label.values():
            os.makedirs(dst_dir + dir_no, exist_ok=True)
        with open(dst_dir + csv_name, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['path','label'])
            straight_generated = 0
            left_generated = 0
            right_generated = 0
            while(straight_generated + left_generated + right_generated < img_num):
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
                    image = cv2.line(image, begin, end ,color, line_width)
                    image = cv2.line(image, begin, (end[0]+line_width, end[1]), color, line_width)
                    image = cv2.line(image, begin, (end[0]-line_width, end[1]), color, line_width)
                    image = cv2.line(image, (0,H-line_width), (W, H-line_width), color, line_width//2)
                    image = cv2.line(image, (line_width,0), (line_width, H), color, line_width//2)

                    cv2.imwrite(dst_dir + class_label[label] + "/" + str(straight_generated) + ".png", image)
                    writer.writerow(['./'+dst_dir +class_label[label] + "/" + str(straight_generated) + ".png",class_label[label]])
                    print(straight_generated)
                    straight_generated = straight_generated + 1
                elif((label=="left") and (left_generated < left_num)):
                    image = cv2.line(image, begin, end ,color, line_width)
                    image = cv2.line(image, begin, (end[0]+line_width, end[1]), color, line_width)
                    image = cv2.line(image, begin, (end[0]-line_width, end[1]), color, line_width)
                    image = cv2.line(image, (0,H-line_width), (W, H-line_width), color, line_width//2)
                    image = cv2.line(image, (line_width,0), (line_width, H), color, line_width//2)

                    cv2.imwrite(dst_dir + class_label[label] + "/" + str(left_generated) + ".png", image)
                    writer.writerow(['./'+dst_dir +class_label[label] + "/" + str(left_generated) + ".png",class_label[label]])
                    print(left_generated)
                    left_generated = left_generated + 1
                elif((label=="right") and (right_generated < right_num)):
                    image = cv2.line(image, begin, end ,color, line_width)
                    image = cv2.line(image, begin, (end[0]+line_width, end[1]), color, line_width)
                    image = cv2.line(image, begin, (end[0]-line_width, end[1]), color, line_width)
                    image = cv2.line(image, (0,H-line_width), (W, H-line_width), color, line_width//2)
                    image = cv2.line(image, (line_width,0), (line_width, H), color, line_width//2)
                    
                    cv2.imwrite(dst_dir + class_label[label] + "/" + str(right_generated) + ".png", image)
                    writer.writerow(['./'+dst_dir +class_label[label] + "/" + str(right_generated) + ".png",class_label[label]])
                    print(right_generated)
                    right_generated = right_generated + 1 
                print("-------------------------")

class image_generator():
    def __init__(self):
        pass
    def write_straight(self, image, width, height, color, line_width, direction="straight", grad_range=(40, 45, 3)):
        if(direction=="straight"):
            grad  = np.random.randint(-grad_range[2],grad_range[2]+1)
            begin = (np.random.randint(line_width,width-line_width), 0)
            end   = (int(math.tan(math.radians(grad))*height) + begin[0], height) 
        elif(direction=="right"):
            grad = np.random.randint(-grad_range[1],-grad_range[0]+1)
            rand = np.random.randint(line_width*3,width+height-line_width*3)
            if(rand < width):
                begin = (rand, 0)
                end   = (int(math.tan(math.radians(grad))*height) + begin[0], height)
            else:
                begin = (width, rand-width)
                end   = (width + int(math.tan(math.radians(grad))*(height-begin[1])), height)
        elif(direction=="left"):
            grad = np.random.randint(grad_range[0],grad_range[1]+1)
            rand = np.random.randint(line_width*3,width+height-line_width*3)
            if(rand < width):
                begin = (width-rand, 0)
                end   = (int(math.tan(math.radians(grad))*(height)+begin[0]), height)
            else:
                begin = (0, rand-width)
                end   = (int(math.tan(math.radians(grad))*(height-begin[1])), height)
        else:
            print("error: should specify the direction in write_straight()")
            return
        image = cv2.line(image, begin, end, color, line_width)
        image = cv2.line(image, begin, (end[0]+line_width, end[1]), color, line_width)
        image = cv2.line(image, begin, (end[0]-line_width, end[1]), color, line_width)
        image = cv2.line(image, (0,height-line_width), (width, height-line_width), color, line_width//2)
        image = cv2.line(image, (line_width,0), (line_width, height), color, line_width//2)
        return image
        
    def write_curve(self, image, width, height, color, line_width, direction="right"):
        while(1):
            rand = np.random.randint(line_width*2,height-line_width/2)
            axes = (rand, np.random.randint(rand-line_width*2, rand+line_width*2))
            norm = int(math.sqrt((axes[0])**2 + (axes[1])**2))
            if(norm > width/2):
                break
        if(direction == "right"):
            center = (width,height)
        elif(direction == "left"):
            center = (0,height)
        else:
            print("error: should specify the direction in write_curve()")
            return
        
        angle = np.random.randint(-5,6)
        image = cv2.ellipse(image,center,axes,angle,0,360,color,line_width)
        return image

    def generate_dataset(self, dst_dir, width=30, height=30, line_width=4, img_num=50, class_label={"straight" : "0", "right_straight" : "1", "left_straight" : "2", "right_curve" : "3","left_curve" : "4",}):
        for dir_no in class_label.values():
            os.makedirs(dst_dir + dir_no, exist_ok=True)
        with open(dst_dir + 'dataset.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['path','label'])
            for label in class_label:
                j=0
                while(j<img_num):
                    image = np.zeros((height,width,1), dtype=np.uint8)
                    image.fill(255)
                    color=0
                    if(label=="straight"):
                        image = self.write_straight(image, width, height, color, line_width, "straight")
                    elif(label=="right_straight"):
                        image = self.write_straight(image, width, height, color, line_width, "right")
                    elif(label=="left_straight"):
                        image = self.write_straight(image, width, height, color, line_width, "left")
                    elif(label=="right_curve"):
                        image = self.write_curve(image, width, height, color, line_width, "right")
                    elif(label=="left_curve"):
                        image = self.write_curve(image, width, height, color, line_width, "left")
                    else:
                        print("Unknown Class")
                    cv2.imwrite(dst_dir + class_label[label] + "/" + str(j) + ".png", image)
                    writer.writerow(['./'+dst_dir +class_label[label] + "/" + str(j) + ".png",class_label[label]])
                    j = j+1