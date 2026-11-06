# R02 — 두 랙 / 두 독립 상판

01: 제조사 포함 컬러 조립 STEP
02: 좌측 프레임 모듈만 (랙/바이알/소니케이터 제외)
03: 우측 프레임 모듈만 (랙/바이알/소니케이터 제외)
04: 전체 등각도 PNG
05: 치수와 봉배치 상면도 PNG
06: 수위·간극 측면도식 PNG
07: 실제 CAD 수치 검사 JSON
08: 소니케이터를 숨긴 치구 등각도 PNG
09: 설계 근거/가정/미확정 사항
11: 검증 기록

CadQuery/numpy/matplotlib이 설치된 Python에서, 압축해제한폴더 기준:
```
python3 01_Sonicator_Rack_Guide/02_Work/02_Rack_Guide_R02/01_build_Preview_R02.py
```
이 R02 Preview를재생성한다. 후속변경은R03 등새revision으로보존한다. 원프로젝트routing도구로통합해야하며본폴더는그검사를통과한상태가아니다.

Preview용STEP은FreeCAD/Fusion/SolidWorks등에서열수있다. 제조사원본은솔리드가아닌surface-shellreference이다. 다른부품은솔리드다. STEP기준mm/Y수직. STL은생성하지않았다.

첨부문서에대한원본은01_References의02~04파일이다. 이는입력당시의1랙배치지침도포함하며, 이번사용자수정요구에따른R02의2랙배치가우선한다.
