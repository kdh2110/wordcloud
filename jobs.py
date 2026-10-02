"""Session-owned job folders and subprocess lifecycle; no shared NLP globals."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import atexit,copy,json,os,shutil,subprocess,sys,tempfile,threading,time,uuid

@dataclass
class Job:
    token:str
    owner:str
    root:Path
    process:subprocess.Popen
    config:dict
    started:float
    touched:float
    cancelled:bool=False

    def log_tail(self,limit=16000):
        try:
            with (self.root/'run.log').open('rb') as f:
                f.seek(0,2);size=f.tell();f.seek(max(0,size-limit))
                return f.read().decode('utf-8',errors='replace').replace('\r','\n')
        except FileNotFoundError:return ''

    @property
    def status(self):
        if self.process.poll() is None:return 'running'
        if self.cancelled:return 'cancelled'
        return 'done' if self.process.returncode==0 and (self.root/'success.txt').exists() else 'failed'

    @property
    def output(self):return self.root/'output'/self.config['mode']

class JobManager:
    def __init__(self):
        self.root=Path(tempfile.mkdtemp(prefix='paper_wordcloud_web_'))
        self.jobs={};self.lock=threading.RLock();self.closed=threading.Event()
        self.max_jobs=max(1,int(os.environ.get('WORDCLOUD_MAX_CONCURRENT','1')))
        self.ttl=max(300,int(os.environ.get('WORDCLOUD_SESSION_TTL','86400')))
        self.timeout=max(60,int(os.environ.get('WORDCLOUD_JOB_TIMEOUT','3600')))
        atexit.register(self.close)
        threading.Thread(target=self._reaper,daemon=True).start()

    def start(self,owner,content,config):
        with self.lock:
            if any(j.owner==owner and j.status=='running' for j in self.jobs.values()):
                raise ValueError('현재 진행 중인 분석을 완료하거나 중지한 뒤 다시 실행해 주세요.')
            if sum(j.status=='running' for j in self.jobs.values())>=self.max_jobs:
                raise ValueError('서버에서 다른 분석을 진행 중입니다. 잠시 후 다시 시작해 주세요.')
            token=uuid.uuid4().hex;root=self.root/owner/token;root.mkdir(parents=True)
            (root/'input.xlsx').write_bytes(content)
            cfg=copy.deepcopy(config);cfg['job_dir']=str(root);cfg['cache_dir']=str(self.root/owner/'cache')
            env=os.environ.copy();env['PYTHONUNBUFFERED']='1';env['PYTHONIOENCODING']='utf-8'
            for name in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:
                env.setdefault(name,'1')
            logfile=(root/'run.log').open('wb')
            try:
                process=subprocess.Popen([sys.executable,'-u',str(Path(__file__).with_name('worker.py'))],
                    stdin=subprocess.PIPE,stdout=logfile,stderr=subprocess.STDOUT,env=env,
                    cwd=str(Path(__file__).parent))
                process.stdin.write(json.dumps(cfg,ensure_ascii=False).encode('utf-8'));process.stdin.close()
            except Exception:
                if 'process' in locals():process.terminate();process.wait(timeout=10)
                shutil.rmtree(root,ignore_errors=True)
                raise
            finally:logfile.close()
            now=time.time();job=Job(token,owner,root,process,cfg,now,now);self.jobs[token]=job
            return job

    def get(self,owner,token):
        with self.lock:
            job=self.jobs.get(token)
            if job is None or job.owner!=owner:return None
            job.touched=time.time();return job

    def cancel(self,owner,token):
        with self.lock:
            j=self.get(owner,token)
            if j and j.status=='running':
                j.cancelled=True;j.process.terminate()
                try:j.process.wait(timeout=5)
                except subprocess.TimeoutExpired:j.process.kill();j.process.wait(timeout=5)

    def clear(self,owner):
        with self.lock:
            for token,j in list(self.jobs.items()):
                if j.owner==owner:
                    self.cancel(owner,token);del self.jobs[token]
            shutil.rmtree(self.root/owner,ignore_errors=True)

    def _reaper(self):
        while not self.closed.wait(30):
            with self.lock:
                now=time.time()
                for j in list(self.jobs.values()):
                    if j.status=='running' and now-j.started>self.timeout:
                        self.cancel(j.owner,j.token)
                        with (j.root/'run.log').open('a',encoding='utf-8') as f:f.write('\nERROR|최대 실행 시간을 초과하여 분석을 중지했습니다.\n')
                active={j.owner for j in self.jobs.values() if j.status=='running'}
                for owner in {j.owner for j in self.jobs.values()}-active:
                    if all(now-j.touched>self.ttl for j in self.jobs.values() if j.owner==owner):self.clear(owner)

    def close(self):
        if self.closed.is_set():return
        self.closed.set()
        with self.lock:
            for owner in {j.owner for j in self.jobs.values()}:self.clear(owner)
            shutil.rmtree(self.root,ignore_errors=True)
