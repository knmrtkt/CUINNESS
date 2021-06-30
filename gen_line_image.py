import os
import csv
import cv2
import numpy as np

class gen_line_image():
    def __init__(self):
        pass
    def generate_point(self, W, H, r):
        if(0 <= r < W):
            return r, 0
        elif(0 <= r< (W+H)):
            return W, r-W
        elif((W+H) <= r < (2*W+H)):
            return (2*W+H)-r, W
        elif((2*W+H) <= r < (2*W+2*H)):
            return 0, (2*W+2*H)-r
        return 0,0

    def get_domain_from_coord(self, W, H, r, domain_num_W, domain_num_H):
        if(0 <= r < W):
            return int(r/(W/domain_num_W))
        elif(0 <= r < (W + H)):
            return domain_num_W + int((r-W)/(W/domain_num_H))
        elif((W + H) <= r < (2*W + H)):
            return domain_num_W + domain_num_H + int((r-W-H)/(W/domain_num_W))
        else:
            return 2*domain_num_W + domain_num_H + int((r-2*W-H)/(H/domain_num_H))

    def begin_or_end(self, a, b, domain_a, domain_b):
        if(a[1] > b[1]):
            a, b = b, a
            domain_a, domain_b = domain_b, domain_a
        return a, b, domain_a, domain_b

    def get_label_from_domain(self, domain_begin, domain_end):
        if(domain_begin==0):
            if(4<=domain_end<=8):
                return "left"
            elif(domain_end==3 or domain_end==9):
                return "straight"
        elif(domain_begin==1):
            if(3<=domain_end<=9):
                return "straight"
        elif(domain_begin==2):
            if(4<=domain_end<=8):
                return "right"
            elif(domain_end==3 or domain_end==9):
                return "straight"
        elif(domain_begin==3):
            if(5<=domain_end<=8):
                return "right"
        elif(domain_begin==9):
            if(4<=domain_end<=7):
                return "left"
        return "none"

    def generate_image(self, W, H, domain_num_W, domain_num_H, dst_dir, csv_name, img_num, line_width, class_label):
        ## threshold for excepting short line
        th = (W//2)**2
        color=0
        ## generate directory
        for dir_no in class_label.values():
            os.makedirs(dst_dir + dir_no, exist_ok=True)
        ## generate blank image
        # os.makedirs(dst_dir + str(len(class_label)), exist_ok=True)
        # for i in range(img_num//len(class_label)):
        #     image = np.zeros((H,W,1), dtype=np.uint8)
        #     image.fill(255)
        #     cv2.imwrite(dst_dir + str(len(class_label)) + "/" + str(i) + ".png", image)
        ## generate line image
        with open(dst_dir + csv_name, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['path','label'])
            generated = {}
            for label in class_label:
                generated[label] = 0
            while(sum(generated.values()) < img_num):
                image = np.zeros((H,W,1), dtype=np.uint8)
                image.fill(255)
                r_a = np.random.randint(0, 2*W + 2*H)
                r_b = np.random.randint(0, 2*W + 2*H)
                a = self.generate_point(W, H, r_a)
                b = self.generate_point(W, H, r_b)
                domain_a = self.get_domain_from_coord(W, H, r_a, domain_num_W, domain_num_H)
                domain_b = self.get_domain_from_coord(W, H, r_b, domain_num_W, domain_num_H)
                begin, end, domain_begin, domain_end = self.begin_or_end(a, b, domain_a, domain_b)
                label = self.get_label_from_domain(domain_begin, domain_end)
                ## except none label image and extreamly short line
                if((label == 'none' or (begin[0]-end[0])**2 + (begin[1]-end[1])**2 < th) and (generated[label] >= img_num//len(class_label))):
                    continue
                image = cv2.line(image, begin, end ,color, line_width)
                ## thick line
                image = cv2.line(image, begin, (end[0]+line_width//2, end[1]), color, line_width)
                image = cv2.line(image, begin, (end[0]-line_width//2, end[1]), color, line_width)
                
                cv2.imwrite(dst_dir + class_label[label] + "/" + str(generated[label]) + ".png", image)
                writer.writerow(['./'+dst_dir +class_label[label] + "/" + str(generated) + ".png",class_label[label]])
                generated[label] = generated[label] + 1

    def mark_image(self, W, H, dst_dir, line_width, color, marker_type='nothing'):
        def mark(file_path):
            if(os.path.basename(file_path).split('.', 1)[1] != 'png'):
                return
            image = cv2.imread(file_path)
            if(marker_type=='nothing'):
                pass
            elif(marker_type=='cross'):
                image = cv2.line(image, (0,H-line_width), (W, H-line_width), color, line_width//2)
                image = cv2.line(image, (line_width,0), (line_width, H), color, line_width//2)
            elif(marker_type=='point'):
                image = cv2.rectangle(image, (line_width, H-2*line_width), (2*line_width, H-line_width), color, -1)
            elif(marker_type=='rectangle'):
                image = cv2.rectangle(image, (line_width, H-3*line_width), (2*line_width, H-line_width), color, -1)
            elif(marker_type=='three'):
                image = cv2.rectangle(image, (line_width, H-2*line_width), (2*line_width, H-line_width), color, -1)

            cv2.imwrite(file_path, image)

        def recursive_file_check(path):
            if os.path.isdir(path):
                files = os.listdir(path)
                for file in files:
                    recursive_file_check(path + "/" + file)
            else:
                mark(path)

        recursive_file_check(dst_dir)
        
def main():
    ImageSize = 32
    img_num = 90
    img_gen = gen_line_image()
    img_gen.generate_image(ImageSize, ImageSize, 3, 2, 'linetrace/', 'dataset.csv', img_num, 4, {"straight" : "0", "right" : "1", "left" : "2",})
    img_gen.mark_image(ImageSize, ImageSize, 'linetrace', 4, 0, marker_type='cross')

if __name__ == "__main__":
    main()