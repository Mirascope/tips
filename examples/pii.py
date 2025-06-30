from presidio_analyzer import AnalyzerEngine

def mask_pii(text: str) -> tuple[str, dict[str, str]]:
    """Detect and mask PII using Presidio"""
    analyzer = AnalyzerEngine()
    
    # Analyze text for PII
    results = analyzer.analyze(text=text, language='en')
    mapping = {f"<{result.entity_type}>": text[result.start:result.end] for result in results}
    inverse_mapping = {v: k for k, v in mapping.items()}
    return unmask_pii(text, inverse_mapping), mapping

def unmask_pii(text: str, mapping: dict[str, str]) -> str:
    for k, v in mapping.items():
        text = text.replace(k, v)
    return text

if __name__ == "__main__":
    text = "My name is John Doe and my email is john.doe@example.com. My phone number is 123-456-7890."
    print("ORIGINAL:\n", text)
    anonymized_text, mapping = mask_pii(text)
    print("ANONYMIZED:\n", anonymized_text)
    print("UNANONYMIZED:\n", unmask_pii(anonymized_text, mapping))