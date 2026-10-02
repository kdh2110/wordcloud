# 논문 워드클라우드 홈페이지 v9

기존 v8 결과를 바로 보여주는 홈페이지에 **내 파일로 워드클라우드 만들기** 탭을 추가했습니다.

## 바뀐 내용

- 화면 상단: Streamlit 고정 메뉴와 겹치지 않도록 본문 위쪽 여백을 4.5rem으로 조정했습니다.
- HTML 버튼: 관련도순/피인용순 선택과 리스트·이미지 다운로드를 글자 12px, 높이 30px로 통일했습니다. 기존 v8 report.html에도 자동 적용합니다.
- 기존 결과 보기: 관리자 report.html을 표시합니다. 파일이 없으면 명시적으로 표시된 100건 샘플을 보여줍니다.
- 내 파일로 워드클라우드 만들기: 이용자가 원본 Excel을 업로드하고 분석하면 같은 사이트에서 결과를 탐색할 수 있습니다.
- 각 결과 화면에서 현재 조건의 워드클라우드 PNG와 검색·필터·정렬을 적용한 논문 목록 CSV를 각각 다운로드할 수 있습니다. CSV는 현재 화면의 한 페이지만이 아니라 조건에 맞는 전체 목록입니다.
- 업로드 분석 결과에는 순위표 확인 및 Excel/HTML/이미지/ZIP 다운로드도 제공합니다.

## 지금 운영 중인 GitHub 저장소에 적용

1. ZIP을 풀고 `wordcloud_streamlit_v9` **폴더 안의 파일**을 기존 저장소의 `app.py`가 있는 위치에 업로드합니다. ZIP 자체를 올리는 것이 아닙니다.
2. 같은 이름은 새 파일로 교체하고, 새 파일도 모두 추가합니다. 특히 `builder.py`, `pipeline.py`, `worker.py`, `jobs.py`, `excel_io.py`, `viewer.py`, `explorer_template.html`, `requirements.txt`, `packages.txt`가 필요합니다.
3. **현재 운영 중인 `report.html`은 그대로 두세요.** 이번 ZIP에는 기존 결과를 덮어쓰지 않도록 `report.html`을 넣지 않았습니다. `sample_report.html`은 report.html이 없을 때만 쓰는 예시입니다.
4. `.streamlit/config.toml`도 새 파일로 교체합니다. 업로드 제한 50MB, 메시지 한도 200MB가 들어 있습니다. 숨김 폴더가 안 보이면 GitHub에서 Add file → Create new file → `.streamlit/config.toml` 경로로 만들고 내용을 붙여넣으세요.
5. GitHub에 Commit 후 Streamlit이 변경 사항과 추가 의존성을 반영할 때까지 기다립니다. 필요하면 앱 메뉴의 관리 화면에서 Reboot app을 실행합니다.
6. Python은 **3.12**, 실행 파일은 **app.py**를 사용합니다. 다른 Python 버전으로 운영 중이고 설치가 실패하면 Python 3.12로 다시 배포하세요.

`requirements.txt`에 spaCy 모델이, `packages.txt`에 Java와 한글 폰트가 들어 있습니다. **이전 표시 전용 버전의 app.py만 바꾸면 업로드 분석 기능은 동작하지 않습니다.** 전체 코드를 함께 업데이트하세요.

기존 별도 의존성 파일(uv.lock, Pipfile, environment.yml 등)이 있다면 이 패키지와 충돌하지 않도록 정리해야 합니다. Streamlit은 여러 의존성 파일을 모두 합쳐 읽지 않습니다.

## 처음 배포하는 경우

1. GitHub 저장소를 만들고 이 폴더 안의 파일을 저장소 최상위에 업로드합니다.
2. 실제 공개 결과가 있으면 v8에서 만든 `paper_explorer.html`을 `report.html`로 바꿔 같은 위치에 추가합니다.
3. https://share.streamlit.io → Create app → GitHub 저장소, 실제 브랜치, `app.py` 선택.
4. Advanced settings에서 Python 3.12 선택 후 Deploy.
5. 생성된 `https://....streamlit.app` 링크 공유. 누구나 볼 수 있게 하려면 공유 설정을 공개로 지정합니다.

현재 패키지는 배포용 파일입니다. 사용자 GitHub/Streamlit 계정에 실제 배포한 것은 아닙니다.

## 이용자 화면

처음 접속하면 **기존 결과 보기**가 선택되어 있습니다. 공개된 결과의 단어를 클릭해 논문을 볼 수 있습니다.

자신의 자료를 분석하려면:

