#!/usr/bin/env python3.6.8
# -*- coding: utf-8 -*-
# Copyright:    Yuhan Jiang
# Email:        yuhan.jiang@marquette.edu
# Date:         10/03/2020
# Discriptions : Read the GPS from Screenshot of Google Earth web (fullscreen on 2nd monitor)
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
import cv2 as cv
import re,os
import matplotlib.pyplot as plt

# read image
def ORC_GoogleEarthScreenshotGPS(imgName,path,showResult_bool=True):
    im = cv.imread(path+'Capture'+str(imgName)+'.PNG')
    img_rgb = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
    part=[]
    part.append(img_rgb[1050:1079,3593:3618])#camera
    part.append(img_rgb[1050:1079,3641:3655])#N_degree
    part.append(img_rgb[1050:1079,3658:3674])#N_min
    part.append(img_rgb[1050:1079,3677:3691])#N_sec
    part.append(img_rgb[1050:1079,3707:3721])#W_degree
    part.append(img_rgb[1050:1079,3726:3740])#W_min
    part.append(img_rgb[1050:1079,3743:3756])#W_sec

    partcopy=part.copy()

    StringList=['Camera','N_deg','N_min','N_sec','W_deg','W_min','W_sec']

    letter=[]
    for i in range(len(part)):
        part[i]=cv.bilateralFilter(part[i],-1,5,5)
        ret,part[i]=cv.threshold(part[i],160,255,cv.THRESH_BINARY_INV)

        lt=re.sub('[\W_]+','',pytesseract.image_to_string(part[i]))# only keep num

        if 'a' in lt:# handel the error 8 be detected as a
            new=""
            for i in range(len(lt)):
                if i==lt.index('a'):
                    new=new+'8'
                else:
                    new=new+lt[i]
            lt=new

        if lt=='' or lt.isdigit()==False: # check blank and non- number
            imagebackup=partcopy[i]# try second time, otherwise manually input it
            imagebackup=cv.bilateralFilter(imagebackup,-1,5,5)
            ret2,imagebackup=cv.threshold(imagebackup,150,255,cv.THRESH_BINARY)

            lt=re.sub('[\W_]+','',pytesseract.image_to_string(imagebackup))

            if lt=='' or lt.isdigit()==False:  # check blank and non- number
                fig=plt.figure("Capture"+str(imgName)+'_'+StringList[i]+'_Err!_'+str(lt))
                plt.imshow(partcopy[i])
                plt.show()
                lt=input("Err! Please Input the Number in the Figure:")
                #plt.clf()
                plt.close(fig)

        if lt.isdigit():
            letter.append(lt)
        else:
            print("Error")

            #print("Camera:",letter[0],end='\t')
            #print(letter[1],"°",letter[2],"'",letter[3],'" N',end='\t')
            #print(letter[4],"°",letter[5],"'",letter[6],'" W',end='\t')

    if showResult_bool:

            plt.figure("Capture"+str(imgName))
            plt.ion()
            ax=[]
            for i in range(len(part)):
                ax.append(plt.subplot(1,int(len(part)),int(i)+1))
                ax[i].set_xlabel(letter[i])
                plt.imshow(part[i])
            plt.pause(3)
            plt.ioff()
            plt.clf()
            plt.close()
            del ax
    print(str(imgName),'\t',"Camera:",letter[0],end='\t')
    print(letter[1],"°",letter[2],"'",letter[3],'" N',end='\t')
    print(letter[4],"°",letter[5],"'",letter[6],'" W',end='\n')
    return letter,StringList

def add_Py3D_log(glb_file_path,str_data):
    path_file_name = glb_file_path+'HighwayASS_GPS.txt'
    if not os.path.exists(path_file_name):
        with open(path_file_name, "w") as f:
            print(f)
    with open(path_file_name, "a") as f:
        f.writelines(str_data)
#-----------------
if __name__ == '__main__':
    imglist=range(53)
    path='D:/CentOS/G3/'
    option1=False
    option2=True
    for i in imglist:
        l,string=ORC_GoogleEarthScreenshotGPS(i,path,showResult_bool=1) # l is int list [275, 43,03,38, 87,55,14], string is string list  ['Camera','N_deg','N_min','N_sec','W_deg','W_min','W_sec']

        if option1==True:
            l_float=[float(le) for le in l ]# Option 1 save GPS coordinate as float
            Latitude_float=format(l_float[1]+l_float[2]/60+l_float[3]/60/60,'.4f')
            Longitude_float=format(-(l_float[4]+l_float[5]/60+l_float[6]/60/60),'.4f')
            add_Py3D_log(path,[str(i),'\t',l[0],'\t',str(Latitude_float),'\t',str(Longitude_float),'\n']) # format ID 0, Camera 275, Latitude 43.0606,Longitude -87.9206
        if option2==True:
            letter=[] # Option 2
            for j in range(len(l)):
                letter.append(str(l[j]))
            #add_Py3D_log(path,[str(i),'\t',letter[0],'\t',letter[1],"°",letter[2],"'",letter[3],'"\tN\t',letter[4],"°",letter[5],"'",letter[6],'"\tW\n']) # format ID 0, Camera 275, Latitude 43°03'38" N,Longitude 87°55'14" W
            add_Py3D_log(path,[str(i),'\t',letter[0],'\t',letter[1],"\t",letter[2],"\t",letter[3],'\tN\t',letter[4],"\t",letter[5],"\t",letter[6],'\tW\n'])# format ID 0, Camera 275, Latitude Deg 43 Min 03 Sec38 N, Longitude Deg 87 Min 55 Sec14  W