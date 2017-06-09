# Private Video Conference Software ( PVCS ) 
Nginx + Flask + Mongo [ Video Conference Application , that manages you to have a ip based services with as many audience as possible ] It is like skype but with a lot of users. 

Here it is used an application written in Flask + Mongo to manage an Online Video Call Conference Web application. 

Nginx is used to spread the streams to the clients and stream access is managed by the Flask Application. 

Feature options are Stream Watermarking. 

After this is done , each stream will watermark its ip and then if there is a leak , due to someone recording the stream , when file is 
given to the system , it shows who recorded it and when. 

Watermarking intends to cover : 
1) Audio Watermarking 
2) Video Watermarking 

In the repository you can find the source code of the Managing Application + API. 

**Requirements :** 
1. ffmpeg 
2. nginx - rtmp 

