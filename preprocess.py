# -Programmer Name: Gan Qian Chao TP055444
# -Program Name : Image Upload Preprocessing (IDFD Bad Quality Image Detection)
# -Description : Use for detect bad quality image which is blur, glare and tilt
# -First Written on: 20 March 2023
# -Editted on: 10 April 2023
from skimage.transform import hough_line, hough_line_peaks
from skimage.feature import canny
from skimage.io import imread
from skimage.color import rgb2gray
from scipy.stats import mode
import cv2
import numpy as np

#Blur detection (variance of sobel)
def variance_of_sobel(image):
    # compute the Sobel of the image and then return the focus
    # measure, which is simply the variance of the Sobel
    sobelx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
    return np.mean(sobelx**2 + sobely**2)

def check_blur(image):
    #blur_detection
    img = cv2.imread(image)
    resize_img = cv2.resize(img,(540,960))
    sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpen = cv2.filter2D(resize_img, -1, sharpen_kernel)
    # convert the region to grayscale, then apply the blur detection algorithm
    gray = cv2.cvtColor(sharpen, cv2.COLOR_BGR2GRAY)
    fs = variance_of_sobel(gray)
    blur = 0                             
    if fs < 7000:
        blur = 1
    return blur

#Glare_detection using binary threshold
def check_glare(image):
    img = cv2.imread(image)
    #glare_detection
    glare = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # apply thresholding to the grayscale image
    ret, thresh = cv2.threshold(glare, 250, 255, cv2.THRESH_BINARY)

    # count the number of non-zero pixels
    nz_count = cv2.countNonZero(thresh)

    # calculate the size of the image
    img_size = img.shape[0] * img.shape[1]

    # calculate the percentage of non-zero pixels
    nz_percent = (nz_count / img_size) * 100

    # classify the image as glared or not
    if nz_percent > 1:
        glare=1
    else:
        glare=0
    return glare

#Check tilt with Canny+ Hough Line
def check_tilt(image):
    img = rgb2gray(imread(image))
    # convert to edges
    edges = canny(img)
    # Classic straight-line Hough transform between 0.1 - 180 degrees.
    tested_angles = np.deg2rad(np.arange(0.1, 180.0))
    h, theta, d = hough_line(edges, theta=tested_angles)
    
    # find line peaks and angles
    accum, angles, dists = hough_line_peaks(h, theta, d)
    
    # round the angles to 2 decimal places and find the most common angle.
    most_common_angle = mode(np.around(angles, decimals=2),keepdims=True)[0]
    
    # convert the angle to degree for rotation.
    skew_angle = np.rad2deg(most_common_angle - np.pi/2)
    tilt = 0
    for angle in skew_angle:
        if angle>0:
            if angle>10 and angle<80:
                tilt = 1
        else:
            if angle>-80 and angle<-10:
                tilt = 1
    return tilt

def check_bad_quality(file_stream):
    #blur_detection
    blur = check_blur(file_stream)
    #glare_detection
    glare = check_glare(file_stream)
    #tilt_detection
    tilt = check_tilt(file_stream)
    return blur,glare,tilt