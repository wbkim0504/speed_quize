# Speed Quiz 
```
author : Wonbae Kim
date : 2020.3.22
```
****

# How to install

## glfw 설치
```
sudo apt install glfw (X)
-> shared library가 설치가 안됨
-> 소스로 설치할것
```

## glfw 소스로 설치
```
소스 다운로드 -> git clone https://glfw/glfw
CMakeLists.txt 에서 shared option을 ON으로 변경
```

## 필요 라이브러리 설치
```
sudo apt install libxinerama-dev libxcursor-dev libxi-dev
```

## OpenGL 설치
```
sudo pip install PyOpenGL PyOpenGL_accelerate
```

## freetype 설치
```
sudo pip install freetype-py
```

---
## Windows 설치
```
- Python 을 인터넷에서 다운받아서 설치한다. (windows 에서는 anaconda를 설치한다.)  
https://www.anaconda.com/distribution/

- Python 2.7 버전을 설치한다. (64-bit)  
설치후 anaconda cmd 창에서 python 명령 실행

- Visual C++ Compiler for Python 2.7을 설치한다. (PyOpenGL 컴파일에 필요)  
Aka.ms/vcpython27 로 접속해서 설치 프로그램을 다운받는다.  
VCForPython25.msi 설치

- PyOpenGL을 설치한다.  
python –m pip install PyOpenGL PyOpenGL-accelerate  

- mpu_monitoring 실행에 필요한 python 모듈을 설치한다.  
python –m pip install glfw  
python –m pip install freetype-py  

- speed_quiz 설치 디렉토리로 이동하여 qz_main 을 실행한다.  
python qz_main.py
```