1. **내 파일로 워드클라우드 만들기** 탭 선택.
2. 원본 논문 Excel(.xlsx) 업로드. 집계된 analysis.xlsx나 워드클라우드 순위표는 입력 자료가 아닙니다.
3. 시트와 제목·초록·저자키워드 열 확인. Scopus 등의 영문 열 이름도 자동으로 제안합니다. 피인용 횟수·저자·연도·저널명·DOI 등은 선택 항목입니다.
4. 필요한 경우 분석 설정에서 가중치, 제외 표현, 단어 수, 색상, 이미지 크기를 조정합니다.
5. **분석 시작** 클릭. 기본은 최대 100건 샘플이며, 전체 논문은 설정에서 **전체 논문**을 선택해야 합니다.
6. 완료되면 같은 탭에 클릭형 워드클라우드와 논문 목록이 나타납니다. 두 다운로드 버튼을 필요한 경우에만 누릅니다.

파일을 올리는 순간 자동 분석하지 않습니다. 열 지정과 설정 확인 후 분석 시작을 눌러야 합니다. 분석 중에는 진행 단계와 경과 시간이 표시되며 중지할 수 있습니다. 실패하면 오류를 표시합니다.

## 분석 설정과 점수

기존 로컬 업로드 앱의 v8 분석 엔진을 사용합니다. 이번 변경의 주목적은 홈페이지 통합과 표시 방식입니다.

- 기본 제목/초록/저자키워드 가중치: **5 / 1 / 5**
- 기본 인용 가중치 강도: **α=0.5**
- 인용 미반영 점수: 제목DF×제목가중치 + 초록DF×초록가중치 + 저자키워드DF×저자키워드가중치
- 인용 반영 점수: 논문별 필드 기여점수 × (1 + α×ln(1+피인용횟수))를 논문 전체에서 합산
- IDF: ln((전체 논문 수+1)/(통합DF+1))+1. 통합DF는 발견 필드가 여러 개여도 논문당 한 번입니다.
- 인용/IDF 적용 여부의 네 조합을 제공합니다. 피인용 열을 선택하지 않으면 인용 반영·미반영 점수가 같습니다.
- 한국어는 KoNLPy/Okt, 영어는 spaCy. 외부 생성형 AI API는 호출하지 않습니다.
- 키워드 seed·복합어 후보·불용어 기준은 포함된 엔진을 사용합니다. 사용자 자신의 Colab 코드에서 사전/별칭 등을 별도로 바꿨다면 그 변경까지 자동으로 가져오는 것은 아닙니다.

원문 행·단어 수에 따라 시간이 달라집니다. 최초 설치에는 모델 다운로드 시간이 추가됩니다. JSON·placement 파일은 이용자 결과물에 생성하지 않습니다. HTML 내부에는 클릭 검색에 필요한 데이터가 포함됩니다.

## 운영 방식과 한계

- 분석은 **방문자의 PC가 아닌 Streamlit 서버**에서 실행합니다.
- 기본 동시 분석 1건으로 제한합니다. 진행 중인 다른 분석이 있으면 잠시 후 다시 시작하라는 안내가 나타납니다. 자동 대기열은 아닙니다. 기존 공개 결과는 계속 열람할 수 있습니다.
- 각 세션의 입력·결과·캐시는 서로 다른 임시 폴더에 보관합니다. 공개 report.html을 교체하거나 다른 방문자 화면에 게시하지 않습니다.
- 분석 파일·캐시 삭제 버튼을 제공하며, 완료 후 24시간 동안 접근하지 않은 세션의 작업 파일은 앱이 살아 있는 동안 주기적으로 정리합니다. 서버 재시작 때도 유실될 수 있습니다. 브라우저를 새로고침하면 이전 세션 결과에 다시 연결되지 않을 수 있으니 필요한 결과를 저장하세요.
- Community Cloud의 제한된 메모리에서 8,000건 분석 완료를 보장하지는 않습니다. 기본은 100건으로 시험한 뒤 전체를 실행하는 흐름입니다. 대량 자료/여러 이용자의 상시 분석에는 더 큰 서버를 고려하세요.
- 업로드 한도 50MB, 시트 검사 최대 50,000행, 기본 작업 제한 1시간입니다. 이미지 최대 크기 등 설정이 클수록 메모리를 많이 씁니다.
- 환경 변수 `WORDCLOUD_MAX_CONCURRENT`, `WORDCLOUD_JOB_TIMEOUT`, `WORDCLOUD_SESSION_TTL`, `WORDCLOUD_FONT_PATH`로 운영 한도를 조정할 수 있습니다. 동시 실행 수를 늘리기 전 서버 자원을 확인하세요.

## 나중에 모양만 조정할 곳

- 상단 여백: `app.py` → `padding-top:4.5rem`
- 관련도순·다운로드 크기: `viewer.py` → `COMPACT_STYLE` → `font-size:12px`, `height:30px`, `padding:5px 8px`
- 결과 영역 높이: `app.py`, `builder.py` → `components.html(..., height=1300, scrolling=True)`
- 분석 초기 가중치: `builder.py`의 제목/초록/저자키워드 number_input 기본값

기존 report.html 파일의 CSS를 매번 직접 수정할 필요가 없습니다.

## 공식 배포 참고

- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies
- https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app
