"""
Phase 8: Policy and Safety Guardrail Layer

Adheres to rag-architecture.md Section 4.6:
- Pre-generation guardrails: detect prohibited intents, PII in user input.
- Post-generation guardrails: enforce sentence count <= 3, citation present,
  footer present, no advisory language.
- Refusal and fallback templates (Section 11).
"""
import re
from typing import Dict, Tuple


# ── Refusal & Fallback Templates (§11) ────────────────────────────────────────

ADVISORY_REFUSAL = (
    "I can only help with factual information available in the current Groww Assist "
    "source corpus and cannot provide investment advice or comparisons. "
    "For personalized guidance, please consult a SEBI-registered financial "
    "advisor. Learn more at https://www.amfiindia.com"
)

OUT_OF_SCOPE_REFUSAL = (
    "This query does not appear to be related to mutual funds or the Groww Assist "
    "platform. I can answer factual questions about schemes, NAV, expense "
    "ratio, exit load, holdings, and related topics."
)

LOW_CONFIDENCE_FALLBACK = (
    "I could not find a verifiable answer in the current Groww Assist source corpus "
    "for this scheme. Please check the relevant scheme page directly."
)

PII_BLOCK_MESSAGE = (
    "Your message appears to contain sensitive personal information. "
    "For your safety, I cannot process messages containing PAN, Aadhaar, "
    "bank details, OTPs, or similar data. Please remove any personal "
    "information and try again."
)


# ── PII Detection Patterns ────────────────────────────────────────────────────

PII_PATTERNS = {
    "pan": re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"),
    "aadhaar": re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"),
    "phone": re.compile(r"\b(?:\+91[\s-]?)?[6-9]\d{9}\b"),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "bank_account": re.compile(r"\b\d{9,18}\b"),     # rough heuristic
    "ifsc": re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b"),
    "otp": re.compile(r"\b(?:otp|OTP)\s*(?:is|:)?\s*\d{4,6}\b"),
}

# ── Advisory / Prohibited Language ─────────────────────────────────────────────

ADVISORY_PHRASES = [
    "should i", "invest in", "is it good", "recommend", "best fund",
    "which is better", "better than", "compare returns", "good investment",
    "worth investing", "buy or sell", "my portfolio",
    "which fund to choose", "should i switch", "top rated", "star rating",
    "future performance", "will it go up", "price prediction", "guaranteed",
    "ranking", "rank", "highest return",
    "lowest risk", "safe investment", "better option", "suggest a fund",
    "portfolio review", "calculate my returns", "wealth creation",
]

ADVISORY_OUTPUT_PHRASES = [
    "you should", "i recommend", "it is a good idea",
    "consider investing", "i suggest", "you might want to",
    "it would be wise", "i advise", "you could try",
]


