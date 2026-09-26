"""
intent_matcher.py
Figures out WHAT the user wants to do, from natural language.

Approach: TF-IDF + cosine similarity.
- TF-IDF turns each sentence into a list of numbers (a "vector")
  based on which words appear and how important/rare they are.
- Cosine similarity measures how close two vectors are (0 = totally
  different, 1 = identical meaning-wise).

For each intent (add, list, upcoming, update_status, delete, help),
we store a handful of EXAMPLE phrases. When the user types something,
we compare it against every example and return the intent whose
examples are the closest match.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Each intent maps to a list of example phrases a user might type.
# More varied examples = better matching for real questions later.
INTENT_EXAMPLES = {
    "add": [
        "add a new application",
        "I applied to a company",
        "track a new internship",
        "log a new application",
        "add internship for company",
        "I want to add an application",
    ],
    "list_all": [
        "show all my applications",
        "list my applications",
        "what applications do I have",
        "show everything I applied to",
        "display all applications",
    ],
    "list_pending": [
        "show pending applications",
        "what's still pending",
        "which ones are pending",
        "show me what I'm waiting on",
        "show me what's pending",
        "can you show me what's pending",
        "what applications are still pending",
    ],
    "upcoming": [
        "what's due soon",
        "show upcoming deadlines",
        "anything due this week",
        "what deadlines are coming up",
        "remind me what's due",
        "show deadlines in the next few days",
    ],
    "update_status": [
        "mark this as applied",
        "update the status",
        "change status to interview",
        "mark as rejected",
        "set status to accepted",
    ],
    "delete": [
        "delete an application",
        "remove this entry",
        "delete this one",
        "get rid of an application",
    ],
    "help": [
        "what can you do",
        "help",
        "how do I use this",
        "what commands are available",
        "what can this bot do",
        "hey what can this bot do",
        "how does this bot work",
    ],
}

# Flatten into two parallel lists: every example phrase, and which
# intent it belongs to. This is the format TF-IDF needs to work with.
_all_phrases = []
_phrase_intents = []
for intent, examples in INTENT_EXAMPLES.items():
    for phrase in examples:
        _all_phrases.append(phrase)
        _phrase_intents.append(intent)

# Fit the vectorizer once on all example phrases when this file loads,
# so we don't redo this expensive step on every single user message.
_vectorizer = TfidfVectorizer(stop_words="english")
_phrase_vectors = _vectorizer.fit_transform(_all_phrases)


def detect_intent(user_text, confidence_threshold=0.35):
    """
    Compare user_text against all example phrases.
    Returns (intent_name, confidence_score).
    If nothing matches well enough, returns ("unknown", score).
    """
    user_vector = _vectorizer.transform([user_text])

    similarities = cosine_similarity(user_vector, _phrase_vectors)[0]

    best_index = similarities.argmax()
    best_score = similarities[best_index]
    best_intent = _phrase_intents[best_index]

    if best_score < confidence_threshold:
        return "unknown", best_score

    return best_intent, best_score


if __name__ == "__main__":
    # Quick manual check: try phrasings NOT in the example list above,
    # to prove it generalizes instead of just matching exact strings.
    test_inputs = [
        "can you show me what's pending",
        "I just applied to a new company, please add it",
        "anything I need to worry about this week?",
        "please remove that entry",
        "what is the weather today",  # should come back "unknown"
    ]

    for text in test_inputs:
        intent, score = detect_intent(text)
        print(f"'{text}' -> {intent} (confidence: {score:.2f})")
