# 링크로 바로 보는 논문 워드클라우드

방문자는 링크에 접속하면 즉시 기존 HTML의 워드클라우드와 논문 목록을 볼 수 있습니다. 홈페이지에 Excel 업로드·분석 실행 화면은 없습니다.

- 워드클라우드 글자 클릭 → 관련 논문 표시
- 인용 반영/미반영, IDF 적용/미적용 전환
- 논문 검색, 발견 위치 필터, 관련도순/피인용순
- **워드클라우드 다운로드**: 현재 선택한 인용·IDF 조건의 원본 PNG
- **리스트 다운로드**: 선택한 키프레이즈의 현재 검색·발견 위치·정렬 조건에 맞는 전체 논문 목록 CSV (현재 페이지뿐 아니라 모든 페이지 포함)

## 현재 들어 있는 결과

**동봉된 report.html은 이전에 제공한 Scopus 샘플100건의 분석 결과입니다.** 화면 상단에도 샘플임을 표시했습니다. 현재 보유한 실제 전체 결과 HTML을 아래 방법으로 교체하면 그 결과가 홈페이지에 표시됩니다.

이 앱은 미리 계산한 결과를 보여주므로 Java·KoNLPy·spaCy를 서버에 설치할 필요가 없습니다. 분석은 기존 Colab/Python 코드에서 수행하고, 배포 서버는 결과 화면만 제공합니다.

배포 전에 동봉된 **report.html을 브라우저에서 열어** 화면과 두 다운로드 버튼을 미리 확인할 수도 있습니다.

## 1. GitHub에 올리기

1. ZIP을 압축 해제합니다.
2. https://github.com 에 로그인하고 `New repository`를 선택합니다.
3. 저장소 이름을 예를 들어 `paper-wordcloud-viewer`로 지정합니다. 코드와 논문 데이터가 함께 들어 있으므로 저장소 공개 여부를 원하는 방식으로 선택하세요.
4. 저장소를 생성한 뒤 `uploading an existing file` 또는 `Add file → Upload files`를 누릅니다.
5. 압축을 푼 폴더 **안의 파일과 `.streamlit` 폴더**를 올립니다. ZIP 자체나 상위 폴더를 올리지 마세요.
6. `Commit changes`를 누릅니다.

GitHub 저장소 첫 화면에 `app.py`, `viewer.py`, `report.html`, `requirements.txt`, `README.md`가 보여야 합니다. `.streamlit/config.toml`도 포함되어야 합니다.

폴더가 업로드되지 않았다면 GitHub의 `Add file → Create new file`에서 파일명에 `.streamlit/config.toml`을 입력하고 동봉된 파일의 내용을 붙여 넣으세요.

## 2. Streamlit에서 배포하기

1. https://share.streamlit.io 에 접속해 GitHub 계정을 연결합니다.
2. **Create app → Yup, I have an app**을 선택합니다.
3. 아래 항목을 지정합니다.

| 항목 | 값 |
|---|---|
| Repository | 직접 만든 `내아이디/paper-wordcloud-viewer` |
| Branch | `main` 또는 실제 GitHub 브랜치 |
| Main file path | **app.py** |
| App URL | 사용 가능한 원하는 이름 |
| Advanced settings → Python version | **3.12** |
| Secrets | 필요 없음 |

4. **Deploy**를 누릅니다.
5. 설치가 완료되면 `<앱이름>.streamlit.app` 주소가 열립니다. 이 주소를 다른 사람에게 공유하면 됩니다.

GitHub 업로드만으로 Streamlit 주소가 자동 생성되지는 않습니다. 처음 한 번은 위 배포 설정이 필요합니다. GitHub Pages 설정은 사용하지 않습니다.

앱 설정의 `Sharing → Who can view this app`에서 공개 범위를 확인하세요. 공개 앱은 링크로 볼 수 있고 비공개 앱은 허용된 이용자가 로그인해서 봅니다. 저장소 공개 범위와 앱 공개 범위를 각각 확인하세요.

## 3. 실제 결과로 바꾸는 방법 (관리자)

1. 기존 v8 코드로 생성한 **paper_explorer.html**을 준비합니다. 논문 데이터와 이미지가 포함된 완성된 파일이어야 합니다.
2. 파일 이름을 **report.html**로 바꿉니다.
3. GitHub에서 현재 `report.html`을 새 파일로 덮어쓰고 `Commit changes`를 누릅니다.
4. Streamlit의 변경 반영이 끝나면 페이지를 새로고침합니다. 반영되지 않으면 Manage app에서 Reboot 후 확인하세요.