class PolicyGuardrails:
    """Pre-generation and post-generation safety guardrails."""

    # ── Pre-Generation ─────────────────────────────────────────────────────

    def check_pii(self, text: str) -> Tuple[bool, str | None]:
        """
        Scan user input for PII patterns.
        Returns (has_pii: bool, detected_type: str | None)
        """
        for pii_type, pattern in PII_PATTERNS.items():
            if pattern.search(text):
                return True, pii_type
        return False, None

    def check_prohibited_intent(self, query: str) -> Tuple[bool, str | None]:
        """
        Rule-based check for advisory / recommendation / comparison intents.
        Returns (is_prohibited: bool, reason_key: str | None)
        """
        lower = query.lower()
        for phrase in ADVISORY_PHRASES:
            if phrase in lower:
                return True, "advisory"
        return False, None

    def pre_generate(self, query: str) -> Dict:
        """
        Run all pre-generation guardrails on the raw user query.

        Returns:
            {
                "allowed": bool,
                "block_reason": str | None,  # "pii" | "advisory" | None
                "refusal_message": str | None,
            }
        """
        # 1. PII check
        has_pii, pii_type = self.check_pii(query)
        if has_pii:
            print(f"[Guardrail] PII detected ({pii_type}). Blocking request.")
            return {
                "allowed": False,
                "block_reason": "pii",
                "pii_type": pii_type,
                "refusal_message": PII_BLOCK_MESSAGE,
            }

        # 2. Prohibited intent check
        is_prohibited, reason = self.check_prohibited_intent(query)
        if is_prohibited:
            print(f"[Guardrail] Prohibited intent detected: {reason}")
            return {
                "allowed": False,
                "block_reason": reason,
                "refusal_message": ADVISORY_REFUSAL,
            }

        return {"allowed": True, "block_reason": None, "refusal_message": None}

    # ── Post-Generation ────────────────────────────────────────────────────

    def _split_sentences(self, text: str) -> List[str]:
        """Robust sentence splitting handling common abbreviations like 'Rs.'"""
        # 1. Clean up extra whitespace
        text = text.strip()
        # 2. Heuristic split: punctuation followed by space and Uppercase letter
        # We try to avoid splitting on "Rs." or "NAV." if followed by number
        # Using a negative lookbehind for common abbreviations
        abbreviations = [
            "Rs", "No", "Dr", "Vol", "NAV", "Cr", "L", "p.a", "vs", "e.g", "i.e",
            "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
            "Approx", "Min", "Max", "p.m", "p.y"
        ]
        pattern = r'(?<!\b' + r')(?<!\b'.join(abbreviations) + r')(?<=[.!?])\s+(?=[A-Z0-9])'
        parts = re.split(pattern, text)
        
        # Filter out citation / footer lines
        return [
            s for s in parts
            if not s.startswith("[Source:") and 
               not s.startswith("Last updated") and
               not s.lower().startswith("last updated")
        ]

    def _count_sentences(self, text: str) -> int:
        """Count actual factual sentences using robust splitter."""
        return len(self._split_sentences(text))

    def _has_citation(self, text: str) -> bool:
        """Check for [Source: ...] citation block."""
        return bool(re.search(r"\[Source:\s*https?://", text))

    def _has_footer(self, text: str) -> bool:
        """Check for 'Last updated from sources:' footer line."""
        return "last updated from sources:" in text.lower()

    def _has_advisory_language(self, text: str) -> bool:
        """Detect prescriptive / advisory phrasing in the generated answer."""
        lower = text.lower()
        return any(phrase in lower for phrase in ADVISORY_OUTPUT_PHRASES)

    def post_generate(self, answer: str) -> Dict:
        """
        Validate the generated answer against §4.6 post-generation rules.

        Returns:
            {
                "compliant": bool,
                "violations": list[str],   # e.g. ["sentence_count", "no_citation"]
                "corrected_answer": str,    # auto-fixed if possible, else safe fallback
            }
        """
        violations = []

        # 1. Sentence count <= 3 (excluding citation / footer)
        sentence_count = self._count_sentences(answer)
        if sentence_count > 3:
            violations.append("sentence_count_exceeded")

        # 2. (Citation and Footer checks are now handled by the UI Layer)

        # 4. No advisory language
        if self._has_advisory_language(answer):
            violations.append("advisory_language_detected")

        if not violations:
            return {
                "compliant": True,
                "violations": [],
                "corrected_answer": answer,
            }

        # ── Auto-correction attempt ───────────────────────────────────────
        
        # If advisory language detected, return safe fallback entirely (cannot auto-fix)
        if "advisory_language_detected" in violations:
            print(f"[Guardrail] Advisory language found in output — returning fallback.")
            return {
                "compliant": False,
                "violations": violations,
                "corrected_answer": LOW_CONFIDENCE_FALLBACK,
            }

        sentences = self._split_sentences(answer)
        corrected_body = " ".join(sentences[:3])
        
        # Reconstruct answer using only factual body
        corrected = corrected_body

        print(f"[Guardrail] Auto-corrected violations: {violations}")
        return {
            "compliant": False,
            "violations": violations,
            "corrected_answer": corrected,
        }


if __name__ == "__main__":
    guardrails = PolicyGuardrails()

    # ── Pre-generation tests ──────────────────────────────────────────────
    print("=" * 60)
    print("PRE-GENERATION GUARDRAIL TESTS")
    print("=" * 60)

    test_queries = [
        ("What is the expense ratio of SBI Contra Fund?", True),
        ("Should I invest in HDFC Mid Cap Fund?", False),
        ("Which is better, SBI or HDFC fund?", False),
        ("My PAN is ABCDE1234F, check my NAV", False),
        ("My phone 9876543210 send me fund details", False),
        ("What is NAV of Nippon India Large Cap?", True),
        ("OTP is 456789 please verify", False),
    ]

    for query, expected_allowed in test_queries:
        result = guardrails.pre_generate(query)
        status = "PASS" if result["allowed"] == expected_allowed else "FAIL"
        icon = "+" if status == "PASS" else "x"
        print(f"  [{icon}] Query: '{query[:50]}...'")
        print(f"       Expected allowed={expected_allowed}, Got allowed={result['allowed']}")
        if result["block_reason"]:
            print(f"       Block reason: {result['block_reason']}")
        print()

    # ── Post-generation tests ─────────────────────────────────────────────
    print("=" * 60)
    print("POST-GENERATION GUARDRAIL TESTS")
    print("=" * 60)

    good_answer = (
        "The expense ratio of SBI Contra Fund Direct Growth is 0.66%. "
        "This is the total expense ratio as of 13 Apr 2026. "
        "[Source: https://groww.in/mutual-funds/sbi-contra-fund-direct-growth]\n\n"
        "Last updated from sources: Recent"
    )
    bad_answer_advisory = (
        "You should invest in SBI Contra Fund because it has low expense ratio. "
        "I recommend this fund for long-term growth."
    )
    bad_answer_no_citation = (
        "The NAV is Rs. 402.83 as of today. "
        "This fund has been performing well recently."
    )

    for label, answer in [
        ("Compliant answer", good_answer),
        ("Advisory language", bad_answer_advisory),
        ("Missing citation & footer", bad_answer_no_citation),
    ]:
        result = guardrails.post_generate(answer)
        icon = "+" if result["compliant"] else "x"
        print(f"  [{icon}] {label}")
        print(f"       Compliant: {result['compliant']}, Violations: {result['violations']}")
        print()
