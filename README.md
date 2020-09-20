# Version

LFW_Movie 포크

BETA

# K-Movie.bundle

Plex 기본 에이전트에서 제공하는 리뷰 / 트레일러 / 부가영상 제공

TMDb와 부분 통합


APIKEY 발급을 위해서는 디스코드 필수

https://discord.gg/6p5rew

# 왓챠와 부분 통합 및 부분 서칭 가능

![image](https://user-images.githubusercontent.com/70357228/93386067-1e011800-f8a2-11ea-8776-a67f750ea488.png)

![image](https://user-images.githubusercontent.com/70357228/93386010-075ac100-f8a2-11ea-9dda-3657ef5ce376.png)

# 다수선택 기능

![image](https://user-images.githubusercontent.com/70357228/93378291-3455a680-f897-11ea-8ece-730de54c2b72.png)

파일네임에 매칭됨.


# 서버에 본인 라이브러리 백업 가능


![image](https://user-images.githubusercontent.com/70357228/93432220-2daf4980-f900-11ea-8823-ae0423482bff.png)


파일 이름(EX : Return of Daimajin 1966 BluRay 720p x264 AAC-Shiniori.mp4) 에 기반하여 매핑된 메타데이터 ID를 서버에 저장하고, 다음 라이브러리를 구성할 때 불러올 수 있음.

APIKEY 기반이라 다른 서버에서도 그대로 적용 가능.

해당 기능은 똑같은 라이브러리를 여러 서버에 구축할 때 유용하게 사용되리라 예상.


# 다양한 기능들

## TMDb 컬렉션

## 왓챠 컬렉션

## 왓챠 평론가 평론 (Official_user == True)

## 왓챠 컬렉션 블랙리스트

## 왓챠 개인별 점수 컬렉션화

## 평론가 블랙리스트

## 네이버 평론가 크롤

## 평론가 점수가 특정 점수 이하이면 로튼 토마토 표기

## 링크 기반 예고편 및 부가영상 스트리밍

## 왓챠 및 TMDb에서도 검색 가능. IMDb는 부분적으로만 지원.


# 왓챠 쿠키 얻는 법

![image](https://user-images.githubusercontent.com/59600370/88553501-50d81e00-d060-11ea-9eb1-b0d99f0935b2.png)

크롬 개발자모드(F12) 들어가셔서 Network 들어가신 후 찾으시면 됩니다.

## 자세한 왓챠 쿠키 얻는 법

1) https://pedia.watcha.com/ko-KR/contents/m5ewr3z 해당 페이지에 들어갑니다. 로그인이 되어있어야만 합니다.

2) F12를 누릅니다.

3) Network 탭에 들어갑니다.

![image](https://user-images.githubusercontent.com/59600370/88563497-01e4b580-d06d-11ea-8739-83680229b0eb.png)

4) Name 탭에 m5ewr3z 항목을 찾습니다.

5) 오른쪽 탭(Headers)에서 Requests Headers 항목에서 cookie 값을 복사한 뒤 설정에 붙여넣습니다.

# FAQ

## 에이전트가 나타나지 않습니다.

.xml 파일이 형성되지 않은 것으로 보입니다.

에이전트 > 영화 > The Movie Database 에이전트에 들어간 후 아래에 나타나는 LFW Movie 옆 톱니바퀴를 눌러 .xml 파일을 생성해 줍니다.

![image](https://user-images.githubusercontent.com/59600370/89057836-4471ff00-d399-11ea-9288-a43c2da0ce96.png)

그리고 PMS 를 재시작하면 영화 에이전트 내에서 LFW Movie 에이전트가 나타납니다.



## 설정이 저장되지 않습니다.

이는 한글 때문에 저장이 되지 않는 것입니다.

xml 파일을 직접 수정해주시면 됩니다.

윈도우를 기준으로 아래의 경로에 존재합니다.

![image](https://user-images.githubusercontent.com/59600370/89057975-73887080-d399-11ea-9d0c-19c83e298f9f.png)

파일을 열어서 수정하시면 됩니다.


![image](https://user-images.githubusercontent.com/59600370/89058056-9a46a700-d399-11ea-87e7-5da6a17afd6e.png)

아래와 같은 규칙으로 되어있으니, 구분자에 맞게끔 원하는 대로 수정하시길 바랍니다.



# Thanks to

Soju6jan
