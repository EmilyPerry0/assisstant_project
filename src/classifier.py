import re

INTENT_PATTERNS = {
    'weather': re.compile(r'\b(weather|forecast|temperature|rain|snow|jacket|umbrella)\b', re.IGNORECASE),
    'timer': re.compile(r'\b(timer|countdown|minutes|remind me in|set a timer|start a|timers|time earns|minute)\b', re.IGNORECASE),
    'alarm': re.compile(r'\b(alarm|wake me|wake up|remind me at|set an alarm|alarms)\b', re.IGNORECASE),
}

TIMER_SUBINTENT_PATTERNS = {
    'create': re.compile(r'\b(set|create|start|add|make)\b', re.IGNORECASE),
    'list': re.compile(r'\b(list|show|what timers|any timers|how many)\b', re.IGNORECASE),
    'check': re.compile(r'\b(time|left|remaining|how long|left on timer)\b', re.IGNORECASE),
    'delete': re.compile(r'\b(delete|cancel|remove|clear)\b', re.IGNORECASE),
}


ALARM_SUBINTENT_PATTERNS = {
    'create': re.compile(r'\b(set|create|add|make|schedule|start)\b', re.IGNORECASE),
    'delete': re.compile(r'\b(delete|remove|cancel|clear|stop)\b', re.IGNORECASE),
    'list': re.compile(r'\b(list|show|view|see|what alarms|any alarms)\b', re.IGNORECASE),
}

def detect_intent(text: str) -> str:
    for intent, pattern in INTENT_PATTERNS.items():
        if pattern.search(text):
            return intent
    return 'fallback'  # unknown intent

def detect_timer_sub_intent(text: str) -> str:
    for action, pattern in TIMER_SUBINTENT_PATTERNS.items():
        if pattern.search(text):
            return action
    return 'unknown'

def detect_alarm_sub_intent(text: str) -> str:
    for action, pattern in ALARM_SUBINTENT_PATTERNS.items():
        if pattern.search(text):
            return action
    return 'unknown'

