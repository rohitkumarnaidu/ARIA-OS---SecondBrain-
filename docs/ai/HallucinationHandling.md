# Hallucination Handling — Second Brain OS

## Document Control

| Field | Value |
|---|---|
| **Document ID** | AI-HAL-002 |
| **Version** | 1.0.0 |
| **Status** | Approved |
| **Date** | 2026-07-10 |
| **Classification** | Internal |
| **Owner** | Developer |
| **Related Docs** | [AIEvaluation.md](AIEvaluation.md), [Guardrails.md](Guardrails.md), [RAGArchitecture.md](RAGArchitecture.md) |

---

## 1. Executive Summary

Hallucinations in LLM outputs are categorized into four types: factual, temporal, logical, and source. The Second Brain OS employs a multi-layer detection and mitigation strategy: prompt engineering, RAG-based grounding, confidence scoring, and runtime validation. Any detected hallucination triggers graceful fallback to algorithmic results or user-facing uncertainty expressions.

---

## 2. Hallucination Types

| Type | Definition | Example | Risk |
|---|---|---|---|
| **Factual** | Incorrect facts or data | "Your GPA is 4.0" (actual: 3.2) | High |
| **Temporal** | Wrong time/dates | "Your deadline is next week" (actual: tomorrow) | High |
| **Logical** | Contradictory reasoning | "You have 5 tasks due today, none are urgent" (3 are urgent) | Medium |
| **Source** | Attributing info to wrong source | "Your professor said..." (user never mentioned this) | Medium |

---

## 3. Detection Pipeline

```mermaid
graph TD
    OUTPUT["LLM Output"] --> DETECT{Detection Layer}
    
    DETECT --> FV[Factual Verification<br/>Query database for claims<br/>Cross-reference user data]
    DETECT --> SG[Source Grounding<br/>Check source citations<br/>Verify against context]
    DETECT --> TC[Temporal Check<br/>Validate date references<br/>Compare with actual dates]
    DETECT --> LC[Logical Consistency<br/>Check for contradictions<br/>Verify against known state]
    
    FV --> RESULT{Result}
    SG --> RESULT
    TC --> RESULT
    LC --> RESULT
    
    RESULT -->|"All clear"| PASS[Return output]
    RESULT -->|"Low confidence"| MITIGATE[Apply mitigation]
    RESULT -->|"Hallucination detected"| FALLBACK[Fallback to algorithmic result]
    
    MITIGATE --> MIT1[Source citation<br/>"Based on your data..."]
    MITIGATE --> MIT2[Uncertainty expression<br/>"It appears that..."]
    MITIGATE --> MIT3[Confidence disclosure<br/>"I'm not entirely sure..."]

    style PASS fill:#00FFA3,color:#000
    style FALLBACK fill:#EF4444,color:#fff
```

---

## 4. Detection Methods

### 4.1 Factual Verification

```python
async def verify_factual_claims(output_text: str, user_id: str) -> dict:
    """Verify factual claims against Supabase data."""
    claims = extract_claims(output_text)
    verified = []

    for claim in claims:
        # Query database for ground truth
        if "tasks" in claim.entity:
            data = await supabase.table("tasks")\
                .select("count")\
                .eq("user_id", user_id)\
                .execute()
            ground_truth = data.data[0]["count"]
        confidence = match_claim_to_data(claim, ground_truth)
        verified.append({"claim": claim, "confidence": confidence})

    return verified
```

### 4.2 Source Grounding

| Technique | Implementation | Effectiveness |
|---|---|---|
| Context window check | Verify all claims reference provided context | 90% |
| Citation extraction | Parse citations from agent output | 85% |
| RAG relevance scoring | Embedding similarity to source documents | 95% |

### 4.3 Temporal Validation

```python
def validate_temporal_claims(output: dict) -> list[str]:
    """Check date/time claims against actual data."""
    errors = []
    now = datetime.now()

    if "deadline" in output:
        if output["deadline"] < now:
            errors.append("Deadline is in the past")

    if "days_remaining" in output:
        # Recalculate from actual data
        pass

    return errors
```

---

## 5. Prevention Strategies

| Strategy | Layer | Effort | Impact |
|---|---|---|---|
| **Prompt engineering** | Input | Low | 40% reduction |
| **RAG (grounding)** | Context | Medium | 60% reduction |
| **Constrained decoding** | Output | High | 80% reduction |
| **Few-shot examples** | Input | Low | 30% reduction |
| **Temperature control** | Config | Low | 20% reduction |

**Recommended configuration:**
```python
LLM_CONFIG = {
    "temperature": 0.3,      # Lower = more deterministic
    "top_p": 0.9,            # Nucleus sampling
    "frequency_penalty": 0.2, # Discourage repetition
    "presence_penalty": 0.1,  # Encourage covering all required points
}
```

---

## 6. Response Strategies

| Detection Result | User-Facing Response | Internal Action |
|---|---|---|
| Confirmed accurate | Normal response | Log confidence score |
| Low confidence (0.5-0.7) | "Based on your data, it appears that..." | Log as low-confidence |
| High suspicion (< 0.5) | Fallback to algorithmic result | Log hallucination attempt |
| Clear hallucination | Error message "I couldn't verify that information" | Alert, retry |

---

## 7. Related Documents

| Document | Description |
|---|---|
| [AIEvaluation.md](AIEvaluation.md) | Quality evaluation dimensions |
| [RAGArchitecture.md](RAGArchitecture.md) | Retrieval-augmented generation |
| [Guardrails.md](Guardrails.md) | Safety guardrails |
