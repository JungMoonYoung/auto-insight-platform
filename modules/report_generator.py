"""
Report Generator Module
HTML 형식의 분석 리포트 자동 생성 (Enhanced Design)
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List
import plotly.graph_objects as go

# 마크다운 라이브러리 (없으면 텍스트로 출력)
try:
    import markdown
except ImportError:
    markdown = None


class HTMLReportGenerator:
    """HTML 리포트 생성기 (Pro Design)"""
    
    def __init__(self, template_path: str = None):
        self.template_path = template_path or Path(__file__).parent.parent / "templates" / "report_template.html"
    
    def generate_report(self,
                       analysis_type: str,
                       data_info: Dict,
                       insights: Dict,
                       charts: List[go.Figure],
                       summary_table: str = None,
                       gpt_analysis: str = None) -> str:
        """HTML 리포트 생성"""
        # 템플릿 로드 (파일이 없으면 내부 템플릿 사용)
        template = self._get_pro_template()
        
        # 기본 정보 설정
        report_date = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
        type_names = {
            'ecommerce': 'E-Commerce 고객 세분화 분석',
            'sales': '매출 트렌드 및 성과 분석',
            'review': '고객 리뷰 및 감성 분석'
        }
        analysis_name = type_names.get(analysis_type, '데이터 분석 리포트')
        
        # 차트 HTML 변환
        charts_html = self._convert_charts_to_html(charts)
        
        # 인사이트 HTML 변환
        findings_html = self._format_findings(insights.get('key_findings', []))
        actions_html = self._format_actions(insights.get('action_items', []))
        
        # GPT 분석 HTML 변환 (마크다운 적용)
        gpt_html = self._format_gpt_analysis(gpt_analysis)
        
        # 데이터 정보 HTML 변환
        data_info_html = self._format_data_info(data_info)
        
        # 템플릿 치환
        html = template.replace('{{REPORT_DATE}}', report_date)
        html = html.replace('{{ANALYSIS_TYPE}}', analysis_name)
        html = html.replace('{{DATA_INFO}}', data_info_html)
        html = html.replace('{{KEY_FINDINGS}}', findings_html)
        html = html.replace('{{ACTION_ITEMS}}', actions_html)
        html = html.replace('{{GPT_ANALYSIS}}', gpt_html)
        html = html.replace('{{CHARTS}}', charts_html)
        
        if summary_table:
            html = html.replace('{{SUMMARY_TABLE}}', summary_table)
        else:
            html = html.replace('{{SUMMARY_TABLE}}', '')
        
        return html
    
    def _convert_charts_to_html(self, charts: List[go.Figure]) -> str:
        """Plotly 차트를 HTML로 변환"""
        charts_html = ""
        for i, fig in enumerate(charts):
            chart_html = fig.to_html(
                include_plotlyjs='cdn' if i == 0 else False,
                div_id=f'chart_{i}',
                config={'displayModeBar': False, 'responsive': True}
            )
            charts_html += f'<div class="chart-wrapper">{chart_html}</div>\n'
        return charts_html
    
    def _format_findings(self, findings: List[str]) -> str:
        if not findings: return "<p class='empty-msg'>발견사항이 없습니다.</p>"
        html = "<ul class='insight-list'>\n"
        for f in findings: html += f"<li>{f}</li>\n"
        html += "</ul>"
        return html
    
    def _format_actions(self, actions: List[str]) -> str:
        if not actions: return "<p class='empty-msg'>권장 액션이 없습니다.</p>"
        html = "<div class='action-grid'>\n"
        for i, a in enumerate(actions, 1): 
            html += f"<div class='action-card'><span class='step'>{i}</span><p>{a}</p></div>\n"
        html += "</div>"
        return html
    
    def _format_data_info(self, data_info: Dict) -> str:
        html = '<div class="kpi-grid">\n'
        label_map = {
            'rows': ('총 데이터', 'rows'), 'columns': ('분석 변수', 'cols'),
            'missing': ('결측치', 'null'), 'customers': ('고객 수', 'users')
        }
        for key, value in data_info.items():
            label = label_map.get(key, (key, ''))[0]
            if isinstance(value, (int, float)): value = f"{value:,}"
            html += f'''
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
            </div>
            '''
        html += '</div>\n'
        return html

    def _format_gpt_analysis(self, text: str) -> str:
        """GPT 마크다운 텍스트를 스타일링된 HTML로 변환"""
        if not text: return ""
        
        if markdown:
            # 마크다운 확장 기능 활성화 (테이블, 펜스드 코드 등)
            content = markdown.markdown(text, extensions=['tables', 'fenced_code'])
        else:
            content = f"<pre>{text}</pre>"
            
        return f"""
        <div class="section gpt-section">
            <div class="section-header">
                <span class="ai-badge">AI INSIGHT</span>
                <h2>전문가 전략 분석</h2>
            </div>
            <div class="gpt-content markdown-body">
                {content}
            </div>
        </div>
        """

    def _get_pro_template(self) -> str:
        """전문적인 디자인의 HTML 템플릿"""
        return """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>분석 리포트</title>
    <link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #4f46e5;
            --primary-light: #eef2ff;
            --secondary: #64748b;
            --bg: #f8fafc;
            --surface: #ffffff;
            --text-main: #1e293b;
            --text-sub: #475569;
            --border: #e2e8f0;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Pretendard', sans-serif; background: var(--bg); color: var(--text-main); line-height: 1.6; }
        
        .container { max-width: 1000px; margin: 40px auto; background: var(--surface); border-radius: 16px; box-shadow: var(--shadow); overflow: hidden; }
        
        /* Header */
        .header { background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); color: white; padding: 60px 40px; text-align: center; }
        .header h1 { font-size: 2.8em; font-weight: 700; margin-bottom: 10px; letter-spacing: -0.02em; }
        .header p { font-size: 1.1em; opacity: 0.9; font-weight: 300; }
        .report-meta { margin-top: 20px; display: inline-block; background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px; font-size: 0.9em; }

        /* Sections */
        .section { padding: 40px; border-bottom: 1px solid var(--border); }
        .section:last-child { border-bottom: none; }
        .section h2 { font-size: 1.5em; color: var(--text-main); margin-bottom: 25px; display: flex; align-items: center; gap: 10px; font-weight: 700; }
        .section h2::before { content: ''; display: block; width: 6px; height: 24px; background: var(--primary); border-radius: 3px; }

        /* KPI Grid */
        .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .kpi-card { background: var(--primary-light); padding: 20px; border-radius: 12px; text-align: center; border: 1px solid #c7d2fe; }
        .kpi-label { font-size: 0.9em; color: var(--secondary); margin-bottom: 5px; text-transform: uppercase; letter-spacing: 0.05em; }
        .kpi-value { font-size: 2em; font-weight: 700; color: var(--primary); }

        /* Findings List */
        .insight-list { list-style: none; }
        .insight-list li { 
            background: #fff; border: 1px solid var(--border); padding: 15px 20px; margin-bottom: 10px; 
            border-radius: 8px; border-left: 4px solid var(--primary); font-weight: 500;
            transition: transform 0.2s;
        }
        .insight-list li:hover { transform: translateX(5px); }

        /* Action Grid */
        .action-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }
        .action-card { background: #fff7ed; border: 1px solid #ffedd5; padding: 20px; border-radius: 12px; position: relative; }
        .action-card .step { 
            position: absolute; top: -10px; left: -10px; width: 30px; height: 30px; 
            background: #f97316; color: white; border-radius: 50%; display: flex; 
            align-items: center; justify-content: center; font-weight: bold; font-size: 0.9em; 
        }
        
        /* GPT Section (Enhanced) */
        .gpt-section { background: #f8fafc; position: relative; overflow: hidden; }
        .section-header { display: flex; align-items: center; gap: 15px; margin-bottom: 25px; }
        .ai-badge { 
            background: linear-gradient(90deg, #3b82f6, #8b5cf6); color: white; 
            padding: 4px 10px; border-radius: 4px; font-size: 0.75em; font-weight: 700; 
        }
        
        .gpt-content { 
            background: white; padding: 40px; border-radius: 16px; 
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05); border: 1px solid var(--border); 
        }
        
        /* Markdown Styles inside GPT Content */
        .markdown-body h3 { font-size: 1.3em; margin-top: 1.5em; margin-bottom: 0.8em; padding-bottom: 0.5em; border-bottom: 2px solid var(--primary-light); color: var(--primary); }
        .markdown-body p { margin-bottom: 1em; color: var(--text-sub); line-height: 1.8; }
        .markdown-body strong { color: var(--text-main); background: linear-gradient(120deg, transparent 60%, #c7d2fe 60%); padding: 0 2px; }
        .markdown-body ul { padding-left: 20px; margin-bottom: 1.5em; }
        .markdown-body li { margin-bottom: 0.5em; position: relative; list-style: none; padding-left: 10px; }
        .markdown-body li::before { content: '•'; color: var(--primary); font-weight: bold; position: absolute; left: -15px; }
        .markdown-body blockquote { 
            border-left: 4px solid var(--primary); background: var(--primary-light); 
            padding: 15px 20px; border-radius: 0 8px 8px 0; margin: 1.5em 0; color: var(--text-main); font-style: italic;
        }
        .markdown-body table { width: 100%; border-collapse: collapse; margin: 1.5em 0; }
        .markdown-body th { background: var(--bg); padding: 10px; text-align: left; font-weight: 600; border-bottom: 2px solid var(--border); }
        .markdown-body td { padding: 10px; border-bottom: 1px solid var(--border); }

        /* Chart Wrapper */
        .chart-wrapper { background: white; border-radius: 12px; padding: 20px; margin-bottom: 30px; border: 1px solid var(--border); box-shadow: var(--shadow); }

        .footer { background: var(--text-main); color: #94a3b8; text-align: center; padding: 30px; font-size: 0.9em; }
        
        @media print {
            body { background: white; }
            .container { box-shadow: none; margin: 0; width: 100%; max-width: 100%; }
            .gpt-content { box-shadow: none; border: 1px solid #ccc; }
            .section { page-break-inside: avoid; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 자동 분석 리포트</h1>
            <p>{{ANALYSIS_TYPE}}</p>
            <div class="report-meta">생성일시: {{REPORT_DATE}}</div>
        </div>
        
        <div class="section">
            <h2>📋 데이터 개요</h2>
            {{DATA_INFO}}
        </div>
        
        <div class="section">
            <h2>🔍 핵심 발견사항</h2>
            {{KEY_FINDINGS}}
        </div>

        {{GPT_ANALYSIS}}
        
        <div class="section">
            <h2>💡 실행 권장사항</h2>
            {{ACTION_ITEMS}}
        </div>
        
        <div class="section">
            <h2>📊 데이터 시각화</h2>
            {{CHARTS}}
        </div>
        
        {{SUMMARY_TABLE}}
        
        <div class="footer">
            <p>Auto-Insight Platform | AI Driven Data Analytics</p>
            <p>본 리포트는 자동 생성되었으며, 의사결정의 참고 자료로 활용하시기 바랍니다.</p>
        </div>
    </div>
</body>
</html>
        """