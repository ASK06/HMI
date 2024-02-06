*** Settings ***
Library  RPA.Images

*** Test Cases ***
Comparison
    ${R}=  Find Template In Image  C:\\Users\\u115949\\Downloads\\originalimage.jpg   C:\\Users\\u115949\\Downloads\\croppedimage.jpg
    Log To Console  ${R}

Comparison1
    ${s}=  Find Template In Image  C:\\Users\\u115949\\OneDrive - Trane Technologies\\Pictures\\original_image1.jpg    C:\\Users\\u115949\\OneDrive - Trane Technologies\\Pictures\\cropped_image1.jpg
    Log To Console  ${s}

Comparison2
    ${t}=  Find Template In Image  C:\\Users\\u115949\\Downloads\\HAT_Web_App_1\\HAT_Web_App\\assets\\hat_current_image.jpg    C:\\Users\\u115949\\OneDrive - Trane Technologies\\Pictures\\cropped_image.jpg
    Log To Console  ${t}