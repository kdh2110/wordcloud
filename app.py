"""Streamlit Community Cloud entrypoint. Visitors immediately see the report."""
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
from viewer import prepare_report

st.set_page_config(page_title='연구 키프레이즈 · 논문 탐색',page_icon='📚',layout='wide',initial_sidebar_state='collapsed')
st.markdown('<style>.block-container{padding-top:0.6rem;padding-bottom:0.5rem;max-width:1900px}</style>',unsafe_allow_html=True)
report=Path(__file__).with_name('report.html')
try:
    html=prepare_report(report.read_text(encoding='utf-8-sig'))
except (OSError,ValueError) as e:
    st.error(f'결과 화면을 불러오지 못했습니다: {e}')
    st.info('관리자: 완성된 paper_explorer.html 파일의 이름을 report.html로 바꾸어 app.py와 같은 위치에 올려 주세요.')
    st.stop()

# Render only trusted administrator-provided report HTML, never a visitor upload.
components.html(html,height=1300,scrolling=True)
