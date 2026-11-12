from pathlib import Path
import json
import duckdb

root=Path(__file__).resolve().parent
db=root/'data/MAI_SMA_학생용DB_1000.duckdb'
con=duckdb.connect(str(db),read_only=True,config={'enable_external_access':False})
queries={
    '전체 정비 문서 수':'SELECT count(*) FROM master',
    '선박 수':'SELECT count(*) FROM vessels',
    '부품 소모 기록이 있는 서로 다른 문서 수':'SELECT count(*) FROM (SELECT DISTINCT VESSELCODE,DOC_NO FROM consumption)',
    '선박별 정비 문서 수':'SELECT VESSELCODE,count(*) FROM master GROUP BY VESSELCODE ORDER BY VESSELCODE',
}
print('MAI SMA - 학생용 1,000건 DB 기준값 확인')
print('DuckDB version:',duckdb.__version__)
print('Database:',db.name)
print('Mode: READ ONLY / SQL executed directly / LLM NOT USED')
print('='*72)
for title,sql in queries.items():
    rows=con.execute(sql).fetchall()
    print('\n'+title);print('SQL:',sql);print('Result:',rows)
print('\n이 수치는 DB 직접 조회값입니다. AI 모델의 답변 성공을 뜻하지 않습니다.')
con.close()
