import cv2

img = cv2.imread('../data//train//non-erotic//1.jpg')
# get the dimensions of the image
height, width, channels = img.shape
print(f"Image dimensions: {width}x{height}, {channels} channels")
cv2.imshow('Image', img)
# wait for a key press to close the window
cv2.waitKey(0)
cv2.destroyAllWindows()