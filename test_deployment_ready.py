"""
Deployment Readiness Test
DAY 32: 배포 전 최종 확인 스크립트
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """파일 존재 여부 확인"""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} 누락: {filepath}")
        return False

def check_file_not_exists(filepath, description):
    """파일이 존재하지 않아야 함 (보안)"""
    if not Path(filepath).exists():
        print(f"✅ {description} (안전): {filepath}")
        return True
    else:
        print(f"⚠️  {description} 발견 (주의!): {filepath}")
        return False

def check_gitignore():
    """gitignore 확인"""
    try:
        with open('.gitignore', 'r', encoding='utf-8') as f:
            content = f.read()

        checks = {
            '.env': '.env' in content,
            'secrets.toml': 'secrets.toml' in content,
            'venv/': 'venv/' in content,
        }

        all_pass = True
        for item, exists in checks.items():
            if exists:
                print(f"✅ .gitignore에 '{item}' 포함됨")
            else:
                print(f"❌ .gitignore에 '{item}' 누락!")
                all_pass = False

        return all_pass
    except Exception as e:
        print(f"❌ .gitignore 확인 실패: {e}")
        return False

def check_requirements():
    """requirements.txt 확인"""
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            content = f.read()

        # 제외되어야 할 패키지
        excluded = ['selenium', 'webdriver-manager', 'undetected-chromedriver']
        excluded_found = [pkg for pkg in excluded if pkg in content and not content.find(f'# {pkg}') > -1]

        if excluded_found:
            print(f"⚠️  크롤링 패키지가 주석 처리되지 않음: {excluded_found}")
            return False
        else:
            print(f"✅ 크롤링 패키지 제외됨 (정상)")

        # 필수 패키지
        required = ['streamlit', 'pandas', 'plotly', 'scikit-learn', 'openai']
        missing = [pkg for pkg in required if pkg not in content]

        if missing:
            print(f"❌ 필수 패키지 누락: {missing}")
            return False
        else:
            print(f"✅ 필수 패키지 모두 포함됨")

        return True
    except Exception as e:
        print(f"❌ requirements.txt 확인 실패: {e}")
        return False

def main():
    """배포 준비 상태 확인"""
    # UTF-8 출력 설정
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("=" * 70)
    print("Streamlit Cloud 배포 준비 상태 확인")
    print("=" * 70)

    all_checks = []

    # 1. 필수 파일 존재 확인
    print("\n[1/5] 필수 파일 확인")
    print("-" * 70)
    all_checks.append(check_file_exists('app.py', '메인 앱'))
    all_checks.append(check_file_exists('requirements.txt', '의존성'))
    all_checks.append(check_file_exists('.streamlit/config.toml', 'Streamlit 설정'))
    all_checks.append(check_file_exists('.streamlit/secrets.toml.example', 'Secrets 템플릿'))
    all_checks.append(check_file_exists('DEPLOYMENT.md', '배포 가이드'))
    all_checks.append(check_file_exists('README.md', 'README'))

    # 2. 민감 파일 보안 확인
    print("\n[2/5] 보안 확인 (민감 파일 제외)")
    print("-" * 70)
    all_checks.append(check_file_not_exists('.streamlit/secrets.toml', 'Secrets 파일'))

    # 3. .gitignore 확인
    print("\n[3/5] .gitignore 확인")
    print("-" * 70)
    all_checks.append(check_gitignore())

    # 4. requirements.txt 확인
    print("\n[4/5] requirements.txt 확인")
    print("-" * 70)
    all_checks.append(check_requirements())

    # 5. 모듈 폴더 확인
    print("\n[5/5] 모듈 폴더 확인")
    print("-" * 70)
    modules = [
        'modules/data_loader.py',
        'modules/preprocessor.py',
        'modules/rfm_analyzer.py',
        'modules/sales_analyzer.py',
        'modules/visualizer.py',
        'modules/report_generator.py',
        'modules/gpt_analyzer.py',
    ]
    for module in modules:
        all_checks.append(check_file_exists(module, f'모듈'))

    # 최종 결과
    print("\n" + "=" * 70)
    total = len(all_checks)
    passed = sum(all_checks)

    if passed == total:
        print(f"✅ 모든 확인 통과! ({passed}/{total})")
        print("=" * 70)
        print("\n🎉 배포 준비 완료!")
        print("\n다음 단계:")
        print("  1. https://share.streamlit.io 접속")
        print("  2. GitHub 계정으로 로그인")
        print("  3. 'New app' 클릭")
        print("  4. Repository: JungMoonYoung/auto-insight-platform")
        print("  5. Branch: main")
        print("  6. Main file: app.py")
        print("  7. Secrets 설정:")
        print("     OPENAI_API_KEY = \"your-api-key\"")
        print("     deployed = true")
        print("  8. Deploy! 클릭")
        print("\n자세한 가이드: DEPLOY_NOW.md 참조")
        return 0
    else:
        print(f"⚠️  일부 확인 실패: {passed}/{total} 통과")
        print("=" * 70)
        print("\n❌ 배포 전 문제를 해결하세요.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
