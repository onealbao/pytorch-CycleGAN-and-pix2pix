import glob
import os
from PIL import Image
import numpy as np
Image.MAX_IMAGE_PIXELS = None
import sys
import math
import cv2

def mask_mxif(sample_id,marker):
    workdir = '/mnt/1T/baos1/GCA/data/MXIF/cyclegan/'
    
    
    tissue_mask = cv2.imread('%s/%s_TISSUE_MASK.tif' % (workdir,sample_id),cv2.IMREAD_GRAYSCALE)
    tissue_mask[tissue_mask == 0 ] = 0
    tissue_mask[tissue_mask == 255] = 1
    
    img = cv2.imread('%s/%s_%s.tif' % (workdir,sample_id,marker))
    img_masked = cv2.bitwise_and(img,img,mask = tissue_mask)
    cv2.imwrite('%s/%s_%s_masked.tif' % (workdir, sample_id,marker),img_masked)
      
def resize_mxif_to_ihe_space(x_size,y_size,sample_id,marker):
    workdir = '/mnt/1T/baos1/GCA/data/MXIF/cyclegan/'
    workdir_mxif_resize = '/mnt/1T/baos1/GCA/data/MXIF/cyclegan/mxif_in_ihe_space/'
    he_dim = 0.5036
    print(sample_id)
#     sample_id = 'GCA002ACB'
#     img = cv2.imread('%s/%s_ALL.tif' % (workdir,sample_id))
    img = cv2.imread('%s/%s_%s_masked.tif' % (workdir,sample_id,marker))
    h,w,dim = img.shape
    dim = (int(w * x_size/he_dim), int(h * y_size / he_dim))

    # resize image
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    cv2.imwrite('%s/%s_%s_masked_IN_IHE.tif' % (workdir_mxif_resize,sample_id,marker),resized)
    
    
def roi_MXIF(sample_id,marker,x,y,w,h):
    print(sample_id)
    target_dir = '/mnt/1T/baos1/GCA/data/MXIF/cyclegan/mxif_in_ihe_space/roi'
#     img = cv2.imread('/mnt/1T/baos1/GCA/data/MXIF/cyclegan/cropped_ihe_one_third/GCA002ACB_IHE_cropped.tiff')
    img = cv2.imread('/mnt/1T/baos1/GCA/data/MXIF/cyclegan/mxif_in_ihe_space/%s_%s_masked_IN_IHE.tif' % (sample_id,marker))

    img_to_save = img[y:y+h,x:x+w,:]
    cv2.imwrite('%s/%s_%s_masked_IN_IHE_ROI.tif' % (target_dir,sample_id,marker),img_to_save)

def crop256_MXIF(sample_id,marker,w,h):
    src_dir = '/mnt/1T/baos1/GCA/data/MXIF/cyclegan/mxif_in_ihe_space/roi'
    target_dir = '%s/crop256' % src_dir
    #print('Number of arguments:%s' % sys.argv[1])
    raw_img_path = '%s/%s_%s_masked_IN_IHE_ROI.tif' % (src_dir,sample_id,marker)
    print(raw_img_path)
    # raw_img_name = sys.argv[2]
    # w = 7956
    # h = 5292
    roundup_w = math.ceil(w/256)#int(sys.argv[3])
    roundup_h = math.ceil(h/256)#int(sys.argv[4])

    img = Image.open(raw_img_path)#.convert('RGB')
    img_cropped_zero_padding = img.crop((0, 0, 256* roundup_w, 256*roundup_h ))

#     save_image_path = '%s/%s_ALL_IN_IHE_ROI_crop256.tif' % (target_dir,sample_id)
    save_image_path = '%s/%s_%s_masked_IN_IHE_ROI_crop256.tif' % (target_dir,sample_id,marker)
    img_cropped_zero_padding.save(save_image_path, 'TIFF')
    
def split_MXIF(sample_id,patch_size, marker_list):    
    src_dir = '/mnt/1T/baos1/GCA/data/MXIF/cyclegan/mxif_in_ihe_space/roi/crop256'
    
    
    imgs = []
    for marker in marker_list:
        suffix = '%s_masked_IN_IHE_ROI_crop256' % marker
        raw_img_path = '%s/%s_%s.tif' % (src_dir,sample_id,suffix) 
        img = Image.open(raw_img_path)
        imgs.append(img)
        break
    
    w,h = imgs[0].size
#     img = Image.open(raw_img_path)
    w,h = img.size

    xUpper = math.ceil((w)/patch_size)
    #yUpper = math.ceil((h-500)/patch_size)
    yUpper = math.ceil(h/patch_size) # no need to minus 500...
    # for i in range (0,curX-1):
    #     for j in range (0,yUpper-1):
    for i in range (0,xUpper):
        print('i:%d' % i)
        for j in range (0,yUpper):
            print('j:%d' % j)
            tmp_img_list = []
            
            for marker in marker_list:
                suffix = '%s_masked_IN_IHE_ROI_crop256' % marker
                raw_img_path = '%s/%s_%s.tif' % (src_dir,sample_id,suffix) 
                img = Image.open(raw_img_path)
            
            
            
            
#             for img in imgs:
#                 #start point = (0,0)
                curX = 0 + i * patch_size
                curY = 0 + j * patch_size
                targetX = curX + patch_size
                targetY = curY + patch_size
                img_cropped = img.crop((curX, curY, targetX, targetY))
                tmp_img_list.append(img_cropped)
        
            imgs_comb = np.hstack((np.asarray(train_img) for train_img in tmp_img_list ) )

            raw_img_path = '%s/%s_%s.tif' % (src_dir,sample_id,marker)
            tmp_file_name = '%s/patch/%s/%s_ALL_CHANNEL_%s_%s.png' % (src_dir,sample_id,sample_id,i,j) 
            imgs_comb = Image.fromarray( imgs_comb)
            imgs_comb.save( tmp_file_name, 'PNG')            
            
marker_list = ['ACTG1','ACTININ','BCATENIN','CD11B','CD20','CD3D','CD45','CD4','CD68','CD8','CGA','COLLAGEN','DAPI','ERBB2','FOXP3','HLAA','LYSOZYME','MUC2','NAKATPASE','OLFM4','PANCK','PCNA','PEGFR','PSTAT3','SMA','SOX9','VIMENTIN']

# sample_list=['GCA002ACB']
# preprocess_ALL(sample_list,marker_list)


nested_dict2 = {'GCA012TIB': {'x_size':0.32431067048081824 ,'y_size':0.32411197154821314,'x':1026,'y':1970,'w':3084,'h':2178}}



def preprocess_ALL2(sample_list,marker_list):
    for sample_id in sample_list:
        for marker in  marker_list:
            print(marker)
            mask_mxif(sample_id,marker)
#             resize_mxif_to_ihe_space(x_size,y_size,sample_id,marker)
            resize_mxif_to_ihe_space(nested_dict2[sample_id]['x_size'] ,nested_dict2[sample_id]['y_size'],sample_id,marker)
#             roi_MXIF(sample_id,marker,x,y,w,h)
            roi_MXIF(sample_id,marker, nested_dict2[sample_id]['x'],nested_dict2[sample_id]['y'],nested_dict2[sample_id]['w'],nested_dict2[sample_id]['h'])
#             crop256_MXIF('GCA002ACB', 7956, 5292)
            crop256_MXIF(sample_id,marker, nested_dict2[sample_id]['w'],nested_dict2[sample_id]['h'])
    
        patch_size = 256
        split_MXIF(sample_id,patch_size, marker_list)
        
*sample_list, = nested_dict2
preprocess_ALL2(sample_list,marker_list)
