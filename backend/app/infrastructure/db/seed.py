import json
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.infrastructure.db.base import Base
from backend.app.infrastructure.db.models import (
    LoanProduct,
    ParameterSet,
    PipelineNode,
    PipelineStrategy,
    ProductVariable,
    ProductWorkflow,
    Role,
    RuleSet,
    RuleVersion,
    User,
    UserRole,
    VariableCatalogItem,
    VariableCatalogVersion,
    WorkflowRuleAssignment,
    WorkflowVersion,
)
from backend.app.infrastructure.db.session import get_engine, get_session_factory
from backend.app.security.passwords import hash_password


DEFAULT_ROLES = [
    ("admin", "Administrador"),
    ("analista", "Analista"),
    ("evaluador", "Evaluador"),
    ("auditor", "Auditor"),
    ("admin_negocio", "Administrador de negocio"),
    ("admin_riesgos", "Administrador de riesgos"),
    ("plataforma", "Administracion privilegiada de plataforma"),
]

DEFAULT_USERS = [
    ("admin", "Administrador", "admin123", "admin"),
    ("analista", "Analista", "analista123", "analista"),
    ("evaluador", "Evaluador", "evaluador123", "evaluador"),
    ("auditor", "Auditor", "auditor123", "auditor"),
    ("negocio", "Administrador Negocio", "negocio123", "admin_negocio"),
    ("riesgos", "Administrador Riesgos", "riesgos123", "admin_riesgos"),
    ("plataforma", "Administrador Plataforma", "plataforma123", "plataforma"),
]

PLD_RUNTIME_IDS = {
    "workflow": "workflow-pld-standard",
    "catalog": "catalog-pld-v1",
    "parameter_set": "parameter-pld-v1",
    "pipeline": "pipeline-pld-v1",
    "workflow_version": "workflow-version-pld-v1",
}

PLD_VARIABLE_DEFINITIONS = [
    ("campaign_code", "campaign_db", True),
    ("customer_type", "campaign_db", False),
    ("profile_code", "campaign_db", False),
    ("sunedu_flag", "campaign_db", False),
    ("employment_status", "campaign_db", False),
    ("validated_income", "campaign_db", True),
    ("reported_debt", "user_input", False),
    ("initial_offered_amount", "campaign_db", False),
    ("existing_consumption_balance", "campaign_db", False),
    ("campaign_rate", "campaign_db", False),
    ("campaign_term_months", "campaign_db", False),
]

PLD_RULE_DEFINITIONS = [
    ("pld.collect_context", "derivation"),
    ("pld.check_eligibility", "eligibility"),
    ("pld.calculate_metrics", "metric"),
    ("pld.build_decision", "decision"),
]


def seed_identity_data(session: Session) -> dict[str, int]:
    now = datetime.now(UTC)
    roles_created = 0
    users_created = 0

    existing_roles = {
        role.code: role
        for role in session.execute(select(Role)).scalars().all()
    }

    for code, name in DEFAULT_ROLES:
        if code not in existing_roles:
            role = Role(id=str(uuid4()), code=code, name=name, created_at=now)
            session.add(role)
            existing_roles[code] = role
            roles_created += 1

    session.flush()

    existing_users = {
        user.username: user
        for user in session.execute(select(User)).scalars().all()
    }
    existing_user_roles = {
        (user_role.user_id, user_role.role_id)
        for user_role in session.execute(select(UserRole)).scalars().all()
    }

    for username, display_name, password, role_code in DEFAULT_USERS:
        user = existing_users.get(username)
        if user is None:
            user = User(
                id=str(uuid4()),
                username=username,
                display_name=display_name,
                password_hash=hash_password(password),
                is_active=True,
                created_at=now,
            )
            session.add(user)
            session.flush()
            existing_users[username] = user
            users_created += 1

        role = existing_roles[role_code]
        relation_key = (user.id, role.id)
        if relation_key not in existing_user_roles:
            session.add(
                UserRole(
                    id=str(uuid4()),
                    user_id=user.id,
                    role_id=role.id,
                    created_at=now,
                )
            )
            existing_user_roles.add(relation_key)

    session.commit()
    return {"roles_created": roles_created, "users_created": users_created}


