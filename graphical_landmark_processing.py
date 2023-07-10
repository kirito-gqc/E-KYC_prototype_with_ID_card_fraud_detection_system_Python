# -Programmer Name: Gan Qian Chao TP055444
# -Program Name : Graphical Landmark Preprocessing (IDFD Graphical Landmark Verification)
# -Description : Use for detect graphical landmarks such as face, face_landmark_1, face_lndmark_2, classify the landmarks detected to fake or real
# -First Written on: 18 March 2023
# -Editted on: 10 April 2023
#import YOLO library and face_recognition
from ultralytics import YOLO
import os
import glob
import face_recognition

predict_dir = "static/model"

#landmark detection (face, face_landmark_1, face_landmark_2, signature)
def detect_landmarks(image):
    model = os.path.join(predict_dir,'yolov8_object_detection.pt')
    obj_detection_model = YOLO(model)
    result = obj_detection_model.predict(source=image, conf=0.25, line_thickness=2, save=True, save_crop=True,save_conf=True, hide_conf=True, project="static", name="result/predict")
    annotation = result[0].boxes.boxes
    myresult = {}
    replace = {}
    for box in annotation:
        label = int(box[-1])
        score = round(100 * float(box[-2]),1)
        if label in myresult:
            original_score = myresult[label]
            if original_score>score:
                myresult[label] = score
                if label in replace:
                    replace[label] += 1
                else:
                    replace[label] = 1
        else:
            myresult[label] = score
              
    return myresult,replace

#get file location of YOLO prediction crops (from static/result/predict)
def get_related_files(image,replace):
    # Get the last folder in the predict directory
    prediction_folders = sorted(glob.glob(os.path.join('static/result/predict*')), key=os.path.getctime)
    latest_predict_dir = prediction_folders[-1]

    if latest_predict_dir:
        corps = os.path.join(latest_predict_dir,'crops')
        face_dir = os.path.join(corps, 'face')
        face_landmark_1_dir = os.path.join(corps, 'face_landmark_1')
        face_landmark_2_dir = os.path.join(corps, 'face_landmark_2')
        signature_dir = os.path.join(corps,'signature')
        landmark_list = [face_dir,face_landmark_1_dir,face_landmark_2_dir,signature_dir]
        base_name = os.path.basename(image)
        name, ext = os.path.splitext(base_name)
        print("base:",base_name)
        i=0
        landmark_image = []
        for landmark in landmark_list:
            if os.path.exists(landmark):
                image_files = glob.glob(os.path.join(landmark, '*.jpg'))
                print(image_files)
                num_images = len(image_files)
                if num_images > 1:
                    if i in replace:
                        file_num = replace[i]
                        end_char = file_num+1
                        target_name = name+str(end_char)+ext
                        target = os.path.join(landmark,target_name)
                        print(target)
                        for file_path in image_files:
                            if file_path == target:
                                landmark_image.append(file_path)
                    else:
                        file_path = image_files[0]
                        landmark_image.append(file_path)                            
                else:
                    file_path = image_files[0]
                    landmark_image.append(file_path)
            i+=1                    
        return latest_predict_dir, landmark_image                            
    else:
        # handle case where no matching directories were found
        error = ""        
        return error,error

#landmark fraud classification (face, face_landmark_1, face_landmark_2, signature), classify to fake and real    
def classify_landmark(file):
    for landmark in file:
        print("landmark:",landmark)
        if landmark == file[0]:
            model = os.path.join(predict_dir,'face_classify.pt')
            face_classify_model = YOLO(model)
            face_result = face_classify_model.predict(source=landmark, conf=0.25, project="static", name="result/classify/face")
            face_probs = face_result[0].probs
            if face_probs[0] < face_probs[1]:
                #No face fraud
                face_fraud = False
            else:
                #Have face fraud
                face_fraud = True
            
        elif landmark == file[1]:
            model = os.path.join(predict_dir,'face_landmark_1_classify.pt')
            landmark_1_classify_model = YOLO(model)
            face_landmark_1_result = landmark_1_classify_model.predict(source=landmark, conf=0.25, project="static", name="result/classify/face_landmark_1")
            face_landmark_1_probs = face_landmark_1_result[0].probs
            if face_landmark_1_probs[0] < face_landmark_1_probs[1]:
                #No landmark 1 fraud
                landmark_1_fraud = False
            else:
                #Have landmark 1 fraud
                landmark_1_fraud = True
        elif landmark == file[2]:
            model = os.path.join(predict_dir,'face_landmark_2_classify.pt')
            landmark_2_classify_model = YOLO(model)
            face_landmark_2_result = landmark_2_classify_model.predict(source=landmark, conf=0.25, project="static", name="result/classify/face_landmark_2")          
            face_landmark_2_probs = face_landmark_2_result[0].probs
            if face_landmark_2_probs[0] < face_landmark_2_probs[1]:
                #No landmark 2 fraud
                landmark_2_fraud = False
            else:
                #Have landmark 2 fraud
                landmark_2_fraud = True
        else:
            model = os.path.join(predict_dir,'signature_classify.pt')
            signature_classify_model = YOLO(model)
            signature_result = signature_classify_model.predict(source=landmark, conf=0.25, project="static", name="result/classify/signature") 
            signature_probs = signature_result[0].probs      
            if signature_probs[0] < signature_probs[1]:
                #No landmark 1 fraud
                signature_fraud = False
            else:
                #Have landmark 1 fraud
                signature_fraud = True       
    return face_fraud, landmark_1_fraud,landmark_2_fraud, signature_fraud

#face match between registered id and uploaded id
def match_face(registered, file):
    face_landmark_obtain = file[0]
    registered_img = face_recognition.load_image_file(registered)
    original_face_encoding = face_recognition.face_encodings(registered_img)[0]

    # my_face_encoding now contains a universal 'encoding' of my facial features that can be compared to any other picture of a face!

    unknown_img = face_recognition.load_image_file(face_landmark_obtain)
    unknown_face_encoding = face_recognition.face_encodings(unknown_img)[0]

    # Now we can see the two face encodings are of the same person with `compare_faces`!

    results = face_recognition.compare_faces([original_face_encoding], unknown_face_encoding)

    if results[0] == True:
        match = True
    else:
        match = False
    return match
