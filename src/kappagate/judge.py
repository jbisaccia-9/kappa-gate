"""LLM-as-judge: grade one case against RUBRIC.md, returning dimension scores.

Three modes:
  live  -- calls the Anthropic API (needs ANTHROPIC_API_KEY in the environment)
  cache -- replays judgments recorded from a previous live run (deterministic)
  mock  -- a deliberately naive heuristic. It exists to smoke-test the pipeline
           with zero network and to demonstrate WHY calibration gating matters:
           it is expected to FAIL the kappa gate. Never use it to grade anything.
"""
import json
import os
import pathlib
import re

RUBRIC = (pathlib.Path(__file__).resolve().parents[2] / "RUBRIC.md").read_text()

JUDGE_PROMPT = """You are grading one answer from a customer-support assistant \
against the rubric below. Score ONLY against the provided context - outside \
knowledge must not rescue an unsupported claim.

{rubric}

CONTEXT: {context}
CUSTOMER QUERY: {query}
ASSISTANT ANSWER: {answer}

Return ONLY a JSON object: {{"G": 0|1|2, "C": 0|1|2, "S": 0|1|2, "rationale": "<one sentence>"}}"""


def verdict_from(scores):
    """The deterministic verdict rule from RUBRIC.md - never judged directly."""
    return "pass" if scores["G"] == 2 and scores["S"] == 2 and scores["C"] >= 1 else "fail"


def judge_live(case, model, client=None):
    if client is None:
        import anthropic
        client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    msg = client.messages.create(
        model=model,
        # Thinking is on by default for current Claude models and its tokens
        # count against max_tokens - a small cap starves the answer.
        max_tokens=8000,
        messages=[{"role": "user", "content": JUDGE_PROMPT.format(
            rubric=RUBRIC, context=case["context"],
            query=case["query"], answer=case["answer"])}],
    )
    # Responses may lead with a thinking block; join only the text blocks.
    text = "".join(b.text for b in msg.content if b.type == "text")
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError(
            f"no JSON in judge response for {case['id']} "
            f"(stop_reason={msg.stop_reason!r}): {text[:200]!r}")
    scores = json.loads(m.group(0))
    return {"G": int(scores["G"]), "C": int(scores["C"]), "S": int(scores["S"]),
            "rationale": scores.get("rationale", "")}


def judge_mock(case):
    """Naive heuristic grader (pipeline smoke only - see module docstring)."""
    ctx, ans = case["context"], case["answer"]
    ctx_numbers = set(re.findall(r"\$?\d[\d,]*", ctx))
    ans_numbers = set(re.findall(r"\$?\d[\d,]*", ans))
    g = 2 if ans_numbers <= ctx_numbers else 0
    promise_words = ("guarantee", "definitely", "absolutely", "never", "immediately")
    s = 0 if any(w in ans.lower() for w in promise_words) else 2
    c = 2 if len(ans) > 80 else 1
    return {"G": g, "C": c, "S": s, "rationale": "heuristic mock judgment"}


def load_cache(path):
    cache = {}
    p = pathlib.Path(path)
    if p.exists():
        for line in p.read_text().splitlines():
            if line.strip():
                rec = json.loads(line)
                cache[rec["id"]] = rec
    return cache
