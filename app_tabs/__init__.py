# tabs/__init__.py
# 각 탭은 render_* 함수를 export합니다.
from app_tabs.coaching_guide_tab import render_coaching_guide_tab
from app_tabs.coaching_log_tab import render_coaching_log_tab

__all__ = ["render_coaching_guide_tab", "render_coaching_log_tab"]