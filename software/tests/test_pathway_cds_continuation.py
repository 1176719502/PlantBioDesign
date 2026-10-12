"""Regression coverage for real CDS handoff, navigation, and invalid input retention."""
from __future__ import annotations

import ast
import copy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Mapping
import unittest

from Bio import SeqIO
from services.gate3_pathway_mapping import (
    CDS_SOURCE_TYPES, analyze_pathway_cds, apply_step_cds_to_unit,
    new_pathway_step, normalize_pathway_steps, update_pathway_step,
    validate_pathway_mapping,
)

ROOT = Path(__file__).resolve().parents[1]


def app_functions(state: dict[str, Any], units: list[dict[str, Any]]) -> dict[str, Any]:
    """Execute production UI predicates without launching the Streamlit app."""
    names = {
        '_multi_tu_component_uses_user_input', '_is_explicit_five_prime_absence',
        '_multi_tu_editor_widget_state_is_present', '_prepare_multi_tu_editor_widget_state',
        '_formal_ui_signature', '_formal_step_statuses', '_normalize_formal_current_step',
        '_formal_step_contract', '_set_formal_step',
    }
    tree = ast.parse((ROOT / 'app.py').read_text('utf-8'))
    module = ast.Module(body=[node for node in tree.body if isinstance(node, ast.FunctionDef)
                             and node.name in names], type_ignores=[])
    namespace = dict(
        Any=Any, Mapping=Mapping, hashlib=hashlib, json=json,
        st=SimpleNamespace(session_state=state), _transcription_units=lambda: units,
        _MULTI_TU_EDITOR_REQUIRED_ROLES=('promoter', 'five_prime_region', 'cds', '3_prime_regulatory_region'),
        _MULTI_TU_EDITOR_OPTIONAL_ROLES=('targeting_sequence', 'linker', 'fusion_tag'),
        _is_pathway_multi_tu_project=lambda: True,
        _is_generic_multi_tu_workflow=lambda: False,
        _formal_project_type=lambda: 'dual_tu', PROJECT_TYPE_DUAL_TU='dual_tu',
        PROJECT_TYPE_SINGLE_GENE='single_gene', _host_supports_project_type=lambda *args: True,
        _multi_tu_overall_ready=lambda value: False,
        _is_multi_tu_expression_assembly=lambda value: False,
    )
    namespace['_refresh_pathway_mapping_status'] = lambda: validate_pathway_mapping(
        state['formal_pathway_steps'], units)
    exec(compile(module, str(ROOT / 'app.py'), 'exec'), namespace)
    return namespace


class PathwayContinuationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.units = [dict(unit_id='tu-cyp', display_name='CYP TU', order=1),
                      dict(unit_id='tu-doda', display_name='DODA TU', order=2)]
        self.steps = []
        for index, (accession, gene) in enumerate((('HQ656023.1', 'CYP76AD1'), ('HQ656027.1', 'DODA1'))):
            record = SeqIO.read(ROOT / 'data/real_cases/betalain_three_enzyme/source_records' / f'{accession}.gb', 'genbank')
            feature = next(f for f in record.features if f.type == 'CDS')
            sequence = str(feature.extract(record.seq))
            step = new_pathway_step(step_id=f'step-{gene}')
            step.update(step_name=gene, enzyme_name=gene, enzyme_gene_name=gene,
                        mapped_unit_id=self.units[index]['unit_id'])
            step.update(analyze_pathway_cds(sequence, source_reference=f'{accession} CDS {feature.location}'))
            self.steps.append(step)
        self.state = dict(mvp_project_id='project-a', formal_project_name='Pathway test',
                          formal_project_definition={'project_name': 'Pathway test', 'plant_host': 'Tobacco'},
                          formal_pathway_steps=self.steps, formal_transcription_units=self.units)

    def apply_all(self) -> None:
        for step in self.steps:
            self.steps, self.units = apply_step_cds_to_unit(self.steps, self.units, step['step_id'])
        self.state.update(formal_pathway_steps=self.steps, formal_transcription_units=self.units)

    def test_pending_and_applied_navigation_share_completion(self) -> None:
        ui = app_functions(self.state, self.units)
        self.assertFalse(validate_pathway_mapping(self.steps, self.units)['mapping_complete'])
        self.assertFalse(ui['_formal_step_statuses']()[1]['done'])
        self.assertEqual(ui['_normalize_formal_current_step'](3), 2)
        self.apply_all()
        ui = app_functions(self.state, self.units)
        self.assertTrue(validate_pathway_mapping(self.steps, self.units)['mapping_complete'])
        self.assertTrue(ui['_formal_step_statuses']()[1]['done'])
        self.assertEqual(ui['_normalize_formal_current_step'](3), 3)
        self.state['formal_step2_design_dirty'] = True
        self.assertEqual(ui['_normalize_formal_current_step'](3), 2)

    def test_real_cds_written_only_to_selected_stable_tu(self) -> None:
        before = copy.deepcopy(self.units)
        steps, units = apply_step_cds_to_unit(self.steps, self.units, self.steps[0]['step_id'])
        self.assertEqual(units[1], before[1])
        self.assertEqual(self.units, before)
        self.assertEqual(units[0]['cds']['raw_text'], self.steps[0]['cds_sequence'])
        self.assertEqual(units[0]['cds']['source_name'], self.steps[0]['cds_source_reference'])
        self.assertFalse(validate_pathway_mapping(steps, units)['mapping_complete'])

    def test_every_manual_source_hydrates_and_recovers_lost_widgets(self) -> None:
        self.apply_all()
        for source_type in CDS_SOURCE_TYPES:
            with self.subTest(source_type=source_type):
                for unit in self.units:
                    unit['cds']['source_type'] = source_type
                ui = app_functions(self.state, self.units)
                ui['_prepare_multi_tu_editor_widget_state']()
                for unit in self.units:
                    prefix = f"formal_{unit['unit_id']}_cds"
                    self.assertEqual(self.state[prefix + '_mode'], '用户序列')
                    self.assertEqual(self.state[prefix + '_text'], unit['cds']['raw_text'])
                    self.assertEqual(self.state[prefix + '_name'], unit['cds']['display_name'])
                self.state.pop('formal_tu-doda_cds_text')
                ui['_prepare_multi_tu_editor_widget_state']()
                self.assertEqual(self.state['formal_tu-doda_cds_text'], self.steps[1]['cds_sequence'])
        self.state['mvp_project_id'] = 'project-b'
        self.units[0]['cds']['display_name'] = 'Different project CDS'
        ui['_prepare_multi_tu_editor_widget_state']()
        self.assertEqual(self.state['formal_tu-cyp_cds_name'], 'Different project CDS')

    def test_invalid_original_input_cannot_be_sanitized_into_valid_application(self) -> None:
        original = self.steps[0]['cds_sequence']
        for raw in ('', original[:3] + 'N' + original[3:], 'ATGA', '>one\nATGTAA\n>two\nATGTAA'):
            with self.subTest(raw=raw[:25]):
                steps = update_pathway_step(self.steps, self.steps[0]['step_id'], cds_sequence=raw)
                for _ in range(3):
                    steps = normalize_pathway_steps(steps)
                validation = validate_pathway_mapping(steps, self.units)
                self.assertTrue(validation['blocking_items'])
                self.assertFalse(validation['mapping_complete'])
                self.assertEqual(steps[0]['cds_analysis']['original_text'], raw)
                with self.assertRaises(ValueError):
                    apply_step_cds_to_unit(steps, self.units, steps[0]['step_id'])

    def test_mapping_errors_and_unused_empty_tu_block_navigation(self) -> None:
        self.apply_all()
        for kind in ('shared', 'dangling', 'mismatch', 'missing_cds', 'unapplied'):
            steps, units = copy.deepcopy(self.steps), copy.deepcopy(self.units)
            if kind == 'shared': steps[1]['mapped_unit_id'] = steps[0]['mapped_unit_id']
            elif kind == 'dangling': steps[0]['mapped_unit_id'] = 'deleted-tu'
            elif kind == 'mismatch': units[0]['cds']['cds_analysis']['normalized_cds'] = steps[1]['cds_sequence']
            elif kind == 'missing_cds': steps[0] = update_pathway_step(steps, steps[0]['step_id'], cds_sequence='')[0]
            else: steps[0]['applied_to_unit'] = False
            state = {**self.state, 'formal_pathway_steps': steps, 'formal_transcription_units': units}
            ui = app_functions(state, units)
            with self.subTest(kind=kind):
                self.assertFalse(ui['_formal_step_statuses']()[1]['done'])
                self.assertEqual(ui['_normalize_formal_current_step'](3), 2)
        self.units.append(dict(unit_id='unused-empty', display_name='Unconfigured TU', order=3))
        ui = app_functions(self.state, self.units)
        self.assertFalse(ui['_formal_step_statuses']()[1]['done'])


if __name__ == '__main__':
    unittest.main()
