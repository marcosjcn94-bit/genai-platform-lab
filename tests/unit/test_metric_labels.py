from app.telemetry import Metrics, safe_model


def test_metrics_model_allowlist_prevents_external_label_values():
    assert safe_model("primary") == "primary"
    assert safe_model("PRIVATE_CANARY") == "unknown"
    metrics = Metrics()
    metrics.tokens.labels(safe_model("PRIVATE_CANARY")).inc(12)
    values = [
        sample.labels.get("model")
        for family in metrics.registry.collect()
        for sample in family.samples
        if family.name == "platform_tokens"
    ]
    assert set(values) == {"unknown"}
