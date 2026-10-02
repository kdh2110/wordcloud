"""Display an existing v8 HTML report, adding a download for its selected PNG."""
from pathlib import Path
import json,re

# This script runs AFTER the existing report script, so D/version/changeVersion
# refer to the original report state. It does not recompute any rankings.
DOWNLOAD_SCRIPT = r'''
<script>
(function () {
  "use strict";
  const button = document.getElementById("downloadCloud");
  function updateCloudDownload() {
    const cloud = D.clouds[version];
    button.disabled = !(cloud && typeof cloud.png === "string" && cloud.png.startsWith("data:image/png;base64,"));
    button.title = button.disabled ? "현재 조건의 이미지가 없습니다." : "현재 인용·IDF 조건의 원본 PNG 저장";
  }
  button.addEventListener("click", function () {
    const cloud = D.clouds[version];
    if (!cloud || !cloud.png || !cloud.png.startsWith("data:image/png;base64,")) return;
    const a = document.createElement("a");
    a.href = cloud.png;
    a.download = "wordcloud_" + version + ".png";
    document.body.appendChild(a);
    a.click();
    a.remove();
  });
  const originalChangeVersion = changeVersion;
  changeVersion = function (v) {
    originalChangeVersion(v);
    updateCloudDownload();
  };
  const csv = document.getElementById("csv");
  if (csv) {
    csv.textContent = "리스트 다운로드";
    csv.title = "선택한 표현의 검색·발견 위치·정렬 조건에 맞는 전체 논문 목록을 CSV로 저장합니다. 현재 페이지뿐 아니라 모든 페이지를 포함합니다.";
  }
  updateCloudDownload();
})();
</script>
'''

def prepare_report(text):
    """Accept only a trusted administrator-provided full v8 report, not a template."""
    found=re.search(r'<script\b(?=[^>]*\bid=[\"\']dataset[\"\'])[^>]*>(.*?)</script\s*>',text,re.S|re.I)
    if not found:
        raise ValueError('report.html에 분석 데이터가 없습니다. v8에서 생성한 paper_explorer.html을 넣어 주세요.')
    try:data=json.loads(found.group(1))
    except (ValueError,TypeError) as e:
        raise ValueError('HTML의 분석 데이터를 읽을 수 없습니다. __PAYLOAD__가 있는 템플릿 대신 완성된 결과 HTML을 사용하세요.') from e
    if not isinstance(data,dict) or not {'papers','terms','clouds'}.issubset(data):
        raise ValueError('v8 결과 HTML 형식이 아닙니다.')
    if not isinstance(data['papers'],list) or not isinstance(data['terms'],list) or not isinstance(data['clouds'],dict):
        raise ValueError('논문·표현·이미지 데이터 형식을 확인해 주세요.')
    if not re.search(r'function\s+changeVersion\s*\(',text):
        raise ValueError('인용·IDF 전환 함수가 없습니다. v8 결과 HTML을 사용하세요.')
    # Always apply the current styles, even to an already-patched report.
    style_pattern = r'<style\b[^>]*id=["\']viewer-ui-v9["\'][^>]*>.*?</style\s*>'
    if re.search(style_pattern, text, flags=re.S|re.I):
        text = re.sub(style_pattern, lambda m: COMPACT_STYLE.strip(), text, flags=re.S|re.I)
    else:
        text = re.sub(r'</head\s*>', lambda m: COMPACT_STYLE.strip() + m.group(), text, count=1, flags=re.I)
    if re.search(r'id=[\"\']downloadCloud[\"\']',text):
        return text
    marker=re.search(r'<p\b(?=[^>]*\bid=[\"\']cloudnote[\"\'])[^>]*>.*?</p\s*>',text,re.S|re.I)
    if not marker:raise ValueError('워드클라우드 영역을 찾을 수 없습니다. HTML에 cloudnote 요소가 필요합니다.')
    control='\n<div class="cloud-download"><button id="downloadCloud" type="button">워드클라우드 다운로드</button></div>\n'
    text=text[:marker.end()]+control+text[marker.end():]
    css='\n<style>.cloud-download{display:flex;justify-content:flex-end;margin:4px 0 14px}.cloud-download button{font-size:12px;padding:6px 10px}@media print{.cloud-download{display:none}}</style>\n'
    text=re.sub(r'</head\s*>',lambda m:css+m.group(),text,count=1,flags=re.I)
    text=re.sub(r'</body\s*>',lambda m:DOWNLOAD_SCRIPT+m.group(),text,count=1,flags=re.I)
    return text

# Scoped inside the HTML iframe. Size values also override older v8 CSS.
COMPACT_STYLE = r'''
<style id="viewer-ui-v9">
#paperSort,#csv,#downloadCloud {
  font-family:inherit!important;font-size:12px!important;line-height:1.4!important;
  padding:5px 8px!important;height:30px!important;min-height:30px!important;
  width:auto!important;max-width:100%;box-sizing:border-box!important;
  margin:0!important;white-space:nowrap!important;flex:0 0 auto!important;
}
#paperSort {min-width:96px!important;}
#csv,#downloadCloud {min-width:0!important;}
.list-actions {display:flex;align-items:center;justify-content:flex-end;gap:6px;flex-wrap:wrap;}
.cloud-download {display:flex;justify-content:flex-end;margin:4px 0 14px;}
@media print {.cloud-download{display:none}}
</style>
'''
