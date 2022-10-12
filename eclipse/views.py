#Render module to reder web pages
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import os
from PIL import Image #PIL module
import random
from zipfile import ZipFile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def gencode(x):
    code=''
    for i in range(3):
        code+=str(chr(random.randint(97,122)))
    if x==1:
        code="f"+code
    elif x==2:
        code="n"+code
    return code

full_path=''
media_path=''
data=''
#CONVERSION TO BINARY
def gendata(data):
    newdata=[] #list of binary of each bit of data
    for i in data:
        newdata.append(format(ord(i),"08b"))
    return(newdata)

#MODIFICATION OF EACH PIXEL
def modPix(pix,data):
#even for 0,odd for 1
#8th bit for data end 0-continue,1-end
    datalist=gendata(data)
    lendata=len(datalist)#total bits
    imdata=iter(pix)#pixel numeric data

    for i in range(lendata):
        #Extracting 3 pixels per iteration
        #[:3] for...if more bits in pixel
        pix=[value for value in imdata.__next__()[:3]+imdata.__next__()[:3]+imdata.__next__()[:3]]

        for j in range(0,8):
            if (datalist[i][j]=='0') and (pix[j]%2!=0):
                pix[j]-=1
            elif (datalist[i][j]=='1') and (pix[j]%2==0):
                pix[j]-=1
        #8thbit
        if i==lendata-1:
            if pix[-1]%2==0:
                pix[-1]-=1
        else:
            if pix[-1]%2!=0:
                pix[-1]-=1
        pix=tuple(pix)
        yield pix[0:3]
        yield pix[3:6]
        yield pix[6:9]

#ENCODE MODIFIED PIXELS INTO NEW IMAGE
def encode_img(newimage,data):
    w=newimage.size[0]
    x=0
    y=0
    for pixel in modPix(newimage.getdata(),data):
        newimage.putpixel((x,y),pixel)
        #To chanege row
        if x==w-1:
            x=0
            y+=1
        else:
            x+=1

#DECODE DATA
def decode(i):
    image=Image.open(i,'r')
    d_data=''
    imgdata=iter(image.getdata())
    while True:
        pix=[value for value in imgdata.__next__()[:3]+imgdata.__next__()[:3]+imgdata.__next__()[:3]]
        #String of binary
        bin=''
        for i in pix[0:8]:
            if i%2==0:
                bin+='0'
            else:
                bin+='1'
        d_data+=str(chr(int(bin,2)))
        if pix[-1]%2!=0:
            return d_data

#ENCODE DATA
def encode(i,d,n):
    image=Image.open(i,"r")
    data=d
    newimage=image.copy()
    encode_img(newimage,data)
    newimage.save(n,str(n.split(".")[1].upper()))

def home(request):
    return render(request,'home.html')

def imageselection(request):
    return render(request,'imageselection.html')

def encodepage(request):
    global full_path
    global media_path
    if request.method=='POST':
        uploaded_file=request.FILES['document']
        fs = FileSystemStorage()
        fs.save(uploaded_file.name,uploaded_file)
        media_path = os.path.join(BASE_DIR,'media')
        full_path=os.path.join(media_path,uploaded_file.name)
    return render(request,'encode.html')

def check(request):
    global full_path
    global media_path
    global data
    if request.method=='POST':
        uploaded_file=request.FILES['document']
        fs = FileSystemStorage()
        fs.save(uploaded_file.name,uploaded_file)
        media_path = os.path.join(BASE_DIR,'media')
        full_path=os.path.join(media_path,uploaded_file.name)
        data=decode(full_path)
        if len(data)<4:
            error="No Data Found!!"
            return render(request,'nnf.html',{'error':error})
        else:
            return render(request,'check.html')

def decodepage(request):
    global full_path
    global media_path
    if request.method=="POST":
        d=request.POST
        if d['check']!=data[0:4]:
            error="Incorrect Code!!"
            return render(request,'nnf.html',{'error':error})
        else:
            d_message=data[4:]
            if data[0]=='n':
                fs="disabled"
                return render(request,'decode.html',{'d_message':d_message,'fs':fs,'filess':"No Decoded File"})
            else:
                file_name=full_path
                with ZipFile(file_name,'r') as zip:
                    zip.extractall(media_path)
                filename=zip.namelist()[0]
                fs=""
            return render(request,'decode.html',{'d_message':d_message,'filename':filename,'fs':fs,'filess':"Download Decoded File"})
            
def authcode(request):
    global full_path
    global media_path
    if request.method=='POST':
        d=request.POST
        if len(d['newname'])==0:
            nn='noname'
        else:
            nn=d['newname']
        newname=str(nn)+".png"
        new_path=media_path+'/'+str(nn)+'.png'
        if d['status']=='N':
            code=gencode(2)
            m=code+d['message']
            encode(full_path,m,new_path)
        if d['status']=='Y':
            code=gencode(1)
            m=code+d['message']
            uploaded_file=request.FILES['enfile']
            fs = FileSystemStorage()
            fs.save(uploaded_file.name,uploaded_file)
            media_path_file = os.path.join(BASE_DIR,'media')
            full_path_file=os.path.join(media_path_file,uploaded_file.name)
            temp=media_path+'/'+str(nn)+'1.png'
            encode(full_path,m,temp)
            ziploc=media_path+"/zip.zip"
            with ZipFile(ziploc,'w') as zip:
                zip.write(full_path_file)
            out = open(new_path, "wb")
            out.write(open(temp, "rb").read())
            out.write(open(ziploc, "rb").read())
            out.close()
    return render(request,'authcode.html',{'code':code,'newname':newname})
