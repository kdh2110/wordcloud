# 워드클라우드 · HTML 중심 간소화 수정본

남색 제목 영역 오른쪽의 **내 파일로 워드클라우드 만들기** 버튼으로 파일 선택창을 엽니다. 분석이 완료되면 현재 워드클라우드·논문 목록이 새 결과로 바뀝니다. 화면 탭이나 Streamlit 업로더/팝업/설정 위젯을 사용하지 않습니다.

## 파일 구성

실제 기능을 수정할 핵심 코드는 세 파일입니다.

| 파일 | 역할 |
| --- | --- |
| `app.py` | 서버의 파일 확인·작업 관리·화면 연결 |
| `pipeline.py` | 코랩과 웹사이트에서 함께 사용하는 분석 엔진 |
| `ui/index.html` | 공통 HTML 화면, 제목 오른쪽 버튼, 파일 선택·설정창 |

그 외 `requirements.txt`, `packages.txt`, `.streamlit/config.toml`은 배포 설정이고, `sample_report.html`은 기본 화면용 샘플입니다. 별도 JavaScript 빌드나 npm 설치는 필요 없습니다. 안내서까지 ZIP 안의 파일은 총 8개입니다.

## 기존 GitHub에 적용

1. ZIP을 풀고 `wordcloud_streamlit_v9` **폴더 안의 내용**을 기존 저장소의 app.py와 같은 위치에 업로드합니다. `ui`와 `.streamlit` 폴더도 함께 올려주세요.
2. 기존 **report.html은 그대로 유지**하세요. 공개 결과 데이터 파일은 이번 ZIP에 넣지 않았습니다. 파일이 없을 때만 100건 샘플을 표시합니다.
3. 같은 이름의 파일은 교체합니다. 이전 버전의 `builder.py`, `viewer.py`, `worker.py`, `jobs.py`, `excel_io.py`, `explorer_template.html`, `report_component/`는 더 이상 사용하지 않으므로 GitHub에서 삭제해도 됩니다.
4. Streamlit 실행 파일은 `app.py`, Python은 3.12입니다. Commit 후 앱 반영을 기다리고 필요한 경우 Reboot app을 실행합니다.

새 저장소에 올리는 경우에도 같은 구성으로 올린 뒤 https://share.streamlit.io 에서 저장소/브랜치/app.py를 선택해 배포합니다. 실제 계정에 직접 배포한 패키지는 아닙니다.

## 사용하는 방법 · 선택 항목 간소화

1. 제목 오른쪽 **내 파일로 워드클라우드 만들기**를 누르고 원본 논문 Excel(.xlsx)을 선택합니다.
2. 필요한 경우 **분석 설정**에서 제목·초록·저자키워드 가중치, 인용 반영 강도, 색상, 추가 제외 표현만 조정합니다.
3. **분석 시작**을 누르면 전체 논문을 분석하고 같은 화면에 새 결과를 표시합니다.

고정값은 **최대 50개 표현 / 이미지 가로 1200 × 세로 800 / 기본 색상 Dark2**입니다. 추출 기준을 통과한 표현이 50개보다 적거나 배치 공간이 부족하면 실제 표시 개수는 더 적을 수 있습니다.

시트·열·구분자 선택 화면, 분석 범위·단어 수 설정, 피인용 수집일, 자동 후보·이미지 상세 설정, 서지정보 열 확인 화면을 제거했습니다.

- 시트: 첫 행에서 제목·초록·저자키워드 열을 찾을 수 있는 **첫 번째 시트**를 자동으로 사용합니다. 여러 시트를 합치지는 않습니다. 여러 후보가 있으면 선택된 시트명을 안내합니다.
- 열: Scopus/영문·한국어의 알려진 열 이름을 자동으로 연결합니다. 필수 열을 못 찾으면 오류 안내와 함께 멈춥니다. 열의 위치만 보고 임의로 해석하지 않습니다.
- 저자키워드 구분자: 처음 300행에서 세미콜론·세로줄·줄바꿈을 우선 확인하고, 이들이 없으면 쉼표를 사용합니다. 괄호 안의 구분자는 탐지에서 제외합니다. 이는 자동 추정이므로 특이한 용어 안의 쉼표나 혼합 구분자가 있는 자료는 세미콜론 형식으로 정리하면 더 안정적입니다.
- 피인용 열이 없으면 인용 가중치를 적용하지 않는다는 안내가 표시됩니다.
- 기존 후보 발굴 기준(빈도5 / 논문수3 / PMI3)과 이미지 최소 논문수2는 내부 기본값으로 유지합니다.

PNG·논문 목록 CSV·분석 Excel 다운로드는 그대로 사용할 수 있습니다. 파일 선택 화면을 간소화한 변경이며 기존 공개 `report.html`의 분석 값이나 이미지 자체는 다시 계산하지 않습니다. 공개 이미지도 Dark2·1200×800으로 바꾸려면 새 설정으로 분석한 HTML로 교체해야 합니다.

## 코랩과의 일치 범위

`pipeline.py`는 같은 `ui/index.html`에서 결과 HTML을 만듭니다. 따라서 코랩에서도 **같은 분석 엔진·같은 화면 템플릿**을 사용합니다.