**EXPLORER_TEMPLATE = ...로 시작하는 Python 코드나 __PAYLOAD__가 들어 있는 HTML 템플릿을 올리면 안 됩니다.** 실제 논문 데이터가 포함된 최종 결과 HTML이어야 합니다.

별도의 Excel이나 PNG 파일을 함께 올릴 필요는 없습니다. v8의 HTML에 네 가지 이미지와 논문 데이터가 이미 들어 있으므로, 홈페이지에서 현재 선택한 이미지를 바로 저장합니다. 관리자가 올린 HTML은 코드로 실행되므로 본인이 관리하는 결과 파일만 사용하세요.

결과 데이터와 기존 HTML 디자인을 유지한 상태에서, 앱이 이미지 다운로드 버튼을 추가하고 기존 CSV 버튼을 `리스트 다운로드`로 표시합니다. report.html을 바꿔도 이 처리는 자동 적용됩니다. `viewer.py`는 기존 v8의 `dataset`, `cloudnote`, `changeVersion` 구조를 사용합니다.

## 4. 파일 역할

| 파일 | 역할 |
|---|---|
| app.py | Streamlit 첫 화면에서 report.html 표시 |
| viewer.py | 결과 형식 확인, 이미지 다운로드 버튼 연결 |
| report.html | 실제 화면과 분석 데이터 (현재는100건 샘플) |
| requirements.txt | Streamlit 설치 |
| .streamlit/config.toml | 화면·메시지 용량 설정 |
| VALIDATION.md | 기능 확인 내용 |

이전의 업로드형 앱 대신 **새 저장소에 이 파일 묶음을 올리는 방식**을 권장합니다. 기존 저장소를 재사용한다면 이전 `requirements.txt`를 반드시 이 파일로 교체하고, 기존의 `packages.txt` 및 분석용 의존성 파일을 제거해야 불필요한 Java·모델 설치를 피할 수 있습니다.

## 5. 표시와 다운로드

- 첫 화면부터 결과를 표시합니다. 이용자가 파일을 올리거나 분석 시작을 누를 필요가 없습니다.
- PNG는 화면을 캡처한 것이 아니라 HTML에 들어 있는 원래 해상도의 이미지입니다. 다운로드 파일명에 인용·IDF 조건을 포함합니다.
- 리스트는 Excel에서 열 수 있는 UTF-8 BOM CSV입니다. 화면에서는 저자를20명까지만 보여도 목록 파일은 원래 전체 저자 정보를 유지합니다.
- 클릭 여유8px, 검색·정렬·페이지 이동, 저널명 강조 등은 동봉된 결과 HTML에 유지되어 있습니다.
- 홈페이지의 높이는 app.py 마지막 줄의 `height=1300`에서 조정할 수 있습니다.
- 개인정보/논문 초록 등 HTML 안에 포함한 내용은 해당 앱에 접속할 수 있는 사람에게 전달됩니다. 공개할 최종 결과 파일을 선택해 배포하세요.

## 6. 오류가 나면

- `report.html`을 못 찾음: app.py와 같은 폴더인지 확인하세요.
- `분석 데이터가 없습니다`: 완성된 v8 결과 HTML인지 확인하세요.
- `__PAYLOAD__` 관련 오류: 분석 전 템플릿 대신 실제 결과 파일을 올리세요.
- 이미지 다운로드가 비활성화됨: 그 인용·IDF 조합의 PNG가 기존 분석 때 생성되지 않은 경우입니다.
- 다운로드가 차단됨: 브라우저의 다운로드 차단 표시를 확인하고 다시 버튼을 누르세요.
- 대용량 HTML: GitHub 웹 업로드는 파일 크기에 제한이 있습니다. 파일이 큰 경우 Git으로 올리거나 결과에 초록을 포함하지 않는 설정을 검토하세요. 표시 서버의 메시지 한도는 config.toml에서200MB로 설정했습니다.

## 공식 배포 안내

https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

이 배포물은 실제 계정에 배포된 상태는 아닙니다. 본인의 GitHub·Streamlit 계정에서 위 절차로 배포하면 공유 주소가 생성됩니다.
