import cv2

gstreamer_pipeline = (
    'v4l2src device=/dev/video3 ! '
    'image/jpeg, width=4032, height=3040, framerate=10/1 ! '
    'jpegdec ! '
    'videoconvert ! '
    'appsink'
)

cap = cv2.VideoCapture(gstreamer_pipeline, cv2.CAP_GSTREAMER)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

i = 0
while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Error: Could not read frame.")
        break
    
    # Display the resulting frame
    #cv2.imshow('USB Camera Feed', frame)
    print(frame.shape)
    frame= cv2.resize(frame, (320,320))
    cv2.imwrite(f'test/images{i}.jpg',frame)
    cv2.imshow('frame', frame)

    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    i+=1
    break

cap.release()
cv2.destroyAllWindows()
