"""v9: published report + session-owned Excel analysis, Streamlit Cloud entrypoint."""
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
from viewer import prepare_report

st.set_page_config(page_title='연구 키프레이즈 · 논문 탐색',page_icon='📚',layout='wide',initial_sidebar_state='collapsed')
# Keep content below Streamlit's fixed header. Do not hide its menu/share controls.
st.markdown("""<style>
[data-testid="stMainBlockContainer"],.block-container {
  padding-top:4.5rem!important;padding-bottom:1.5rem;max-width:1900px;
}
</style>""",unsafe_allow_html=True)

published,create=st.tabs(['기존 결과 보기','내 파일로 워드클라우드 만들기'])
with published:
    report=Path(__file__).with_name('report.html')
    if not report.exists():
        report=Path(__file__).with_name('sample_report.html')
    try:
        html=prepare_report(report.read_text(encoding='utf-8-sig'))
    except (OSError,ValueError) as e:
        st.error(f'결과 화면을 불러오지 못했습니다: {e}')
        st.info('관리자: 완성된 v8 paper_explorer.html을 report.html로 이름을 바꾸어 app.py와 같은 위치에 넣어 주세요.')
    else:
        components.html(html,height=1300,scrolling=True)
with create:
    from builder import render_builder
    render_builder()
