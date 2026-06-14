import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class DecisionEngineRuntimeDefinitionTests(unittest.TestCase):
    def test_compile_product_runtime_builds_variable_catalog_and_rules(self):
        from backend.app.domain.decision_engine import (
            AppliedVersions,
            DecisionNode,
            PipelineNodeDefinition,
            PipelineStrategy,
            ProductDefinition,
            RuleDefinition,
            VariableDefinition,
            WorkflowDefinition,
            compile_product_runtime,
        )

        class StartNode(DecisionNode):
            node_key = "start"
            node_type = "shared"

            async def run(self, context):
                raise AssertionError("runtime compilation test should not execute nodes")

        product = ProductDefinition(
            product_code="AUTO",
            name="Auto Loan",
            workflows=[
                WorkflowDefinition(
                    workflow_code="standard",
                    product_code="AUTO",
                    name="Workflow estándar",
                    pipeline_version="pipe-v1",
                    rule_pack_version="rules-v1",
                    variables=[
                        VariableDefinition(
                            variable_key="campaign_code",
                            variable_kind="input",
                            data_type="string",
                            required=True,
                        ),
                        VariableDefinition(
                            variable_key="segment_code",
                            variable_kind="derived",
                            data_type="string",
                        ),
                    ],
                    rules=[
                        RuleDefinition(
                            rule_code="derive-segment",
                            rule_type="derivation",
                            product_code="AUTO",
                            workflow_code="standard",
                            consumes_variables=["campaign_code"],
                            produces_variable="segment_code",
                            version="1",
                        )
                    ],
                )
            ],
        )
        strategy = PipelineStrategy(
            strategy_key="standard",
            product_code="AUTO",
            start_node_key="start",
            applied_versions=AppliedVersions(pipeline_version="pipe-v1"),
            nodes=[PipelineNodeDefinition(node_key="start", node_type="shared", next_node_map={})],
        )

        runtime = compile_product_runtime(
            product_definition=product,
            workflow_code="standard",
            strategy=strategy,
            normalizer=lambda request: request,
            nodes=[StartNode()],
        )

        self.assertEqual(runtime.product_code, "AUTO")
        self.assertEqual(runtime.workflow_code, "standard")
        self.assertEqual(runtime.workflow.name, "Workflow estándar")
        self.assertEqual(runtime.variable_catalog["campaign_code"].variable_kind, "input")
        self.assertEqual(runtime.rules[0].rule_code, "derive-segment")

    def test_compile_product_runtime_rejects_rule_consuming_unknown_variable(self):
        from backend.app.domain.decision_engine import (
            AppliedVersions,
            DecisionEngineError,
            DecisionNode,
            PipelineNodeDefinition,
            PipelineStrategy,
            ProductDefinition,
            RuleDefinition,
            VariableDefinition,
            WorkflowDefinition,
            compile_product_runtime,
        )

        class StartNode(DecisionNode):
            node_key = "start"
            node_type = "shared"

            async def run(self, context):
                raise AssertionError("runtime compilation test should not execute nodes")

        product = ProductDefinition(
            product_code="AUTO",
            name="Auto Loan",
            workflows=[
                WorkflowDefinition(
                    workflow_code="standard",
                    product_code="AUTO",
                    name="Workflow estándar",
                    pipeline_version="pipe-v1",
                    rule_pack_version="rules-v1",
                    variables=[
                        VariableDefinition(
                            variable_key="campaign_code",
                            variable_kind="input",
                            data_type="string",
                        )
                    ],
                    rules=[
                        RuleDefinition(
                            rule_code="bad-rule",
                            rule_type="eligibility",
                            product_code="AUTO",
                            workflow_code="standard",
                            consumes_variables=["missing_variable"],
                            produces_effect="block",
                            version="1",
                        )
                    ],
                )
            ],
        )
        strategy = PipelineStrategy(
            strategy_key="standard",
            product_code="AUTO",
            start_node_key="start",
            applied_versions=AppliedVersions(pipeline_version="pipe-v1"),
            nodes=[PipelineNodeDefinition(node_key="start", node_type="shared", next_node_map={})],
        )

        with self.assertRaises(DecisionEngineError):
            compile_product_runtime(
                product_definition=product,
                workflow_code="standard",
                strategy=strategy,
                normalizer=lambda request: request,
                nodes=[StartNode()],
            )

    def test_compile_product_runtime_rejects_rule_producing_unknown_variable(self):
        from backend.app.domain.decision_engine import (
            AppliedVersions,
            DecisionEngineError,
            DecisionNode,
            PipelineNodeDefinition,
            PipelineStrategy,
            ProductDefinition,
            RuleDefinition,
            VariableDefinition,
            WorkflowDefinition,
            compile_product_runtime,
        )

        class StartNode(DecisionNode):
            node_key = "start"
            node_type = "shared"

            async def run(self, context):
                raise AssertionError("runtime compilation test should not execute nodes")

        product = ProductDefinition(
            product_code="AUTO",
            name="Auto Loan",
            workflows=[
                WorkflowDefinition(
                    workflow_code="standard",
                    product_code="AUTO",
                    name="Workflow estándar",
                    pipeline_version="pipe-v1",
                    rule_pack_version="rules-v1",
                    variables=[
                        VariableDefinition(
                            variable_key="campaign_code",
                            variable_kind="input",
                            data_type="string",
                        )
                    ],
                    rules=[
                        RuleDefinition(
                            rule_code="bad-rule",
                            rule_type="derivation",
                            product_code="AUTO",
                            workflow_code="standard",
                            consumes_variables=["campaign_code"],
                            produces_variable="missing_output",
                            version="1",
                        )
                    ],
                )
            ],
        )
        strategy = PipelineStrategy(
            strategy_key="standard",
            product_code="AUTO",
            start_node_key="start",
            applied_versions=AppliedVersions(pipeline_version="pipe-v1"),
            nodes=[PipelineNodeDefinition(node_key="start", node_type="shared", next_node_map={})],
        )

        with self.assertRaises(DecisionEngineError):
            compile_product_runtime(
                product_definition=product,
                workflow_code="standard",
                strategy=strategy,
                normalizer=lambda request: request,
                nodes=[StartNode()],
            )
