# E-KYC_prototype_with_ID_card_fraud_detection_system_ IDFD_Python
This application is applied with concept of E-KYC which user need to gain authorize through registered ID card.
- Language used: Python, HTML, CSS, JavaScript
- DBMS used: MySQL
- Library used: Flask, ULtralytic YOLO, Pillow, Open CV

#Alert:
- The model for recognizing the landmark and Fin card is available in this link: https://drive.google.com/file/d/1aHknOtwghd3A76KLDXDitnrmLpFgZOVt/view?usp=sharing
- Dataset are available as below:
  1. midv2020 fin_id (Finland ID card) dataset link:
  https://drive.google.com/file/d/1jnAC2y8uVOjKMisKo-pAOdrCREf6Pxry/view?usp=sharing
  2. Fraud fin_id (Finland ID card) dataset link:
  https://drive.google.com/file/d/1eqAq9DMNa-Ivf-BqpdAkoqEJeLMu9mlU/view?usp=sharing
  3. YOLO landmark detection dataset link:
  https://drive.google.com/file/d/1cBxlr1EA4KGFBd9IpIhgavrdRmiz8_gs/view?usp=sharing 
  4. YOLO landmark fraud classification dataset link:
  https://drive.google.com/file/d/1eauvQGRa-WZz-ToI7kYed9wdhXxdXoCI/view?usp=sharing


# Dataset
- The dataset used is midv2020's Fin id dataset (Source link: https://arxiv.org/ftp/arxiv/papers/2107/2107.00396.pdf)
- The fraud card dataset is designed using PhotoPea for performing image forgery such as splicing and copy move towards the original card's ID details and security features named as fraud_fin_id

# Introduction
In these few years of pandemic, the applying of eKYC (Electronic Know Your Customer) to the online financial applications for making identification verification using identification card is increasing and it had made the online working process become easier and more secured than the traditional methods of verification. However, there are a misuse of technology by the identity theft on using the design software for tampering identity to commit fraud on the cards stolen from the victim. The identity theft can change their identity easily by using designing tools to do image manipulation towards the card that going to be uploaded to eKYC application. It may cause the identity theft to gain unauthorized access towards the eKYC account by using the fake card tampered. With the problem stated above, the introduction of the fraud detector (IDFD) towards card fraud is becoming more needed to help on detecting the identity theft to use fake card on accessing high privacy account with a more effective and efficiency solution. 

# Deliverables
- There are 2 target users which are
  1) Financial Application Customer
  2) Financial Application Administrator
- The eKYC based financial web application allow customers to:
  1) Register an eKYC account
  2) Login the eKYC account
- The eKYC based financial web application allow administrator to:
  1) View customer eKYC account detail 
  2) Read and view eKYC access records
- The card fraud detector system (IDFD) allows the financial application customer to:
  1) Upload the identification card for verification during registration and login account
  2) Reupload image if card image is rejected
  3) Receive digital alert email while the card from the same account rejected for multiple times
  4) Block access if the authentication request attempt used out
  5) Receive an auto-generated OTP in the email after fraud detection passed
  6) Do face recognition on the face in uploaded card during every login to account
- The card fraud detector system (IDFD) allows the financial application administrator to:
  1) Look over access history of customer

# Development process
- On detecting bad quality image uploaded, bad image like tilt, blur and glare image are rejected before the ID fraud detection started
- On detecting fraud in card, YOLO had been applied to train to differentiate the real and fake landmarks such as face (face), small face landmark (landmark_1), small face landmark with code (landmark_2) and signature in the card using YOLO_landmark_fraud_classification_dataset
- On detecting the Finland ID, YOLO is used to be trained for recognizing the availability of features in uploaded image using YOLO_landmark_detection_dataset
- On verifing text content, the text detection is using the Regex library and Google OCR to detect the text and matching text content with data recorded in MySQL.

