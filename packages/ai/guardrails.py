import re
import json
from typing import Optional


_PROFANITY_SET: set[str] = {
    "fuck", "shit", "ass", "bitch", "dick", "cock", "cunt", "bastard",
    "damn", "piss", "slut", "whore", "douche", "motherfucker", "asshole",
    "bullshit", "crap", "dickhead", "prick", "twat", "wanker", "bollocks",
    "arse", "bloody", "bugger", "cocksucker", "dipshit", "faggot", "nigger",
    "retard", "spic", "kike", "chink", "gook", "wetback", "raghead",
    "cameljockey", "sandnigger", "beaner", "dago", "honky", "cracker",
    "redneck", "tranny", "heeb", "shylock", "gringo", "coon", "sambo",
    "jigaboo", "skank", "bimbo", "milf", "porn", "porno",
    "bestiality", "snuff", "childporn", "childrenporn",
}

_PROFANITY_LONG: list[str] = [w for w in _PROFANITY_SET if len(w) >= 4]
_PROFANITY_SHORT: list[str] = [w for w in _PROFANITY_SET if len(w) < 4]
_PROFANITY_PATTERN: str = ""
if _PROFANITY_LONG:
    _PROFANITY_PATTERN += "(?:" + "|".join(re.escape(w) for w in _PROFANITY_LONG) + ")"
if _PROFANITY_SHORT:
    if _PROFANITY_PATTERN:
        _PROFANITY_PATTERN += "|"
    _PROFANITY_PATTERN += "(?:" + "|".join(r"\b" + re.escape(w) + r"\b" for w in _PROFANITY_SHORT) + ")"
_PROFANITY_COMPILED: re.Pattern = re.compile(_PROFANITY_PATTERN, re.IGNORECASE)

_PROMPT_INJECTION_PATTERNS: list[tuple[str, str]] = [
    ("ignore_prior", r"ignore\s+(all\s+)?(previous|prior|above|earlier\s+)?\s*(instructions|directions|prompts|commands|messages|context)"),
    ("disregard_prior", r"disregard\s+(all\s+)?(previous|prior|above|earlier\s+)?\s*(instructions|directions|prompts|commands|messages)"),
    ("forget_prior", r"forget\s+(all\s+)?(previous|prior|above|earlier\s+)?\s*(instructions|directions|prompts|commands)"),
    ("roleplay_new", r"(you\s+are\s+(now|no\s+longer)\s+(a|an|the)\s+|\bact\s+as\s+(if\s+)?(you\s+are\s+)?|pretend\s+(to\s+be|that\s+you\s+are)|from\s+now\s+on\s+,\s*(you\s+are\s+)?)"),
    ("override_system", r"override\s+(mode|protocol|system|configuration|settings)"),
    ("jailbreak_dan", r"\bdan\b|\bdo\s+anything\s+now\b|no\s+(restrictions|limitations|boundaries|rules|filter|guardrails)"),
    ("bypass_restrictions", r"(you\s+(must|will|have\s+to)\s+(ignore|bypass|circumvent|by-pass))"),
    ("uncensored_response", r"respond\s+(with|using)\s+(no\s+)?(restrictions|limitations|filtering|censorship|guardrails)"),
    ("extract_system_prompt", r"(\bwhat\s+(is\s+)?your\s+(system\s+)?prompt\b|reveal\s+(your\s+)?(system\s+)?prompt|output\s+(your\s+)?(system\s+)?(prompt|instruction)|print\s+(your\s+)?(system\s+)?prompt|display\s+(the\s+)?(system\s+)?prompt)"),
    ("repeat_attack", r"repeat\s+(after\s+me|the\s+(words|text|sentence|prompt)\s+above|the\s+initial\s+prompt)"),
    ("delimiter_attack", r"-{3,}\s*(start|end|begin|finish|instruction|system)\s*-{3,}"),
    ("ignore_above", r"ignore\s+the\s+above"),
]

_PII_PATTERNS: dict[str, re.Pattern] = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "phone": re.compile(r"\b(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
}

_INVISIBLE_UNICODE: re.Pattern = re.compile(
    "[\u200b\u200c\u200d\u2060\u2061\u2062\u2063\u2064\u2066\u2067\u2068\u2069"
    "\ufeff\ufffe\u00ad\u034f\u061c\u115f\u1160\u17b4\u17b5"
    "\u180e\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009"
    "\u200a\u2028\u2029\u202a\u202b\u202c\u202d\u202e\u202f]"
)

