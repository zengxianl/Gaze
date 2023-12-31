#!/usr/bin/env python

import cv2
import numpy as np
import glob


def getmtx():
    """

    Returns:返回一个矫正矩阵

    """
    # Defining the dimensions of checkerboard
    CHECKERBOARD = (6, 9)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # Creating vector to store vectors of 3D points for each checkerboard image
    objpoints = []
    # Creating vector to store vectors of 2D points for each checkerboard image
    imgpoints = []

    # Defining the world coordinates for 3D points
    objp = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
    objp[0, :, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
    prev_img_shape = None

    # Extracting path of individual image stored in a given directory
    images = glob.glob('./calibrateCamera-img/*.jpg')
    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Find the chess board corners
        # If desired number of corners are found in the image then ret = true
        ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, cv2.CALIB_CB_ADAPTIVE_THRESH +
                                                 cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)

        """
        If desired number of corner are detected,
        we refine the pixel coordinates and display 
        them on the images of checker board
        """
        if ret == True:
            objpoints.append(objp)
            # refining pixel coordinates for given 2d points.
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

            imgpoints.append(corners2)

            # Draw and display the corners
            img = cv2.drawChessboardCorners(img, CHECKERBOARD, corners2, ret)

        # cv2.imshow('img', img)
        # cv2.waitKey(0)

    cv2.destroyAllWindows()

    h, w = img.shape[:2]

    """
    Performing camera calibration by 
    passing the value of known 3D points (objpoints)
    and corresponding pixel coordinates of the 
    detected corners (imgpoints)
    """
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    np.save("./param/mtx.npy", mtx)
    print("mtx wrote in mtx.npy")
    np.save("./param/dist.npy", dist)
    print("dist wrote in dist.npy")


def imgcorrect(img, mtx, dist):
    """

    Args:
        img: 待矫正的图片
        mtx: 矫正矩阵
        dist: dist矩阵

    Returns:矫正后的图片

    """
    h, w = img.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

    # 矫正
    dst = cv2.undistort(img, mtx, dist, None, newcameramtx)

    # 裁切图像
    x, y, w, h = roi
    dst = dst[y:y + h, x:x + w]
    cv2.imwrite('imgs/calibresult.png', dst)

    return dst




def main():
    img = cv2.imread("./ORI-IMG2/WIN_20230702_20_19_18_Pro.jpg")
    # getmtx()
    mtx = np.load("./param/mtx.npy")
    dist = np.load("./param/dist.npy")
    ret=imgcorrect(img, mtx, dist)
    cv2.namedWindow("ori", cv2.WINDOW_FREERATIO)
    cv2.namedWindow("ret", cv2.WINDOW_FREERATIO)
    cv2.imshow("ori",img)
    cv2.imshow("ret",ret)
    cv2.waitKey(0)
#getmtx()
main()
