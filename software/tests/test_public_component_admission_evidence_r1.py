"""Focused regression checks for the V1.0 public evidence repair."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import pytest

from services.component_library_v2_adoption import (
    build_v2_canonical_inventory,
    V2AdoptionError,
    load_v2_package,
    v2_component_admission_decision,
)
from services.plant_component_workflow_registry import (
    host_applicability_gate,
    registry_record,
    registry_record_is_admissible,
    workflow_component_options,
)


ROOT = Path(__file__).resolve().parents[1]


def test_allowlisted_evidence_files_and_sealed_governance() -> None:
    registry = ROOT / "services" / "plant_component_workflow_registry.py"
    text = registry.read_text(encoding="utf-8")
    for relative in (
        "docs/qa/component_library_v1_full_evidence_completion/phase_b2b/COMPONENT_LIBRARY_V1_B2B_RIGHTS_GOVERNANCE.json",
        "docs/qa/component_library_v1_full_evidence_completion/phase_b2b/COMPONENT_LIBRARY_V1_B2B_ATTRIBUTION_CONTRACT.md",
        "docs/qa/component_library_v1_full_evidence_completion/phase_b2c/COMPONENT_LIBRARY_V1_B2C_PRODUCT_ADMISSION.json",
        "docs/qa/public_component_admission_evidence_r1/HSP18_2_HOST_SCOPE_PUBLIC_SUMMARY_R1.json",
    ):
        assert (ROOT / relative).is_file(), relative
        assert relative in text
    hsp = ROOT / "docs/qa/public_component_admission_evidence_r1/HSP18_2_HOST_SCOPE_PUBLIC_SUMMARY_R1.json"
    assert hashlib.sha256(hsp.read_bytes()).hexdigest() in text
    assert "p1660_full_sequence" not in hsp.read_text(encoding="utf-8")
    assert "p1661_full_sequence" not in hsp.read_text(encoding="utf-8")


def test_formal_admission_scope_and_host_gate_are_unchanged() -> None:
    assert registry_record_is_admissible(registry_record("PCLV1-PRO-E8-2164"))
    assert registry_record_is_admissible(registry_record("PCLV1-TER-HSP18-2-250"))
    assert host_applicability_gate(registry_record("PCLV1-PRO-E8-2164"), "Solanum lycopersicum") == "ADMITTED"
    assert host_applicability_gate(registry_record("PCLV1-PRO-E8-2164"), "Arabidopsis thaliana") == "HOST_APPLICABILITY_WRONG_HOST"
    assert host_applicability_gate(registry_record("PCLV1-TER-HSP18-2-250"), "Solanum lycopersicum") == "ADMITTED"
    rows = build_v2_canonical_inventory()
    assert len(rows) == 171
    assert sum(bool(row.get("formal_selectable")) for row in rows) == 2
    assert {row["canonical_v2_component_id"] for row in rows if row.get("formal_selectable")} == {"V2-CMP-138", "V2-CMP-144"}
    for row in rows:
        if row["canonical_v2_component_id"] not in {"V2-CMP-138", "V2-CMP-144"}:
            if row["admission_mode"] in {"DIRECT_USE", "USER_SEQUENCE_ASSISTED"}:
                assert v2_component_admission_decision(row["canonical_v2_component_id"])["current_formal_selectable"] is False
            else:
                with pytest.raises(V2AdoptionError):
                    v2_component_admission_decision(row["canonical_v2_component_id"])
    assert [row["registry_component_id"] for row in workflow_component_options(role="promoter", target_host_species="Solanum lycopersicum")] == ["PCLV1-PRO-E8-2164"]
    assert workflow_component_options(role="promoter", target_host_species="Arabidopsis thaliana") == []
    assert workflow_component_options(role="promoter", target_host_species="Oryza sativa") == []


def test_v2_package_cardinality_and_identity_hashes() -> None:
    package = load_v2_package()
    assert len(package["direct"]) == 17
    for row in package["direct"]:
        assert len(row["sequence"]) == row["length"]
        assert hashlib.sha256(row["sequence"].encode()).hexdigest() == row["sequence_sha256"]
    summary = json.loads((ROOT / "docs/qa/public_component_admission_evidence_r1/V2_DIRECT_USE_PUBLIC_EVIDENCE_SUMMARY_R1.json").read_text(encoding="utf-8"))
    assert summary["record_count"] == 15
    assert summary["sequence_payloads_included"] is False
    by_id = {row["canonical_v2_component_id"]: row for row in summary["records"]}
    for row in package["direct"]:
        assert (ROOT / row["evidence_path"]).is_file()
        if row["canonical_v2_component_id"] in by_id:
            public = by_id[row["canonical_v2_component_id"]]
            for field in ("length", "sequence_sha256", "source_artifact_sha256", "exact_boundary", "orientation"):
                assert public[field] == row[field]
            assert public["formal_product_admission"] == "NOT_PROVEN"