_HTML_SCRIPT: re.Pattern = re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
_HTML_ONEVENT: re.Pattern = re.compile(r"\bon\w+\s*=\s*['\"][^'\"]*['\"]", re.IGNORECASE)
_JS_PROTOCOL: re.Pattern = re.compile(r"javascript\s*:", re.IGNORECASE)

_HALLUCINATION_MARKERS: list[str] = [
    "i think", "i believe", "i'm not sure", "maybe", "perhaps",
    "it might be", "it could be", "as far as i know", "to the best of my knowledge",
    "i'm not certain", "i don't know", "i'm not aware",
    "according to my knowledge", "in my understanding",
    "it is possible that", "it seems that", "likely", "probably", "possibly",
    "i cannot confirm", "i have no information", "i dont have",
    "i'm not entirely sure", "it appears that",
]

_REFUSAL_PATTERNS: list[str] = [
    "i cannot", "i can't", "i'm not able to", "i am not able to",
    "i'm sorry", "i am sorry", "sorry, but", "i apologize",
    "as an ai", "as a language model", "i'm an ai",
    "i cannot assist", "i cannot provide", "i cannot help",
    "i'm not permitted", "i am not permitted", "it's not appropriate",
    "against my guidelines", "against guidelines",
    "i cannot fulfill", "i cannot complete", "i cannot answer",
]

_WEASEL_WORDS: list[str] = [
    "arguably", "basically", "essentially", "practically",
    "virtually", "quite", "rather", "somewhat",
    "supposedly", "allegedly", "reportedly",
    "in general", "in most cases", "typically",
    "usually", "often", "sometimes", "occasionally",
    "largely", "mostly", "broadly",
]

_CONTENT_VIOLATION_TOPICS: list[str] = [
    "how to make a bomb", "how to build a weapon", "explosive device",
    "manufacturing drugs", "synthesize narcotics", "methamphetamine recipe",
    "self-harm methods", "suicide methods", "how to commit suicide",
    "illegal activity", "illegal acts", "bypass security",
    "hack into", "unauthorized access", "steal credentials",
    "credit card fraud", "identity theft", "phishing template",
]

_SENSITIVITY_LEVELS: dict[str, float] = {
    "low": 0.6,
    "medium": 0.4,
    "high": 0.2,
    "maximum": 0.1,
}


