import os
from PIL import Image
import numpy as np
from math import sqrt
from math import floor
import cv2
import copy
import time
from datetime import datetime
from random import randint

def getAverageRGB(image):
    im = np.array(image)
    if  len(im.shape) == 3:
        w, h, d = im.shape
        return (tuple(np.average(im.reshape(w * h, d), axis=0)))
    else:
        return [0, 0, 0]


def processImages(path):
    filenames = []
    meanRGBs = []

    for file in os.listdir(path):
        filepath = os.path.join(path, file)
        img = Image.open(filepath)

        filenames.append(file)
        meanRGBs.append(
            [int(val) for val in getAverageRGB(img)]
        )
    return filenames, meanRGBs


def distance2Color(rgb1, rgb2):
    sum = 0
    for i in range(len(rgb1)):
        sum += (pow(rgb1[i] - rgb2[i], 2))
    return sqrt(sum)


def getPaintingIndex(rgb, meanRGBs):
    curIndex = 0
    betaIndex = 0
    betaDistance = float('inf')

    for meanRGB in meanRGBs:
        colorDistance = distance2Color(meanRGB, rgb)
        if colorDistance < betaDistance:
            betaIndex = curIndex
            betaDistance = colorDistance 

        curIndex += 1
    return betaIndex





def create_mosaic(filename):
    # PARAMETERS
    startRow = 37
    slices = 20
    n_splits = 1
    dim = 50
    no_repeat = False
    
    #fileName = sys.argv[1]
    srcPath = "C:\\Users\\xlqgi\\DEV\\Friends\\Picazzo\\src\\" + filename
    destPath = "C:\\Users\\xlqgi\\DEV\\Friends\\Picazzo\\mosaic\\mosaic-" + filename
    thumbnailPath = "C:\\Users\\xlqgi\\DEV\\Friends\\Picazzo\\thumbnails\\image-thumbnail-" + filename
    sectionPath = "C:\\Users\\xlqgi\\DEV\\Friends\\Picazzo\\sections\\sections-"
    paintingSourcePath = "C:\\Users\\xlqgi\\DEV\\Friends\\Picazzo\\elli_processed_paintings"


    # Image Processing to reduce dimensions of srcFile
    img = Image.open(srcPath)
    img.thumbnail((400, 400))
    img.save(thumbnailPath)


    # Initialize create_image
    create_image = []   
    create_image_index = 0


    # Process resized images
    filenamesO, meanRGBsO = processImages(paintingSourcePath)
    filenames = copy.copy(filenamesO)
    meanRGBs = copy.copy(meanRGBsO)
    paintingSplitIndex = floor(len(filenames) / n_splits)


    
    # Section out image
    img = cv2.cvtColor(cv2.imread(thumbnailPath), cv2.COLOR_BGR2RGB)
    height = img.shape[1]
    incrementSlice = floor(height / slices)
    sliceFilePaths = []


    # Timer setup
    times = []


    # Iterate image 
    count = 0
    n_split_counter = 0
    for rowNum in range(startRow, len(img)):

        # Timer functionality
        start = time.perf_counter()


        # Section out every increment
        if rowNum % incrementSlice == 0 and rowNum != 0:
            sliceFilePath = sectionPath + str(count) + ".jpg"
            cv2.imwrite(sliceFilePath, np.asarray(create_image))
            create_image = []
            count += 1
            sliceFilePaths.append(sliceFilePath)
            create_image_index = 0

        # Instantiate 50 empty rows for every row in our thumbnail
        for i in range(dim):
            create_image.append([])


        # Iterate pixels and retrieve corresponding painting
        row = img[rowNum]
        for pixelNum in range(len(row)):
            pixel = row[pixelNum]


            if n_splits > 1:
                n_split_counter = randint(0, n_splits)
                paintingStartIndex = paintingSplitIndex * n_split_counter
                paintingEndIndex = paintingSplitIndex * (n_split_counter + 1)


            # Identify painting (remove copies)
                paintingIndex = getPaintingIndex(pixel, 
                    meanRGBs[
                        paintingStartIndex : paintingEndIndex
                    ]
                )
                paintingName = filenames[
                    paintingStartIndex : paintingEndIndex
                ][paintingIndex]
            #n_split_counter += 1

            paintingIndex = getPaintingIndex(pixel, meanRGBs)
            paintingName = filenames[paintingIndex]

            path2Painting = os.path.join(paintingSourcePath, paintingName)
            painting = cv2.imread(path2Painting)



            # Debugging
            '''
            cv2.imshow("window", painting)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            '''


            if no_repeat:
                filenames.remove(paintingName)
                meanRGBs.pop(paintingIndex)

                # Check if we've gone through all paintings
                if len(filenames) == 1:
                    filenames = copy.copy(filenamesO)
                    meanRGBs = copy.copy(meanRGBsO)


            # Populate image with either painting
            for i in range(create_image_index,  create_image_index + dim):
                for j in range(dim):
                    create_image[i].append(painting[i - create_image_index][j])


            
            #print("ROW: " + str(rowNum) + ", PIXEL: " + str(pixelNum))
        
        create_image_index += dim
        #cv2.imwrite('test.jpg', np.asarray(create_image))


        end = time.perf_counter()
        expectedDiff = round((end - start) * (len(img) - rowNum) / 60, 2)
        print("Finished row: " + str(rowNum))
        print("Expected Completion in: " + str(expectedDiff) + "minutes")



    # Save Image
    final_image = []
    for filepath in sliceFilePaths:
        sliceIMG = cv2.imread(filepath)
        for row in sliceIMG:
            final_image.append(row)

    cv2.imwrite(destPath, np.asarray(final_image))

    
def main():

    srcfilenames = ['rama_ravana.jpg'] 
    for srcfilename in srcfilenames:
        print("Beginning " + srcfilename)
        create_mosaic(srcfilename)


if __name__ == "__main__":
    main()