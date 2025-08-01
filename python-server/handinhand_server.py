#!/usr/bin/env python3
"""
Hand in Hand Python Server - uv 실행용 진입점
"""

import sys
import os

# 프로젝트 루트를 Python path에 추가
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 기존 서버 모듈 import
from cmd.server import main

if __name__ == "__main__":
    main()