class Guardrails:
    """Input/output validation and sanitization for LLM interactions."""

    def __init__(self, sensitivity: str = "medium", max_input_length: int = 32000, max_output_length: int = 32000):
        self.sensitivity = _SENSITIVITY_LEVELS.get(sensitivity, 0.5)
        self.sensitivity_name = sensitivity if sensitivity in _SENSITIVITY_LEVELS else "medium"
        self.max_input_length = max_input_length
        self.max_output_length = max_output_length

    def validate_input(self, text: str) -> dict:
        """Check input for prompt injection, malicious content, and PII leakage."""
        issues: list[str] = []
        risk_score: float = 0.0

        if not text or not text.strip():
            return {"safe": True, "issues": [], "risk_score": 0.0}

        if len(text) > self.max_input_length:
            issues.append(f"input_exceeds_max_length:{self.max_input_length}")
            risk_score += 0.5

        for name, pattern in _PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(f"prompt_injection:{name}")
                risk_score += 0.5

        profanity_matches = _PROFANITY_COMPILED.findall(text)
        if profanity_matches:
            unique_profanity = list(set(m.lower() for m in profanity_matches))
            issues.append(f"profanity_detected:{','.join(unique_profanity[:5])}")
            risk_score += 0.4

        for pii_type, pattern in _PII_PATTERNS.items():
            matches = pattern.findall(text)
            if matches:
                issues.append(f"pii_detected:{pii_type}:{len(matches)}_occurrences")
                risk_score += 0.4

        if re.search(_HTML_SCRIPT, text):
            issues.append("html_script_tag_detected")
            risk_score += 0.5

        if re.search(_JS_PROTOCOL, text):
            issues.append("javascript_protocol_detected")
            risk_score += 0.5

        safe = risk_score < self.sensitivity
        return {"safe": safe, "issues": issues, "risk_score": round(min(risk_score, 1.0), 4)}

    def validate_output(self, text: str, input_text: Optional[str] = None) -> dict:
        """Check LLM output for hallucination markers, policy violations, and refusals."""
        issues: list[str] = []
        risk_score: float = 0.0

        if not text or not text.strip():
            return {"safe": True, "issues": [], "risk_score": 0.0}

        text_lower = text.lower()

        hallucination_markers_found: list[str] = []
        for marker in _HALLUCINATION_MARKERS:
            if marker in text_lower:
                hallucination_markers_found.append(marker)
        if hallucination_markers_found:
            issues.append(f"hallucination_markers:{','.join(hallucination_markers_found[:3])}")
            risk_score += 0.4

        weasel_words_found: list[str] = []
        for word in _WEASEL_WORDS:
            if word in text_lower:
                weasel_words_found.append(word)
        if weasel_words_found:
            issues.append(f"weasel_words:{','.join(weasel_words_found[:3])}")
            risk_score += 0.4

        for topic in _CONTENT_VIOLATION_TOPICS:
            if topic in text_lower:
                issues.append(f"content_policy_violation:{topic}")
                risk_score += 0.5

        refusal_count = 0
        for pattern in _REFUSAL_PATTERNS:
            if pattern in text_lower:
                refusal_count += 1
        if refusal_count >= 2:
            issues.append(f"refusal_detected:{refusal_count}_patterns_matched")
            risk_score += 0.5

        if text.strip().startswith("{") or text.strip().startswith("["):
            try:
                json.loads(text)
            except json.JSONDecodeError:
                issues.append("invalid_json_output")
                risk_score += 0.5

        if input_text and not text_lower.startswith(("i cannot", "i can't", "sorry")):
            input_lower = input_text.lower()
            refusal_triggers = ["refuse", "cannot", "can't"]
            if any(t in input_lower for t in refusal_triggers):
                pass

        safe = risk_score < self.sensitivity
        return {"safe": safe, "issues": issues, "risk_score": round(min(risk_score, 1.0), 4)}

    def sanitize_input(self, text: str) -> str:
        """Strip or escape dangerous content from user input."""
        if not text:
            return ""

        result = _INVISIBLE_UNICODE.sub(" ", text)

        result = _HTML_SCRIPT.sub(" ", result)

        result = _JS_PROTOCOL.sub(" ", result)

        result = re.sub(r"\s+", " ", result).strip()

        if len(result) > self.max_input_length:
            result = result[:self.max_input_length]

        return result

    def sanitize_output(self, text: str) -> str:
        """Clean LLM output by removing excessive formatting and hallucinated citations."""
        if not text:
            return ""

        result = text

        result = re.sub(r"\n{3,}", "\n\n", result)

        result = re.sub(r" {2,}", " ", result)

        result = re.sub(r"#{4,}", "###", result)

        result = re.sub(r"\*\*\*\*+", "***", result)

        result = re.sub(r"\[Source:\s*[^\]]+\]", "", result)
        result = re.sub(r"\(Source:\s*[^)]+\)", "", result)
        result = re.sub(r"^\d+\.\s*\[.*?\]\(.*?\)\s*$", "", result, flags=re.MULTILINE)

        result = re.sub(r"\r\n", "\n", result)
        result = re.sub(r"\r", "\n", result)

        result = result.strip()

        if len(result) > self.max_output_length:
            result = result[:self.max_output_length]

        return result

    def check_prompt_injection(self, messages: list[dict]) -> dict:
        """Check chat history for injection attacks across all messages."""
        per_message: list[dict] = []
        cumulative_issues: list[str] = []
        max_risk: float = 0.0
        injection_detected: bool = False

        for i, msg in enumerate(messages):
            content = msg.get("content", "")
            role = msg.get("role", "unknown")
            if not content or not isinstance(content, str):
                per_message.append({"index": i, "role": role, "safe": True, "issues": [], "risk_score": 0.0})
                continue

            result = self.validate_input(content)
            entry = {
                "index": i,
                "role": role,
                "safe": result["safe"],
                "issues": result["issues"],
                "risk_score": result["risk_score"],
            }
            per_message.append(entry)

            if not result["safe"]:
                injection_detected = True
                cumulative_issues.extend(result["issues"])
                if result["risk_score"] > max_risk:
                    max_risk = result["risk_score"]

        context_text = " ".join(
            m.get("content", "") for m in messages[-3:] if isinstance(m.get("content"), str)
        )
        escalation_issues: list[str] = []
        if re.search(
            r"(ignore|forget|disregard)\s+(all|the|previous|everything)",
            context_text,
            re.IGNORECASE,
        ):
            escalation_issues.append("escalation_attack:context_manipulation_detected")
            injection_detected = True
            max_risk = max(max_risk, 0.6)

        return {
            "safe": not injection_detected,
            "per_message": per_message,
            "cumulative_issues": cumulative_issues + escalation_issues,
            "max_risk_score": round(max_risk, 4),
        }


guardrails = Guardrails()
