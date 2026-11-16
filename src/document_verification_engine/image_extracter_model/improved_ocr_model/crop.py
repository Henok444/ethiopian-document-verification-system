import cv2
import sys
from pathlib import Path
import numpy as np 

#  reading the image 
path = Path(__file__).resolve().parents[4]

crop_dir = path / "data" / "crop" ; Path(crop_dir).mkdir(exist_ok=True)


a = path / "data"/ "test_image2"  / "id_2.png"
b = path / "data"/ "test_image2"  / "id_3.jpeg"


#-----------------------------------------

def crop(img_path):
    img = cv2.imread(img_path)

    #makeing it gray 


    gray = cv2.cvtColor(img , cv2.COLOR_BGR2GRAY )



    cv2.imwrite(path / "data" / "gray.png" , gray)
    print(gray.shape)

    #----------------------------------------

    # making it black acd white 

    my_threshold = 110 # i can make it authomatic by adding + cv2.THRESH_OTSU)


    t , bw = cv2.threshold(gray , my_threshold , 225 ,cv2.THRESH_BINARY_INV )# + cv2.THRESH_OTSU)

    cv2.imwrite(path / "data" / "thr.png" , bw )
    print(t)


    # --------------------------------------------------

    # --------------------------------------------------

    # removing big objects / finding the box of big object to remove
    # them in the dialation proccess 

    # what i will remove , very long horizontal line 
    # - very big vetical line box


    # creating a window box to slide in the image 
    width_of_the_sliding_window = 1
    height_of_sliding_window = 3


    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (width_of_the_sliding_window, height_of_sliding_window))

    smeared = cv2.dilate(bw, kernel)
    """

    k2 = cv2.getStructuringElement(cv2.MORPH_RECT, (20 , 1))


    smeared = cv2.dilate(sm , k2)
    """

    cv2.imwrite(path / "data" / "dilated.png" , smeared)




    # extract each dilated object boundary and create a reclangular box from the top left corner

    # first create or draw the bondary of each corner 


    contours, _ = cv2.findContours(smeared, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # now extract or create a rectangular box and return the top left cornner coordinate and the height and width 

    big_boxes = [cv2.boundingRect(c) for c in contours]
    #filter unwanted box 
    H, W = img.shape[:2]
    MIN_W = 5
    MIN_H  = 10
    Max_w = 0.8*W
    min_area = 700


    boxes = [b for b in big_boxes if b[2] >= MIN_W and b[2]<= Max_w and b[3] >= MIN_H and b[2]*b[3] > min_area]# and b[2] > b[3]]
    boxes.sort(key=lambda b: (b[1], b[0]))

    print(f"found {len(boxes)} boxes ")


    output_img = bw.copy()

    for (x, y, w, h) in boxes:
        # Set all pixels inside this bounding box region to black (0)
        output_img[y : y + h, x : x + w] = 0
    cv2.imwrite(path / "data" / "reducted.png" , output_img)

    #--------------------------------------------------------



    #----------------------------------------------------------

    # dialate the object inside the black and white horizontally 


    # creating a window box to slide in the image 
    def estimate_char_height(bw):
        H, W = bw.shape
        n, labels, stats, _ = cv2.connectedComponentsWithStats(bw, connectivity=8)
        hs = []
        for i in range(1, n):
            x, y, w, h, area = stats[i]
            if h < max(5, 0.004 * H):  continue      # specks
            if h > 0.10 * H:           continue      # photo, frame, big blobs
            if w > 3 * h:              continue      # underlines, long strokes
            hs.append(h)
        return float(np.median(hs)) if len(hs) >= 10 else None

    def dynamic_kernel(bw, w_factor=1.5, h_factor=0.15):
        ch = estimate_char_height(bw) or 0.02 * bw.shape[0]   # fallback if too few components
        kw = max(3, int(round(w_factor * ch)))
        kh = max(1, int(round(h_factor * ch)))
        return cv2.getStructuringElement(cv2.MORPH_RECT, (kw, kh)), ch


    kernel, ch = dynamic_kernel(output_img)
    smeared = cv2.dilate(output_img, kernel)
    print("char height:", ch)



    #k2 = cv2.getStructuringElement(cv2.MORPH_RECT, (20 , 1))


    #smeared = cv2.dilate(sm , k2)


    cv2.imwrite(path / "data" / "dilated.png" , smeared)


    #---------------------------------------------------------

    # extract each dilated object boundary and create a reclangular box from the top left corner

    # first create or draw the bondary of each corner 


    contours, _ = cv2.findContours(smeared, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # now extract or create a rectangular box and return the top left cornner coordinate and the height and width 

    boxes_be = [cv2.boundingRect(c) for c in contours]

    #--------------------------------------------------------

    #filter unwanted box 
    H, W = img.shape[:2]

    MIN_W = 50
    MIN_H  = 5
    MAX_W = 0.8 * W
    minimum_area = 500000


    boxes_to = [b for b in boxes_be if b[2] >= MIN_W and b[2] <= MAX_W and b[3] >= MIN_H  and b[2] > 2*b[3] and b[2]*b[3] < minimum_area]# 
    # Choose a tolerance based on your average text height (e.g., 15-20 pixels)
    X_TOLERANCE = 100


    # Sort by the row bucket first (y // tolerance), then by x coordinate
    boxes_to.sort(key=lambda b: (b[0]// X_TOLERANCE , b[1]))

    #------------------------------------------------

    # draw a red box on copy of the image for visual inspection and crop the image
    PAD = 5  # if you want to prevent cutting text edges 

    vis = img.copy()
    H, W = img.shape[:2] # to find the border of the original image 

    for i, (x, y, w, h) in enumerate(boxes_to, 1):
        cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(vis, str(i), (x, max(y - 4, 12)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        x1, y1 = max(x - PAD, 0), max(y - PAD, 0)
        x2, y2 = min(x + w + PAD, W), min(y + h + PAD, H)


        cv2.imwrite( crop_dir / str(f"line_{i:03d}.png"), img[y1:y2, x1:x2])
    cv2.imwrite(path / "data" / "redline.png" , vis )
