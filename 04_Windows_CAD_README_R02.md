# 새 Windows PC 저장 경로 / R02 4봉 변형안

프로젝트 최상위 폴더는 다음입니다.

```text
C:\Users\yeonseo kim\Desktop\MOF_SDL\Hardware\CAD
```

이 폴더 안에 `Modules`, `01_requirements_cad_R02.txt`, `02_Setup_CAD_Windows_R02.bat`, `03_Build_CAD_Windows_R02.bat`가 바로 위치하도록 압축을 푸세요. ZIP 파일명 폴더가 한 겹 더 생겼다면 그 안의 내용을 CAD 폴더로 옮깁니다. 폴더 이름의 공백은 지원합니다.

1. Python 3.12와 Python launcher(`py`)를 설치합니다.
2. 처음 한 번 `02_Setup_CAD_Windows_R02.bat`를 실행합니다.
3. `03_Build_CAD_Windows_R02.bat`로 STEP/PNG를 생성합니다.
4. FreeCAD·Fusion 등에서 생성된 `.step` 파일을 열어 회전·확대·측정합니다.

새 산출물 위치:

```text
C:\Users\yeonseo kim\Desktop\MOF_SDL\Hardware\CAD\Modules\01_Sonicator_Rack_Guide\03_Preview\03_Rack_Guide_4Rod_R02
```

소스는 `Modules/01_Sonicator_Rack_Guide/02_Work/03_Rack_Guide_4Rod_R02`의 Python과 `parameters.py`입니다. mm/Y수직 좌표계입니다. 치수를 바꾸고 Python을 재실행하면 STEP을 다시 만듭니다. 일반 CAD 프로그램이 이 CadQuery Python 파일을 그대로 실행하는 것은 아닙니다. STEP에는 CadQuery의 원래 파라미터/피처 이력이 그대로 전달되지는 않습니다.

실행 파일은 자기 위치를 기준으로 이동하고 Python은 `__file__`을 기준으로 경로를 계산하므로 PC가 바뀌어도 다른 경로를 일일이 고칠 필요가 없습니다. 서버의 `/workspace` 경로는 Windows에 입력하지 않습니다. 그림 캐시도 고정 Linux 경로 대신 OS 임시 폴더를 사용합니다.

Windows 배치 파일은 작성·검토했으나 이 Linux 서버에서 Windows 실행을 실제 검증하지는 못했습니다. 같은 Python 생성 소스는 서버에서 실행하여 CAD를 검사했습니다. FreeCAD 등 CAD 뷰어 설치는 별도입니다.

첨부 AGENTS/harness 원본은 References에 보존했습니다. 원 프로젝트의 revision router는 여전히 미첨부이며 해당 prepare/check가 통과한 상태는 아닙니다. 기존8봉/랙 R02는 보존하고 이번4봉/랙 안은 별도 family 폴더로 구분했습니다. 현재 세션은 Windows PC에 직접 접근해 파일을 저장하지 못하며, GitHub 업로드가 완료되었습니다. Downloads/Sonicator_R02_4Rod_Windows.zip에서 패키지를 받을 수 있습니다.

## 최신: 각 변 중앙 4봉 비교안

사용자가 각변중앙 배치를 요청하여 별도 Centered4 family를 추가했습니다. 이 안을 생성하려면 `05_Build_CAD_Centered4_R02.bat`를 실행합니다. 기존 `03_Build_CAD_Windows_R02.bat`는 이전 엇갈린4봉안을 재생성합니다. 설치는 동일한02Setup을사용합니다.

중앙배치 출력은 `Modules/01_Sonicator_Rack_Guide/03_Preview/04_Rack_Guide_Centered4_R02`입니다. 회전위치정밀도가약한배치이므로 로봇반복픽업을보장하는최종설계로간주하지않습니다.
