import cv2
import os
from decord import VideoReader
from decord import gpu, cpu
from PIL import Image
import numpy as np

from time import strftime
from time import gmtime


# O for overview
output_O_widthnum = 7
output_O_heightnum = 5
output_O_startoff = 200

# S for single
output_S_f2f_itv_sec = 4 #sec

output_S_heightnum = 3
output_S_widthnum = 4

# g for global constant for output
output_g_start_off = 200
output_g_end_off = 200

def youtube_demoer( video_path,img_saving_root ):
    vr = VideoReader(video_path, ctx = cpu(0))
    if( len(vr) <1000 ):
        print('too small')
        return None
    frame_rate = vr.get_avg_fps()
    output_S_f2f_itv = output_S_f2f_itv_sec * frame_rate # change sec to frames
    videobasename = os.path.basename( video_path ).split('.')[0]
    img_saving_path = f'{img_saving_root}/{videobasename}'
    os.makedirs(img_saving_path, exist_ok=True)
    

    
    output_O_frame_idx = np.linspace( output_g_start_off , len(vr)-output_g_end_off , output_O_widthnum * output_O_heightnum )//1
    def draw_time(frame, time_second, x, y, color= (0, 0, 255) , thickness=2, size=1,):
        cv2.putText(
            frame, strftime("%H:%M:%S", gmtime(time_second)), (int(x), int(y)), 
                cv2.FONT_HERSHEY_SIMPLEX, size, color, thickness)
        return frame

    def O_concatenating(im_list_2d):
        return cv2.hconcat([cv2.vconcat(im_list_h) for im_list_h in im_list_2d])

    
    O_frames = vr.get_batch(output_O_frame_idx).asnumpy() #get video
    img_height, img_width , _ = O_frames[0].shape # get usual width and height

    #output to single images
    output_S_frame_idc = [output_S_f2f_itv*np.arange(-output_S_heightnum//2+1 
                                                    , output_S_heightnum//2+1,1)
                        ]*len(output_O_frame_idx)
    output_S_frame_idc = [ output_S_frame_idc[idx]+value for idx,value in enumerate(output_O_frame_idx)]
    output_S_frame_seconds =  [ value/frame_rate for idx,value in enumerate(output_S_frame_idc)]
    S_frames = [ vr.get_batch(values).asnumpy() for values in output_S_frame_idc ]  
    S_frames_suitable = [ [cv2.cvtColor(img,cv2.COLOR_RGB2BGR) for img in img_seq ] for img_seq in S_frames]

    output_S_frames = []
    count = 0
    output_file_path_list = []
    for idx0 , img_seq in enumerate(S_frames_suitable):
        if(idx0 % output_S_widthnum != output_S_widthnum-1):
            output_S_frames.append( [draw_time(img , output_S_frame_seconds[idx0][idx1],0,img_height-3) 
                                for idx1, img in enumerate( img_seq ) ] )
        else:
            output_S_frames.append( [draw_time(img , output_S_frame_seconds[idx0][idx1],0,img_height-3) 
                                for idx1, img in enumerate( img_seq ) ] )
            
            output_S_path = strftime(f"{img_saving_path}/%H_%M_%S.jpg", gmtime(output_S_frame_seconds[idx0][0])
                                                )
            print(f"{img_saving_path}/%H_%M_%S.jpg")
            cv2.imencode('.jpg',O_concatenating(output_S_frames) )[1].tofile(output_S_path )
            count = count+1
            output_S_frames = []
            output_file_path_list.append(output_S_path)
            
    if(output_S_frames != []):
        output_S_path = f"{img_saving_path}/999.jpg"
        cv2.imencode('.jpg',O_concatenating(output_S_frames) )[1].tofile( output_S_path )
        output_file_path_list.append(output_S_path)
    return output_file_path_list