- 원본 자료, 시트/열, 분석 범위, 가중치, 후보 기준, 제외 표현, 라이브러리/모델 버전이 같으면 동일한 점수·논문 연결을 계산합니다.
- 웹사이트와 기존에 별도로 수정한 Colab 코드의 사전·불용어·정규화 규칙이 다르면 결과가 달라집니다. 같은 pipeline.py로 맞춰야 합니다.
- 워드클라우드 배치까지 같게 하려면 폰트 파일과 이미지 설정도 같아야 합니다.
- 코랩에서 다운로드한 HTML은 서버 없이 열람·검색·단어 클릭·PNG/CSV 저장이 됩니다.
- **HTML 파일 단독으로 Python/spaCy/KoNLPy 분석을 실행할 수는 없습니다.** 저장된 HTML에서 만들기 버튼을 누르면 ‘새 파일 분석은 배포된 웹사이트에서 이용’ 안내가 나옵니다. 웹사이트에서만 파일 업로드→분석이 연결됩니다.

Streamlit은 파일 전송·Python 실행·세션 연결을 맡습니다. 화면은 표준 HTML/CSS/JavaScript로 만들었지만, 이 배포 패키지가 Streamlit 의존성을 완전히 제거한 것은 아닙니다.

## 코랩 실행 예시

ZIP을 `/content`에 업로드하고 압축을 푼 뒤 다음과 같이 실행합니다. 코랩에 이미 설치한 버전이 다르면 설치 후 런타임 재시작이 필요할 수 있습니다.

```python
# 셀 1 · 설치 (ZIP이 /content에 있는 경우)
!unzip -o /content/wordcloud_streamlit_v9.zip -d /content
!apt-get -qq update
!apt-get -qq install -y default-jre-headless fonts-nanum libgomp1
!pip -q install -r /content/wordcloud_streamlit_v9/requirements.txt
```

```python
# 셀 2 · 원본 Excel 업로드 및 분석
from google.colab import files
from pathlib import Path
import sys, importlib

sys.path.insert(0, '/content/wordcloud_streamlit_v9')
import pipeline as p
importlib.reload(p)

uploaded = files.upload()  # 원본 논문 Excel 1개 선택
input_path = next(name for name in uploaded if name.lower().endswith('.xlsx'))

# Scopus 예시: 웹사이트에서 고른 열/설정과 동일하게 지정
p.SHEET_NAME = 0
p.TITLE_COL = 'Title'
p.ABSTRACT_COL = 'Abstract'
p.KEYWORD_COL = 'Author Keywords'
p.CITATION_COL = 'Cited by'  # 열이 없으면 None, p.CITATION_ALPHA=0
p.TITLE_WEIGHT = 5.0
p.ABSTRACT_WEIGHT = 1.0
p.KEYWORD_WEIGHT = 5.0
p.CITATION_ALPHA = 0.5
p.WORDCLOUD_MAX_WORDS = 50
p.WORDCLOUD_WIDTH = 1200
p.WORDCLOUD_HEIGHT = 800
p.WORDCLOUD_COLORMAP = 'Dark2'
p.EXCLUDE_GENERIC_PHRASES.update({'south korea'})
p.WORDCLOUD_FONT_PATH = '/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf'

out = p.run(input_path, mode='full', output_dir='/content/results', cache_dir='/content/cache')
# 웹사이트와 동일하게 전체 논문을 분석합니다.
files.download(str(out / 'paper_explorer.html'))
files.download(str(out / 'analysis.xlsx'))
```

코랩에서 피인용 열이 없다면 `p.CITATION_COL=None`, `p.CITATION_ALPHA=0.0`, `p.RANKING_VERSION='no_idf'`로 지정합니다. 사용자 파일의 열 이름이 예시와 다르면 실제 열 이름으로 바꾸세요.

## 결과 파일과 운영

분석 출력은 기존처럼 **Excel 1개 + HTML 1개 + 네 가지 조건 PNG**입니다. 별도 JSON·placement 파일과 추가 결과 ZIP은 만들지 않습니다. PNG 생성에 실패한 조건은 HTML에 경고를 표시합니다. 내부 캐시와 작업 기록은 임시 폴더에 분리됩니다.

기본 가중치는 제목5/초록1/저자키워드5, 인용 강도 α=0.5입니다. 인용 점수는 논문별 필드 기여점수×(1+α×ln(1+피인용횟수))의 합계입니다. IDF 적용/미적용도 비교할 수 있습니다. 분석 로직은 v8 기반을 유지합니다.

동시 분석은 기본 1건입니다. 다른 작업 중에는 잠시 후 재시도하라는 안내가 나타납니다. 업로드 최대 50MB, 기본 작업 시간 1시간, 검사 최대 50,000행입니다. 완료된 작업이 24시간 접근되지 않으면 앱이 실행 중일 때 정리됩니다. 브라우저 새로고침/서버 재시작으로 세션이 끊길 수 있으므로 필요한 결과는 다운로드하세요. 무료 서버에서 8,000건 전체의 처리 완료를 보장하지는 않습니다.

## 화면 수정 위치

`ui/index.html`의 `<!--BEGIN_REPORT-->`와 `<!--END_REPORT-->` 사이가 코랩·웹 공통 화면입니다.

- `#wc-create`: 오른쪽 만들기 버튼
- `#wc-modal`: 일반 HTML 파일 선택·설정 창
- `wc-native-script`: 파일 확인·분석 요청과 진행 상태 표시
- 파일 끝의 짧은 스크립트: Streamlit과 HTML 사이의 연결

## 검증

실제 브라우저에서 삭제된 선택 항목이 없는지, Dark2가 기본인지, 100건 전체 분석과 같은 화면 결과 교체가 되는지 확인했습니다. 다운로드한 PNG의 크기 1200×800, CSV 다운로드와 결과 삭제도 확인했습니다. 서버 설정이 단어 수50·전체 분석으로 고정되는지, 시트·열·구분자 자동 인식 및 기존 HTML의 선택창 갱신도 검사했습니다.
