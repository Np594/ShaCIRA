# ShaCIRA
ShaCIRA (Shape &amp; Colour Identifying Robotic Arm)
As Part of my Final year at Uni, I undertook a project to develop a robotic arm that can sort objects based on their shape and colour.
The robotic arm consisted of 6 servos, 1 360-degree servo for the base and then 5 more 180-degree servos.
This project combined Motor control, a Spoken interface, and computer vision.
Motor control was achieved using a 40-pin servo hat and calculating pulse width values, and mapping them to the duty cycle of the servos.
The spoken interface used Speech_Recognition, PYTTSX3, and rapidfuzz to record, reply and match commands.
Computer vision involved training a custom YOLOv11n model along with opencv for object detection.
All these elements were combined to enable the robot's functionality: 
A spoken command is given by the user to sort the objects by shape or colour
Following this, the object detection model is invoked and based on the object the camera sees, the arm sorts it into 1 of 4 bowls until no more objects are presented.
