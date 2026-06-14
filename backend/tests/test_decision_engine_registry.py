import asyncio
import os
import sys
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class DecisionEngineRegistryTests(unittest.TestCase):
    def test_registry_resolves_multiple_products_and_workflows_without_pld_specific_core(self):
        from backend.app.domain.decision_engine import (
            AppliedVersions,
            DecisionEngineOrchestrator,
            DecisionEngineRegistry,
            DecisionNode,
            EngineEvaluationRequest,
            NodeExecutionResult,
            PipelineNodeDefinition,
            PipelineStrategy,
        )

        class SharedNode(DecisionNode):
            node_key = "start"
            node_type = "shared"

            async def run(self, context):
                context.product_result["product"] = context.request.product_code
                return NodeExecutionResult(outcome="done", eligible=True)

        registry = DecisionEngineRegistry()
        strategy_a = PipelineStrategy(
            strategy_key="strategy-a",
            product_code="ALPHA",
            start_node_key="start",
            applied_versions=AppliedVersions(pipeline_version="alpha-v1"),
            nodes=[PipelineNodeDefinition(node_key="start", node_type="shared", next_node_map={})],
        )
        strategy_a_special = PipelineStrategy(
            strategy_key="strategy-a-special",
            product_code="ALPHA",
            start_node_key="start",
            applied_versions=AppliedVersions(pipeline_version="alpha-v2"),
            nodes=[PipelineNodeDefinition(node_key="start", node_type="shared", next_node_map={})],
        )
        strategy_b = PipelineStrategy(
            strategy_key="strategy-b",
            product_code="BETA",
            start_node_key="start",
            applied_versions=AppliedVersions(pipeline_version="beta-v1"),
            nodes=[PipelineNodeDefinition(node_key="start", node_type="shared", next_node_map={})],
        )

        registry.register_product(
            product_code="ALPHA",
            workflow_code="standard",
            strategy=strategy_a,
            normalizer=lambda request: request,
            nodes=[SharedNode()],
        )
        registry.register_product(
            product_code="ALPHA",
            workflow_code="special",
            strategy=strategy_a_special,
            normalizer=lambda request: request,
            nodes=[SharedNode()],
        )
        registry.register_product(
            product_code="BETA",
            workflow_code="standard",
            strategy=strategy_b,
            normalizer=lambda request: request,
            nodes=[SharedNode()],
        )

        alpha_runtime = registry.resolve("ALPHA", "standard")
        alpha_special_runtime = registry.resolve("ALPHA", "special")
        beta_runtime = registry.resolve("BETA", "standard")
        alpha_result = asyncio.run(
            DecisionEngineOrchestrator(nodes=alpha_runtime.nodes).evaluate(
                EngineEvaluationRequest(
                    product_code="ALPHA",
                    workflow_code="standard",
                    document={"document_type": "DNI", "document_number": "12345678"},
                    requested_by={"username": "analista"},
                    product_context={},
                ),
                alpha_runtime.strategy,
            )
        )
        alpha_special_result = asyncio.run(
            DecisionEngineOrchestrator(nodes=alpha_special_runtime.nodes).evaluate(
                EngineEvaluationRequest(
                    product_code="ALPHA",
                    workflow_code="special",
                    document={"document_type": "DNI", "document_number": "12345678"},
                    requested_by={"username": "analista"},
                    product_context={},
                ),
                alpha_special_runtime.strategy,
            )
        )
        beta_result = asyncio.run(
            DecisionEngineOrchestrator(nodes=beta_runtime.nodes).evaluate(
                EngineEvaluationRequest(
                    product_code="BETA",
                    workflow_code="standard",
                    document={"document_type": "DNI", "document_number": "12345678"},
                    requested_by={"username": "analista"},
                    product_context={},
                ),
                beta_runtime.strategy,
            )
        )

        self.assertEqual(alpha_runtime.strategy.applied_versions.pipeline_version, "alpha-v1")
        self.assertEqual(alpha_special_runtime.strategy.applied_versions.pipeline_version, "alpha-v2")
        self.assertEqual(beta_runtime.strategy.applied_versions.pipeline_version, "beta-v1")
        self.assertEqual(alpha_result.product_result["product"], "ALPHA")
        self.assertEqual(alpha_special_result.decision_trace.workflow_code, "special")
        self.assertEqual(beta_result.product_result["product"], "BETA")

    def test_registry_rejects_unknown_product(self):
        from backend.app.domain.decision_engine import (
            DecisionEngineRegistry,
            EngineRegistryError,
        )

        registry = DecisionEngineRegistry()

        with self.assertRaises(EngineRegistryError):
            registry.resolve("UNKNOWN", "standard")

    def test_registry_rejects_unknown_workflow_for_known_product(self):
        from backend.app.domain.decision_engine import (
            AppliedVersions,
            DecisionEngineRegistry,
            DecisionNode,
            EngineRegistryError,
            NodeExecutionResult,
            PipelineNodeDefinition,
            PipelineStrategy,
        )

        class SharedNode(DecisionNode):
            node_key = "start"
            node_type = "shared"

            async def run(self, context):
                return NodeExecutionResult(outcome="done", eligible=True)

        registry = DecisionEngineRegistry()
        strategy = PipelineStrategy(
            strategy_key="strategy-a",
            product_code="ALPHA",
            start_node_key="start",
            applied_versions=AppliedVersions(pipeline_version="alpha-v1"),
            nodes=[PipelineNodeDefinition(node_key="start", node_type="shared", next_node_map={})],
        )

        registry.register_product(
            product_code="ALPHA",
            workflow_code="standard",
            strategy=strategy,
            normalizer=lambda request: request,
            nodes=[SharedNode()],
        )

        with self.assertRaises(EngineRegistryError):
            registry.resolve("ALPHA", "missing")

    def test_persistence_backed_registry_loads_active_runtime(self):
        temp_dir = tempfile.TemporaryDirectory()
        try:
            db_path = Path(temp_dir.name) / "registry_runtime.db"
            os.environ["APP_ENV"] = "test"
            os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{db_path.as_posix()}"

            from backend.app.config.settings import clear_settings_cache
            from backend.app.infrastructure.db.session import clear_database_caches, get_session_factory

            clear_settings_cache()
            clear_database_caches()

            from backend.app.infrastructure.db.base import Base
            from backend.app.infrastructure.db.models import (
                LoanProduct,
                ParameterSet,
                PipelineNode,
                PipelineStrategy,
                ProductVariable,
                ProductWorkflow,
                RuleSet,
                RuleVersion,
                User,
                VariableCatalogItem,
                VariableCatalogVersion,
                WorkflowRuleAssignment,
                WorkflowVersion,
            )

            session_factory = get_session_factory()
            Base.metadata.create_all(bind=session_factory.kw["bind"])

            with session_factory() as session:
                user = User(
                    id=str(uuid4()),
                    username="system",
                    display_name="System",
                    password_hash="hash",
                    is_active=True,
                    created_at=datetime.now(UTC),
                )
                product = LoanProduct(
                    code="PLD",
                    name="Prestamo Libre Disponibilidad",
                    description="Producto base",
                    status="active",
                    created_by=user.id,
                    activated_by=user.id,
                    activated_at=datetime.now(UTC),
                    created_at=datetime.now(UTC),
                )
                workflow = ProductWorkflow(
                    id=str(uuid4()),
                    product_code="PLD",
                    workflow_code="standard",
                    name="Standard",
                    description="Workflow principal",
                    status="active",
                    created_by=user.id,
                    activated_by=user.id,
                    activated_at=datetime.now(UTC),
                    created_at=datetime.now(UTC),
                )
                variable = ProductVariable(
                    id=str(uuid4()),
                    product_code="PLD",
                    variable_key="validated_income",
                    name="Ingreso validado",
                    business_meaning="Ingreso usado por el motor",
                    data_type="number",
                    is_required=True,
                    allowed_sources="both",
                    status="active",
                    created_by=user.id,
                    created_at=datetime.now(UTC),
                )
                catalog = VariableCatalogVersion(
                    id=str(uuid4()),
                    product_code="PLD",
                    version_number=1,
                    status="active",
                    created_by=user.id,
                    activated_by=user.id,
                    activated_at=datetime.now(UTC),
                    created_at=datetime.now(UTC),
                )
                parameter_set = ParameterSet(
                    id=str(uuid4()),
                    product_code="PLD",
                    workflow_code="standard",
                    version_number=1,
                    status="active",
                    payload='{"max_rci": 0.5}',
                    created_by=user.id,
                    activated_by=user.id,
                    activated_at=datetime.now(UTC),
                    created_at=datetime.now(UTC),
                )
                strategy = PipelineStrategy(
                    id=str(uuid4()),
                    loan_product_code="PLD",
                    version_number=1,
                    graph_definition='{"start_node_key": "start"}',
                    status="active",
                    approved_by=user.id,
                    created_by=user.id,
                    created_at=datetime.now(UTC),
                )
                rule_set = RuleSet(
                    id=str(uuid4()),
                    loan_product_code="PLD",
                    name="Core rules",
                    description="Reglas base",
                    effective_from=datetime.now(UTC),
                    status="active",
                    created_by=user.id,
                    activated_by=user.id,
                    activated_at=datetime.now(UTC),
                    created_at=datetime.now(UTC),
                )
                rule_version = RuleVersion(
                    id=str(uuid4()),
                    rule_set_id=rule_set.id,
                    version_number=1,
                    rule_key="income-check",
                    rule_name="Income check",
                    rule_type="validation",
                    condition_expression="validated_income > 0",
                    action_expression="allow",
                    parameters=None,
                    status="active",
                    change_notes=None,
                    approved_by=user.id,
                    created_by=user.id,
                    created_at=datetime.now(UTC),
                )
                workflow_version = WorkflowVersion(
                    id=str(uuid4()),
                    workflow_id=workflow.id,
                    version_number=1,
                    status="active",
                    variable_catalog_version_id=catalog.id,
                    parameter_set_id=parameter_set.id,
                    pipeline_strategy_id=strategy.id,
                    change_notes=None,
                    created_by=user.id,
                    activated_by=user.id,
                    activated_at=datetime.now(UTC),
                    created_at=datetime.now(UTC),
                )
                session.add_all([user, product, workflow, variable, catalog, parameter_set, strategy, rule_set, rule_version, workflow_version])
                session.flush()
                session.add_all([
                    VariableCatalogItem(
                        id=str(uuid4()),
                        catalog_version_id=catalog.id,
                        product_variable_id=variable.id,
                        is_required_in_runtime=True,
                        default_value=None,
                        source_policy_payload='{"allowed_sources": "both"}',
                    ),
                    PipelineNode(
                        id=str(uuid4()),
                        pipeline_strategy_id=strategy.id,
                        node_key="start",
                        node_type="shared",
                        position_x=0,
                        position_y=0,
                        config_payload="{}",
                        created_at=datetime.now(UTC),
                    ),
                    WorkflowRuleAssignment(
                        id=str(uuid4()),
                        workflow_version_id=workflow_version.id,
                        rule_version_id=rule_version.id,
                        execution_order=1,
                        is_active=True,
                    ),
                ])
                session.commit()

            from backend.app.application.engine_admin.runtime_loader import RuntimeLoader

            runtime = RuntimeLoader(session_factory).load_runtime("PLD", "standard")

            self.assertEqual(runtime.product_code, "PLD")
            self.assertEqual(runtime.workflow_code, "standard")
            self.assertEqual(runtime.strategy.product_code, "PLD")
        finally:
            from backend.app.config.settings import clear_settings_cache
            from backend.app.infrastructure.db.session import clear_database_caches

            clear_settings_cache()
            clear_database_caches()
            temp_dir.cleanup()

    def test_runtime_loader_lists_multiple_active_workflows_for_one_product(self):
        temp_dir = tempfile.TemporaryDirectory()
        try:
            db_path = Path(temp_dir.name) / "registry_workflows.db"
            os.environ["APP_ENV"] = "test"
            os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{db_path.as_posix()}"

            from backend.app.config.settings import clear_settings_cache
            from backend.app.infrastructure.db.session import clear_database_caches, get_session_factory

            clear_settings_cache()
            clear_database_caches()

            from backend.app.application.engine_admin.runtime_loader import RuntimeLoader
            from backend.app.infrastructure.db.base import Base
            from backend.app.infrastructure.db.models import LoanProduct, ProductWorkflow, User

            session_factory = get_session_factory()
            Base.metadata.create_all(bind=session_factory.kw["bind"])

            with session_factory() as session:
                user = User(
                    id=str(uuid4()),
                    username="system",
                    display_name="System",
                    password_hash="hash",
                    is_active=True,
                    created_at=datetime.now(UTC),
                )
                session.add(user)
                session.flush()
                session.add(
                    LoanProduct(
                        code="PLD",
                        name="Prestamo Libre Disponibilidad",
                        status="active",
                        is_active=True,
                        created_by=user.id,
                        activated_by=user.id,
                        activated_at=datetime.now(UTC),
                        created_at=datetime.now(UTC),
                    )
                )
                session.add_all(
                    [
                        ProductWorkflow(
                            id=str(uuid4()),
                            product_code="PLD",
                            workflow_code="standard",
                            name="Standard",
                            status="active",
                            created_by=user.id,
                            activated_by=user.id,
                            activated_at=datetime.now(UTC),
                            created_at=datetime.now(UTC),
                        ),
                        ProductWorkflow(
                            id=str(uuid4()),
                            product_code="PLD",
                            workflow_code="special",
                            name="Special",
                            status="active",
                            created_by=user.id,
                            activated_by=user.id,
                            activated_at=datetime.now(UTC),
                            created_at=datetime.now(UTC),
                        ),
                    ]
                )
                session.commit()

            workflows = RuntimeLoader(session_factory).list_active_workflows()

            self.assertEqual(workflows, [("PLD", "special"), ("PLD", "standard")])
        finally:
            from backend.app.config.settings import clear_settings_cache
            from backend.app.infrastructure.db.session import clear_database_caches

            clear_settings_cache()
            clear_database_caches()
            temp_dir.cleanup()

    def test_runtime_loader_allows_active_product_without_active_workflows(self):
        temp_dir = tempfile.TemporaryDirectory()
        try:
            db_path = Path(temp_dir.name) / "registry_empty_product.db"
            os.environ["APP_ENV"] = "test"
            os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{db_path.as_posix()}"

            from backend.app.config.settings import clear_settings_cache
            from backend.app.infrastructure.db.session import clear_database_caches, get_session_factory

            clear_settings_cache()
            clear_database_caches()

            from backend.app.application.engine_admin.runtime_loader import RuntimeLoader
            from backend.app.infrastructure.db.base import Base
            from backend.app.infrastructure.db.models import LoanProduct, User

            session_factory = get_session_factory()
            Base.metadata.create_all(bind=session_factory.kw["bind"])

            with session_factory() as session:
                user = User(
                    id=str(uuid4()),
                    username="system",
                    display_name="System",
                    password_hash="hash",
                    is_active=True,
                    created_at=datetime.now(UTC),
                )
                session.add(user)
                session.flush()
                session.add(
                    LoanProduct(
                        code="PLD",
                        name="Prestamo Libre Disponibilidad",
                        status="active",
                        is_active=True,
                        created_by=user.id,
                        activated_by=user.id,
                        activated_at=datetime.now(UTC),
                        created_at=datetime.now(UTC),
                    )
                )
                session.commit()

            self.assertEqual(RuntimeLoader(session_factory).list_active_workflows(), [])
        finally:
            from backend.app.config.settings import clear_settings_cache
            from backend.app.infrastructure.db.session import clear_database_caches

            clear_settings_cache()
            clear_database_caches()
            temp_dir.cleanup()