def seed_pld_runtime_bundle(session: Session) -> dict[str, bool | str]:
    now = datetime.now(UTC)

    existing_active_workflow = session.execute(
        select(ProductWorkflow).where(
            ProductWorkflow.product_code == "PLD",
            ProductWorkflow.workflow_code == "standard",
            ProductWorkflow.status == "active",
        )
    ).scalar_one_or_none()
    existing_active_version = None
    if existing_active_workflow is not None:
        existing_active_version = session.execute(
            select(WorkflowVersion).where(
                WorkflowVersion.workflow_id == existing_active_workflow.id,
                WorkflowVersion.status == "active",
            )
        ).scalar_one_or_none()
    if existing_active_workflow is not None and existing_active_version is not None:
        return {"created": False, "product_code": "PLD", "workflow_code": "standard"}

    users = {
        user.username: user for user in session.execute(select(User)).scalars().all()
    }
    negocio = users.get("negocio")
    riesgos = users.get("riesgos")
    if negocio is None or riesgos is None:
        raise ValueError("PLD runtime seed requires seeded local users 'negocio' and 'riesgos'.")

    product = session.get(LoanProduct, "PLD")
    if product is None:
        product = LoanProduct(
            code="PLD",
            name="Prestamo de Libre Disponibilidad",
            description="Bootstrap local transitorio del runtime PLD.",
            status="active",
            is_active=True,
            created_by=negocio.id,
            activated_by=riesgos.id,
            activated_at=now,
            created_at=now,
        )
        session.add(product)
    else:
        product.name = "Prestamo de Libre Disponibilidad"
        product.description = "Bootstrap local transitorio del runtime PLD."
        product.status = "active"
        product.is_active = True
        product.activated_by = riesgos.id
        product.activated_at = now

    workflow = session.execute(
        select(ProductWorkflow).where(
            ProductWorkflow.product_code == "PLD",
            ProductWorkflow.workflow_code == "standard",
        )
    ).scalar_one_or_none()
    if workflow is None:
        workflow = ProductWorkflow(
            id=PLD_RUNTIME_IDS["workflow"],
            product_code="PLD",
            workflow_code="standard",
            name="Workflow standard",
            description="Bootstrap local transitorio del workflow PLD.",
            status="active",
            created_by=negocio.id,
            activated_by=riesgos.id,
            activated_at=now,
            created_at=now,
        )
        session.add(workflow)
    else:
        workflow.status = "active"
        workflow.name = "Workflow standard"
        workflow.description = "Bootstrap local transitorio del workflow PLD."
        workflow.activated_by = riesgos.id
        workflow.activated_at = now

    variable_ids: dict[str, str] = {}
    for variable_key, allowed_source, is_required in PLD_VARIABLE_DEFINITIONS:
        variable = session.execute(
            select(ProductVariable).where(
                ProductVariable.product_code == "PLD",
                ProductVariable.variable_key == variable_key,
            )
        ).scalar_one_or_none()
        if variable is None:
            variable = ProductVariable(
                id=f"var-{variable_key}",
                product_code="PLD",
                variable_key=variable_key,
                name=variable_key,
                business_meaning=variable_key,
                description=f"Variable {variable_key}",
                data_type=(
                    "number"
                    if variable_key
                    in {
                        "validated_income",
                        "reported_debt",
                        "initial_offered_amount",
                        "existing_consumption_balance",
                        "campaign_rate",
                    }
                    else "integer" if variable_key == "campaign_term_months" else "string"
                ),
                is_required=is_required,
                allowed_sources=allowed_source,
                status="active",
                created_by=negocio.id,
                activated_by=riesgos.id,
                activated_at=now,
                created_at=now,
            )
            session.add(variable)
        else:
            variable.status = "active"
            variable.allowed_sources = allowed_source
            variable.is_required = is_required
            variable.activated_by = riesgos.id
            variable.activated_at = now
        variable_ids[variable_key] = variable.id

    catalog = session.get(VariableCatalogVersion, PLD_RUNTIME_IDS["catalog"])
    if catalog is None:
        catalog = VariableCatalogVersion(
            id=PLD_RUNTIME_IDS["catalog"],
            product_code="PLD",
            version_number=1,
            status="active",
            created_by=negocio.id,
            activated_by=riesgos.id,
            activated_at=now,
            created_at=now,
        )
        session.add(catalog)
    else:
        catalog.status = "active"
        catalog.activated_by = riesgos.id
        catalog.activated_at = now
    session.flush()

    for variable_key, allowed_source, is_required in PLD_VARIABLE_DEFINITIONS:
        item = session.execute(
            select(VariableCatalogItem).where(
                VariableCatalogItem.catalog_version_id == catalog.id,
                VariableCatalogItem.product_variable_id == variable_ids[variable_key],
            )
        ).scalar_one_or_none()
        if item is None:
            session.add(
                VariableCatalogItem(
                    id=str(uuid4()),
                    catalog_version_id=catalog.id,
                    product_variable_id=variable_ids[variable_key],
                    is_required_in_runtime=is_required,
                    default_value=None,
                    source_policy_payload=json.dumps({"allowedSource": allowed_source}),
                )
            )
        else:
            item.is_required_in_runtime = is_required
            item.source_policy_payload = json.dumps({"allowedSource": allowed_source})

    parameter_set = session.get(ParameterSet, PLD_RUNTIME_IDS["parameter_set"])
    if parameter_set is None:
        parameter_set = ParameterSet(
            id=PLD_RUNTIME_IDS["parameter_set"],
            product_code="PLD",
            workflow_code="standard",
            version_number=1,
            status="active",
            payload=json.dumps({"min_score": 500}),
            created_by=riesgos.id,
            activated_by=riesgos.id,
            activated_at=now,
            created_at=now,
        )
        session.add(parameter_set)
    else:
        parameter_set.status = "active"
        parameter_set.payload = json.dumps({"min_score": 500})
        parameter_set.activated_by = riesgos.id
        parameter_set.activated_at = now

    graph_definition = {
        "start_node_key": "collect_context",
        "next_node_map": {
            "collect_context": {"collected": "check_eligibility"},
            "check_eligibility": {"eligible": "calculate_metrics"},
            "calculate_metrics": {"calculated": "build_decision"},
            "build_decision": {},
        },
    }
    pipeline_strategy = session.get(PipelineStrategy, PLD_RUNTIME_IDS["pipeline"])
    if pipeline_strategy is None:
        pipeline_strategy = PipelineStrategy(
            id=PLD_RUNTIME_IDS["pipeline"],
            loan_product_code="PLD",
            version_number=1,
            graph_definition=json.dumps(graph_definition),
            status="active",
            approved_by=riesgos.id,
            created_by=riesgos.id,
            created_at=now,
        )
        session.add(pipeline_strategy)
    else:
        pipeline_strategy.status = "active"
        pipeline_strategy.graph_definition = json.dumps(graph_definition)
        pipeline_strategy.approved_by = riesgos.id

    for node_key, node_type in (
        ("collect_context", "context"),
        ("check_eligibility", "eligibility"),
        ("calculate_metrics", "metrics"),
        ("build_decision", "decision"),
    ):
        node = session.execute(
            select(PipelineNode).where(
                PipelineNode.pipeline_strategy_id == PLD_RUNTIME_IDS["pipeline"],
                PipelineNode.node_key == node_key,
            )
        ).scalar_one_or_none()
        if node is None:
            session.add(
                PipelineNode(
                    id=str(uuid4()),
                    pipeline_strategy_id=PLD_RUNTIME_IDS["pipeline"],
                    node_key=node_key,
                    node_type=node_type,
                    position_x=0,
                    position_y=0,
                    config_payload=json.dumps({}),
                    created_at=now,
                )
            )
        else:
            node.node_type = node_type
            node.config_payload = json.dumps({})

    rule_version_ids: list[str] = []
    for index, (rule_key, rule_type) in enumerate(PLD_RULE_DEFINITIONS, start=1):
        rule_set_id = f"rule-set-{index}"
        rule_version_id = f"rule-version-{index}"
        rule_version_ids.append(rule_version_id)
        rule_set = session.get(RuleSet, rule_set_id)
        if rule_set is None:
            rule_set = RuleSet(
                id=rule_set_id,
                loan_product_code="PLD",
                name=rule_key,
                description=rule_key,
                effective_from=now,
                status="active",
                is_active=True,
                created_by=riesgos.id,
                activated_by=riesgos.id,
                activated_at=now,
                created_at=now,
            )
            session.add(rule_set)
        else:
            rule_set.status = "active"
            rule_set.is_active = True
            rule_set.activated_by = riesgos.id
            rule_set.activated_at = now

        rule_version = session.get(RuleVersion, rule_version_id)
        if rule_version is None:
            session.add(
                RuleVersion(
                    id=rule_version_id,
                    rule_set_id=rule_set_id,
                    version_number=1,
                    rule_key=rule_key,
                    rule_name=rule_key,
                    rule_type=rule_type,
                    condition_expression="true",
                    action_expression="allow",
                    parameters=json.dumps({}),
                    status="active",
                    approved_by=riesgos.id,
                    created_by=riesgos.id,
                    created_at=now,
                )
            )
        else:
            rule_version.rule_type = rule_type
            rule_version.condition_expression = "true"
            rule_version.action_expression = "allow"
            rule_version.parameters = json.dumps({})
            rule_version.status = "active"
            rule_version.approved_by = riesgos.id

    workflow_version = session.get(WorkflowVersion, PLD_RUNTIME_IDS["workflow_version"])
    if workflow_version is None:
        workflow_version = WorkflowVersion(
            id=PLD_RUNTIME_IDS["workflow_version"],
            workflow_id=workflow.id,
            version_number=1,
            status="active",
            variable_catalog_version_id=catalog.id,
            parameter_set_id=parameter_set.id,
            pipeline_strategy_id=pipeline_strategy.id,
            change_notes="Bootstrap local transitorio del runtime PLD.",
            created_by=negocio.id,
            activated_by=riesgos.id,
            activated_at=now,
            created_at=now,
        )
        session.add(workflow_version)
    else:
        workflow_version.workflow_id = workflow.id
        workflow_version.status = "active"
        workflow_version.variable_catalog_version_id = catalog.id
        workflow_version.parameter_set_id = parameter_set.id
        workflow_version.pipeline_strategy_id = pipeline_strategy.id
        workflow_version.activated_by = riesgos.id
        workflow_version.activated_at = now

    session.flush()
    for execution_order, rule_version_id in enumerate(rule_version_ids, start=1):
        assignment = session.execute(
            select(WorkflowRuleAssignment).where(
                WorkflowRuleAssignment.workflow_version_id == workflow_version.id,
                WorkflowRuleAssignment.rule_version_id == rule_version_id,
            )
        ).scalar_one_or_none()
        if assignment is None:
            session.add(
                WorkflowRuleAssignment(
                    id=str(uuid4()),
                    workflow_version_id=workflow_version.id,
                    rule_version_id=rule_version_id,
                    execution_order=execution_order,
                    is_active=True,
                )
            )
        else:
            assignment.execution_order = execution_order
            assignment.is_active = True

    session.commit()
    return {"created": True, "product_code": "PLD", "workflow_code": "standard"}


def seed_identity_data_for_local_dev() -> dict[str, int]:
    engine = get_engine()
    Base.metadata.create_all(bind=engine)

    session_factory = get_session_factory()
    with session_factory() as session:
        return seed_identity_data(session)


def seed_local_runtime_for_local_dev() -> dict[str, bool | str]:
    engine = get_engine()
    Base.metadata.create_all(bind=engine)

    session_factory = get_session_factory()
    with session_factory() as session:
        seed_identity_data(session)
        return seed_pld_runtime_bundle(session)


if __name__ == "__main__":
    result = seed_identity_data_for_local_dev()
    runtime_result = seed_local_runtime_for_local_dev()
    print(
        "Seed complete: "
        f"roles_created={result['roles_created']}, "
        f"users_created={result['users_created']}"
    )
    print(
        "Runtime bootstrap: "
        f"created={runtime_result['created']}, "
        f"product_code={runtime_result['product_code']}, "
        f"workflow_code={runtime_result['workflow_code']}"
    )
