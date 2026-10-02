from pathlib import Path
import hashlib,json,re,time,uuid
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from excel_io import workbook_sheets,inspect_sheet
from jobs import JobManager

from viewer import prepare_report

@st.cache_resource
def manager():return JobManager()
def render_builder():
    mgr=manager()
    if 'owner' not in st.session_state:st.session_state.owner=uuid.uuid4().hex
    owner=st.session_state.owner
    job=mgr.get(owner,st.session_state.get('job_token'))
    running=bool(job and job.status=='running')
    st.subheader('내 파일로 워드클라우드 만들기')
    st.caption('내 Excel 업로드 → 분석 시작 → 이 화면에서 워드클라우드와 논문 탐색')
    st.info('원본 논문 Excel(.xlsx)을 사용해 주세요. 업로드한 파일은 서버에서 분석하며, 결과는 현재 세션에서만 보여집니다. 기존 공개 결과는 바뀌지 않습니다.')

    with st.expander('분석 설정 · 가중치 · 이미지',expanded=False):
        st.subheader('분석 설정')
        mode=st.radio('분석 범위',['sample','full'],format_func=lambda v:'샘플 · 최대 100건' if v=='sample' else '전체 논문',disabled=running)
        words=st.number_input('워드클라우드 최대 단어 수',10,300,50,10,disabled=running)
        st.markdown('**필드별 가중치**')
        tw=st.number_input('제목',0.0,100.0,5.0,.5,disabled=running)
        aw=st.number_input('초록',0.0,100.0,1.0,.5,disabled=running)
        kw=st.number_input('저자키워드',0.0,100.0,5.0,.5,disabled=running)
        alpha=st.number_input('인용 반영 강도 α',0.0,10.0,.5,.1,disabled=running,help='0이면 인용 미반영 점수와 같습니다. 네 가지 인용·IDF 조합을 모두 출력합니다.')
        asof=st.text_input('피인용 데이터 수집일 (선택)',placeholder='예: 2026-10-01',disabled=running)
        with st.container():
            st.markdown('**후보 발견 · 제외 표현**')
            min_df=st.number_input('이미지에 포함할 최소 논문 수',1,1000,2,disabled=running)
            min_freq=st.number_input('자동 후보 최소 등장 횟수',2,1000,5,disabled=running)
            phrase_df=st.number_input('자동 후보 최소 논문 수',2,1000,3,disabled=running)
            pmi=st.number_input('자동 후보 최소 PMI',0.0,20.0,3.0,.5,disabled=running)
            extra=st.text_area('추가 제외 표현 · 한 줄에 하나',value='south korea',disabled=running,help='기존 불용어 목록에 추가합니다. 영어는 소문자 표제어 형태로 입력하세요.')
        with st.container():
            st.markdown('**이미지 · HTML 설정**')
            cmap=st.selectbox('색상',['hsv','rainbow','tab10','Dark2','viridis'],disabled=running)
            width=st.number_input('이미지 가로(px)',800,3000,2000,100,disabled=running)
            height=st.number_input('이미지 세로(px)',600,2000,1200,100,disabled=running)
            maxfont=st.number_input('최대 글자 크기',30,250,150,10,disabled=running)
            minfont=st.number_input('최소 글자 크기',8,50,16,1,disabled=running)
            power=st.number_input('글자 크기 차이',0.2,2.0,1.0,.1,disabled=running,help='작을수록 크기 차이가 완화됩니다.')
            abstracts=st.checkbox('HTML에 초록 포함',True,disabled=running)
        st.caption('한국어 KoNLPy · 영어 spaCy. 분석 중 외부 AI API를 호출하지 않습니다.')

    uploaded=st.file_uploader('1. 원본 논문 Excel 업로드',type=['xlsx'],disabled=running,help='집계 결과 analysis.xlsx가 아닌 제목·초록·저자키워드가 있는 원본 파일을 선택하세요.')
    ready=False;config=None;content=None;fingerprint=None
    if uploaded is not None:
        content=uploaded.getvalue();fingerprint=hashlib.sha256(content).hexdigest()
        try:
            if st.session_state.get('upload_hash')!=fingerprint:
                sheets=workbook_sheets(content)
                st.session_state.upload_hash=fingerprint
                st.session_state.upload_sheets=sheets
                st.session_state.sheet_info={}
            sheet=st.selectbox('분석할 시트',st.session_state.upload_sheets,disabled=running)
            if sheet not in st.session_state.sheet_info:
                st.session_state.sheet_info[sheet]=inspect_sheet(content,sheet)
            info=st.session_state.sheet_info[sheet];names=info['columns']
            st.caption(f'{info["count"]:,}건 · {len(names)}개 열 / 현재 모드: '+('최대 100건 무작위 샘플' if mode=='sample' else '전체 분석'))
            with st.expander('2. 열 이름 확인',expanded=not running and job is None):
                st.dataframe(pd.DataFrame(info['preview']).fillna('').astype(str),hide_index=True)
                st.caption('첫 번째 행을 열 이름으로 사용합니다. 자동 선택이 맞는지 확인해 주세요.')
                def column(label,aliases,key,required=False):
                    match=next((n for n in names if n.casefold() in {a.casefold() for a in aliases}),None)
                    options=[None]+names
                    return st.selectbox(label+(' *' if required else ''),options,index=options.index(match),
                        format_func=lambda v:'선택 안 함' if v is None else v,key=f'{fingerprint[:12]}:{sheet}:{key}',disabled=running)
                c1,c2,c3=st.columns(3)
                with c1:title=column('제목',['Title','제목','논문제목','Article Title'],'title',True)
                with c2:abstract=column('초록',['Abstract','초록'],'abstract',True)
                with c3:keyword=column('저자키워드',['Author Keywords','저자키워드','저자 키워드'],'keyword',True)
                c1,c2=st.columns(2)
                with c1:citation=column('피인용 횟수',['Cited by','Citation Count','Citations','Times Cited, WoS Core','피인용횟수','피인용 횟수'],'citation')
                with c2:separator=st.selectbox('저자키워드 구분자',['; ',',','|'],index=0,format_func=lambda v:{'; ':'세미콜론 (;) ', ',':'쉼표 (,)', '|':'세로줄 (|)'}[v],disabled=running)
                metadata={}
                with st.expander('논문 목록에 표시할 서지정보 (선택)'):
                    for key,label,aliases in [('AUTHORS_COL','저자',['Authors','저자','Author Full Names']),('YEAR_COL','연도',['Year','Publication Year','연도']),('JOURNAL_COL','저널명',['Source title','Source Title','Publication Title','저널명','학술지명']),('DOI_COL','DOI',['DOI']),('LINK_COL','논문 링크',['Link','URL']),('DOCUMENT_ID_COL','중복 확인용 식별자',['EID','UT (Unique WOS ID)','UT']),('SOURCE_COL','데이터 출처',['Source','출처'])]:
                        metadata[key]=column(label,aliases,key)
            if citation is None:st.info('피인용 횟수 열을 선택하지 않았습니다. 인용 가중치는 적용하지 않으며, 인용 반영/미반영 결과가 같게 생성됩니다.')
            columns={'TITLE_COL':title,'ABSTRACT_COL':abstract,'KEYWORD_COL':keyword,'CITATION_COL':citation,**metadata}
            ready=all([title,abstract,keyword]) and len({title,abstract,keyword})==3 and (citation is None or citation not in {title,abstract,keyword}) and tw+aw+kw>0 and minfont<=maxfont
            if not ready:st.warning('제목·초록·저자키워드를 서로 다른 열로 지정하고, 가중치와 글자 크기를 확인해 주세요.')
            config={'sheet':sheet,'columns':columns,'mode':mode,'source_name':uploaded.name,'source_hash':fingerprint,
                'exclude':[x.strip().lower() for x in extra.splitlines() if x.strip()],
                'settings':{'TITLE_WEIGHT':tw,'ABSTRACT_WEIGHT':aw,'KEYWORD_WEIGHT':kw,'CITATION_ALPHA':alpha if citation else 0.0,'CITATION_AS_OF':asof,
                    'WORDCLOUD_MAX_WORDS':int(words),'WORDCLOUD_MIN_DF':int(min_df),'MIN_PHRASE_FREQ':int(min_freq),'MIN_PHRASE_DF':int(phrase_df),'PMI_THRESHOLD':pmi,'MAX_NGRAM':5,
                    'WORDCLOUD_COLORMAP':cmap,'WORDCLOUD_WIDTH':int(width),'WORDCLOUD_HEIGHT':int(height),'WORDCLOUD_MAX_FONT':int(maxfont),'WORDCLOUD_MIN_FONT':int(minfont),'WORDCLOUD_SIZE_POWER':power,'HTML_INCLUDE_ABSTRACT':abstracts,'KEYWORD_SEPARATOR':separator.strip()}}
        except Exception as e:st.error(f'파일 확인 실패: {e}')
    else:
        st.info('Scopus 등의 원본 Excel을 선택해 주세요. 첫 시험은 샘플 모드로 실행하시면 됩니다.')

    if st.button('3. 분석 시작',type='primary',disabled=running or not ready):
        try:
            new_job=mgr.start(owner,content,config)
            st.session_state.job_token=new_job.token
            st.session_state.pop('results_table',None)
            st.rerun()
        except ValueError as e:st.warning(str(e))
        except Exception as e:st.error(f'분석을 시작하지 못했습니다: {e}')

    if job and job.status=='running':
        @st.fragment(run_every=1)
        def monitor():
            current=mgr.get(owner,job.token)
            if not current or current.status!='running':st.rerun()
            log=current.log_tail()
            steps=re.findall(r'STEP\|\d+\|([^\n]+)',log)
            elapsed=int(time.time()-current.started)
            st.info((steps[-1] if steps else '분석을 준비하고 있습니다.')+f' · 경과 {elapsed//60}분 {elapsed%60}초')
            st.caption('논문 수와 컴퓨터 성능에 따라 시간이 걸립니다. 완료되면 결과 화면이 자동으로 나타납니다.')
            if st.button('분석 중지',key='cancel_job'):
                mgr.cancel(owner,current.token);st.rerun()
            with st.expander('실행 기록'):st.code(log[-10000:],language='text')
        monitor()
    elif job:
        if job.status=='done':
            st.success('분석이 완료되었습니다.')
            settings=job.config['settings']
            st.caption(f"현재 결과: {job.config['source_name']} · {job.config['sheet']} · {job.config['mode']} / 제목 {settings['TITLE_WEIGHT']:g}, 초록 {settings['ABSTRACT_WEIGHT']:g}, 저자키워드 {settings['KEYWORD_WEIGHT']:g}, α {settings['CITATION_ALPHA']:g}")
            if config and any(config.get(k)!=job.config.get(k) for k in config):
                st.warning('업로드 파일 또는 설정이 현재 결과와 다릅니다. 변경 사항은 분석 시작을 눌러야 반영됩니다.')
            for line in job.log_tail().splitlines():
                if line.startswith('WARNING|'):st.warning(line.split('|',1)[1])
            view,table,downloads=st.tabs(['워드클라우드 · 논문 탐색','순위표','결과 다운로드'])
            with view:
                components.html(prepare_report((job.output/'paper_explorer.html').read_text(encoding='utf-8')),height=1300,scrolling=True)
            with table:
                wb=pd.ExcelFile(job.output/'analysis.xlsx',engine='openpyxl')
                sheet_result=st.selectbox('결과 시트',wb.sheet_names,key='result_sheet')
                cache_key=(job.token,sheet_result)
                if st.session_state.get('results_table_key')!=cache_key:
                    st.session_state.results_table=pd.read_excel(wb,sheet_name=sheet_result,nrows=1000)
                    st.session_state.results_table_key=cache_key
                wb.close()
                st.dataframe(st.session_state.results_table,hide_index=True)
                st.caption('화면에는 최대 1,000행을 표시합니다. 전체 내용은 Excel을 다운로드해 확인하세요.')
            with downloads:
                st.download_button('전체 결과 ZIP 다운로드',(job.root/'results.zip').read_bytes(),'wordcloud_results.zip','application/zip',type='primary',on_click='ignore')
                for path in [job.output/'analysis.xlsx',job.output/'paper_explorer.html']+sorted(job.output.glob('wordcloud_*.png')):
                    if path.exists():
                        mime={'.xlsx':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','.html':'text/html','.png':'image/png'}[path.suffix]
                        st.download_button(path.name,path.read_bytes(),path.name,mime,key='download_'+path.name,on_click='ignore')
                st.caption('HTML을 내려받으면 서버 없이 다시 열 수 있습니다. 별도 JSON·placement 파일은 생성하지 않습니다.')
        elif job.status=='cancelled':st.warning('분석을 중지했습니다. 설정을 확인한 뒤 다시 실행할 수 있습니다.')
        else:
            errors=re.findall(r'ERROR\|([^\n]+)',job.log_tail())
            st.error(errors[-1] if errors else '분석에 실패했습니다. 아래 실행 기록을 확인해 주세요.')
        with st.expander('실행 기록 확인'):st.code(job.log_tail(),language='text')
        if st.button('이 세션의 분석 파일·캐시 삭제'):
            mgr.clear(owner)
            for key in ['job_token','results_table','results_table_key']:st.session_state.pop(key,None)
            st.rerun()

    with st.expander('점수 계산과 사용 안내'):
        st.markdown('''기본점수 = **제목DF×5 + 초록DF×1 + 저자키워드DF×5** (가중치는 설정값에 따릅니다).

    인용 반영점수 = **Σ[논문별 필드 기여점수 × (1 + α×ln(1+피인용 횟수))]**.

    IDF = ln((전체 논문 수+1)/(통합DF+1))+1. 네 가지 조합에서 키프레이즈를 우선 정렬합니다.

    관련도순은 각 논문이 선택한 표현의 점수에 기여하는 값의 내림차순입니다. 피인용은 연구의 질 자체를 뜻하지 않으며, 출판 시점·분야에 영향을 받습니다.

    분석은 앱이 실행되는 컴퓨터에서 수행합니다. 업로드 파일·결과·캐시는 세션별 임시 폴더에 보관하며, 작업이 끝난 후 24시간 동안 접근하지 않으면 정리합니다. 브라우저 새로고침 시 세션 연결이 끊길 수 있으므로 완료된 결과를 다운로드해 주세요.''')
