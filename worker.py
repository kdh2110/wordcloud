"""One isolated Python process per analysis: model/JVM and globals never mix."""
from pathlib import Path
import sys,json,traceback,zipfile,os

def main():
    cfg=json.loads(sys.stdin.read())
    root=Path(cfg['job_dir']).resolve()
    print('STEP|0|실행 환경과 입력 데이터를 확인하고 있습니다.',flush=True)
    import pipeline as p
    # Config values are data only; users cannot choose code, output paths or fonts.
    mapping=cfg['columns']
    for key,value in mapping.items():
        if key in {'TITLE_COL','ABSTRACT_COL','KEYWORD_COL','CITATION_COL','AUTHORS_COL','YEAR_COL','JOURNAL_COL','DOI_COL','LINK_COL','DOCUMENT_ID_COL','SOURCE_COL'}:
            setattr(p,key,value)
    p.SHEET_NAME=cfg['sheet']
    for key in ['TITLE_WEIGHT','ABSTRACT_WEIGHT','KEYWORD_WEIGHT','CITATION_ALPHA','CITATION_AS_OF','WORDCLOUD_MAX_WORDS','WORDCLOUD_MIN_DF','MIN_PHRASE_FREQ','MIN_PHRASE_DF','PMI_THRESHOLD','MAX_NGRAM','WORDCLOUD_COLORMAP','WORDCLOUD_WIDTH','WORDCLOUD_HEIGHT','WORDCLOUD_MAX_FONT','WORDCLOUD_MIN_FONT','WORDCLOUD_SIZE_POWER','HTML_INCLUDE_ABSTRACT','KEYWORD_SEPARATOR']:
        if key in cfg['settings']:setattr(p,key,cfg['settings'][key])
    if not p.CITATION_COL:
        p.CITATION_ALPHA=0.0;p.RANKING_VERSION='no_idf'
    p.EXCLUDE_GENERIC_PHRASES.update(cfg.get('exclude',[]))
    p.MISSING_CITATIONS='neutral'
    font=os.environ.get('WORDCLOUD_FONT_PATH','').strip()
    if font:p.WORDCLOUD_FONT_PATH=font
    if min(p.TITLE_WEIGHT,p.ABSTRACT_WEIGHT,p.KEYWORD_WEIGHT)<0 or sum([p.TITLE_WEIGHT,p.ABSTRACT_WEIGHT,p.KEYWORD_WEIGHT])<=0:
        raise ValueError('가중치는 0 이상이며, 한 가지 이상은 0보다 커야 합니다.')
    if p.WORDCLOUD_MIN_FONT>p.WORDCLOUD_MAX_FONT:raise ValueError('최소 글자 크기는 최대 글자 크기보다 작아야 합니다.')
    # Preflight before loading spaCy; invalid citation values retain Excel row numbers.
    header,records=p.read_rows(root/'input.xlsx',cfg['mode'])
    needs_ko=any(p.HANGUL.search(p.clean(r['title'])+' '+p.clean(r['abstract'])+' '+p.clean(r['keywords'])) for r in records)
    if needs_ko:
        import jpype
        try:jpype.getDefaultJVMPath()
        except Exception as e:raise RuntimeError('한국어 분석에는 Java(JDK/JRE)가 필요합니다. 설치 후 앱을 다시 시작하거나 Docker 실행 방법을 이용하세요.') from e
    import importlib.util
    if importlib.util.find_spec('en_core_web_sm') is None:
        raise RuntimeError('영어 모델이 없습니다. python -m spacy download en_core_web_sm 을 실행해 주세요.')
    # Printing stages as they are reached. No fabricated completion percentage.
    p.read_rows_original=p.read_rows
    def reading(*a,**kw):
        print('STEP|1|저자키워드 사전과 제목·초록을 분석합니다.',flush=True)
        return p.read_rows_original(*a,**kw)
    p.read_rows=reading
    original_report=p.write_df_report
    def reporting(*a,**kw):
        print('STEP|3|점수 계산, Excel 및 네 가지 워드클라우드를 생성합니다.',flush=True)
        return original_report(*a,**kw)
    p.write_df_report=reporting
    out=p.run(root/'input.xlsx',cfg['mode'],root/'output',Path(cfg['cache_dir']))
    from viewer import prepare_report
    report=out/'paper_explorer.html'
    report.write_text(prepare_report(report.read_text(encoding='utf-8')),encoding='utf-8')
    paths=[out/'analysis.xlsx',out/'paper_explorer.html']+[out/f'wordcloud_{v}.png' for v in p.SCORE_FIELDS]
    if not (out/'analysis.xlsx').exists() or not (out/'paper_explorer.html').exists():
        raise RuntimeError('필수 결과 파일이 생성되지 않았습니다. 실행 기록을 확인해 주세요.')
    # Only the requested six outputs enter the ZIP. Logs/cache/input stay outside.
    with zipfile.ZipFile(root/'results.zip','w',zipfile.ZIP_DEFLATED) as z:
        for path in paths:
            if path.is_file():z.write(path,path.name)
    for path in paths:
        if not path.exists():print(f'WARNING|{path.name} 생성 실패. 나머지 결과는 다운로드할 수 있습니다.',flush=True)
    (root/'success.txt').write_text(str(out.relative_to(root)),encoding='utf-8')
    print('STEP|4|분석과 결과 파일 생성이 완료되었습니다.',flush=True)

if __name__=='__main__':
    try:main()
    except Exception as e:
        print(f'ERROR|{type(e).__name__}: {e}',flush=True)
        traceback.print_exc()
        sys.exit(1)
