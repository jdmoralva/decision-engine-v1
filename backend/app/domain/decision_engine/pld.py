import math

from backend.app.domain.decision_engine.contracts import AppliedVersions
from backend.app.domain.decision_engine.nodes import DecisionNode, NodeExecutionResult
from backend.app.domain.decision_engine.normalization import normalize_evaluation_request
from backend.app.domain.decision_engine.pipeline import PipelineNodeDefinition, PipelineStrategy
from backend.app.domain.decision_engine.runtime_definitions import (
    ProductDefinition,
    ProductRuntime,
    RuleDefinition,
    VariableDefinition,
    WorkflowDefinition,
    compile_product_runtime,
)


PROFILE_TEA_BY_NUMBER = {
    1: 0.30,
    2: 0.35,
}


def _product_context_value(context, key: str, default=None):
    return context.request.product_context.get(key, default)


def _parse_profile_number(profile_code: str | None) -> int:
    if profile_code is None:
        return 3
    digits = "".join(char for char in profile_code if char.isdigit())
    if not digits:
        return 3
    return int(digits)


def _income_range(income: float) -> int:
    if income <= 1000:
        return 0
    if income <= 2000:
        return 1
    if income <= 3000:
        return 2
    if income <= 4000:
        return 3
    if income <= 5000:
        return 4
    if income <= 7000:
        return 5
    return 6


def _segment_code(sunedu_flag: str | None, employment_status: str | None) -> str:
    sunedu_segment = "CS" if (sunedu_flag or "").strip().upper() == "CON SUNEDU" else "SS"
    labor_segment = "DEP" if (employment_status or "").strip().upper() == "DEP" else "INDEP"
    return f"{sunedu_segment}_{labor_segment}"


def _annual_rate_for_profile(profile_number: int) -> float:
    return PROFILE_TEA_BY_NUMBER.get(profile_number, 0.40)


def _monthly_rate(annual_rate: float) -> float:
    return math.exp(math.log(1 + annual_rate) / 12) - 1


def _resolve_param_pld(profile_number: int, income_range: int) -> float:
    return {1: 0.46, 2: 0.50}.get(profile_number, 0.54) + (0.01 * income_range)


def _resolve_multip_nvi(profile_number: int, income_range: int, segment_code: str) -> float:
    return {1: 3.8, 2: 4.0}.get(profile_number, 4.2) + (0.2 * income_range) + (
        0.2 if segment_code.endswith("DEP") else 0
    )


def _resolve_offer3(
    profile_number: int, income_range: int, is_existing_customer: bool, segment_code: str
) -> float:
    return (
        7000
        + (profile_number * 1000)
        + (income_range * 1000)
        + (500 if is_existing_customer else 0)
        + (500 if segment_code.startswith("CS") else 0)
    )


def _resolve_tope_garita(profile_number: int, segment_code: str) -> float:
    return 2000 + (profile_number * 500) + (500 if segment_code.endswith("DEP") else 0)


def _resolve_term_months(income: float, campaign_term_months: int | None) -> int:
    if campaign_term_months is not None:
        return int(campaign_term_months)
    return 48 if income >= 2000 else 36


def _round_offer(amount: float) -> float:
    return float(round(amount, -2))


class CollectContextNode(DecisionNode):
    node_key = "collect_context"
    node_type = "context"

    async def run(self, context) -> NodeExecutionResult:
        income = float(_product_context_value(context, "validated_income", 0) or 0)
        profile_number = _parse_profile_number(_product_context_value(context, "profile_code"))
        segment_code = _segment_code(
            _product_context_value(context, "sunedu_flag"),
            _product_context_value(context, "employment_status"),
        )

        context.product_result["segment_code"] = segment_code
        context.product_result["reviewed_income"] = float(income)
        context.product_result["_profile_number"] = profile_number
        context.product_result["_income_range"] = _income_range(income)
        context.product_result["_effective_debt"] = float(
            _product_context_value(context, "reported_debt", 0) or 0
        )
        context.product_result["_segment_code"] = segment_code
        context.product_result["_is_existing_customer"] = (
            (_product_context_value(context, "customer_type", "") or "").strip().upper()
            != "NO CLIENTE"
        )

        return NodeExecutionResult(
            outcome="collected",
            rules_applied=["pld.collect_context"],
            consumed_variables=["campaign_code", "customer_type", "validated_income"],
            produced_variables=["segment_code", "reviewed_income"],
        )


class CheckEligibilityNode(DecisionNode):
    node_key = "check_eligibility"
    node_type = "eligibility"

    async def run(self, context) -> NodeExecutionResult:
        return NodeExecutionResult(
            outcome="eligible",
            eligible=True,
            rules_applied=["pld.check_eligibility"],
            consumed_variables=["customer_type", "employment_status", "sunedu_flag"],
            produced_variables=["segment_code"],
        )


class CalculateMetricsNode(DecisionNode):
    node_key = "calculate_metrics"
    node_type = "metrics"

    async def run(self, context) -> NodeExecutionResult:
        income = float(context.product_result.get("reviewed_income", 0) or 0)
        segment_code = str(context.product_result.get("_segment_code", "SS_INDEP"))
        profile_number = int(context.product_result.get("_profile_number", 3) or 3)
        income_range = int(context.product_result.get("_income_range", _income_range(income)))
        effective_debt = float(context.product_result.get("_effective_debt", 0) or 0)
        initial_offered_amount = float(
            _product_context_value(context, "initial_offered_amount", 0) or 0
        )
        existing_consumption_balance = float(
            _product_context_value(context, "existing_consumption_balance", 0) or 0
        )
        campaign_rate_value = _product_context_value(context, "campaign_rate")
        campaign_rate = (
            float(campaign_rate_value) / 100 if campaign_rate_value is not None else None
        )
        term_months = _resolve_term_months(
            income,
            _product_context_value(context, "campaign_term_months"),
        )
        annual_rate = _annual_rate_for_profile(profile_number)
        tem_pld_48 = _monthly_rate(annual_rate)
        rci = 0.0 if income <= 0 else (effective_debt / income)
        param_pld = _resolve_param_pld(profile_number, income_range)
        multip_nvi = _resolve_multip_nvi(profile_number, income_range, segment_code)
        oferta_1 = round(
            (income * (param_pld - rci)) * (1 - (1 / ((1 + tem_pld_48) ** term_months))) / tem_pld_48,
            2,
        )
        oferta_2 = income * multip_nvi
        oferta_3 = _resolve_offer3(
            profile_number,
            income_range,
            bool(context.product_result.get("_is_existing_customer", False)),
            segment_code,
        )
        tope_garita = _resolve_tope_garita(profile_number, segment_code)
        oferta_pld_ini = min(oferta_1, oferta_2, oferta_3)
        oferta_5 = tope_garita if initial_offered_amount <= tope_garita else initial_offered_amount
        oferta_6 = oferta_5 - existing_consumption_balance
        max_tope_min_6 = max(tope_garita, oferta_6)
        offered_amount = _round_offer(
            oferta_pld_ini if oferta_pld_ini < tope_garita else min(oferta_pld_ini, max_tope_min_6)
        )
        offered_amount = max(offered_amount, 0.0)
        effective_rate = campaign_rate if campaign_rate is not None else annual_rate
        tem_eval = _monthly_rate(effective_rate)
        installment_amount = 0.0
        if offered_amount > 0:
            installment_amount = float(
                round(
                    tem_eval * offered_amount / (1 - (1 / ((1 + tem_eval) ** term_months))),
                    0,
                )
            )

        context.product_result["rci"] = float(round(rci, 4))
        context.product_result["offered_amount"] = float(offered_amount)
        context.product_result["installment_amount"] = float(installment_amount)
        context.product_result["rate"] = float(round(effective_rate, 4))
        context.product_result["term_months"] = int(term_months)

        return NodeExecutionResult(
            outcome="calculated",
            rules_applied=["pld.calculate_metrics"],
            consumed_variables=["validated_income", "reported_debt", "segment_code"],
            produced_variables=[
                "reviewed_income",
                "rci",
                "offered_amount",
                "installment_amount",
                "rate",
                "term_months",
            ],
        )


class BuildDecisionNode(DecisionNode):
    node_key = "build_decision"
    node_type = "decision"

    async def run(self, context) -> NodeExecutionResult:
        reviewed_income = float(context.product_result.get("reviewed_income", 0) or 0)
        offered_amount = float(context.product_result.get("offered_amount", 0) or 0)
        rci = float(context.product_result.get("rci", 0) or 0)
        alerts: list[str] = []
        if reviewed_income < 2000:
            alerts.append("income_below_threshold")
        if offered_amount < 3000:
            alerts.append("offer_below_threshold")
        if rci > 0.5:
            alerts.append("rci_above_threshold")

        return NodeExecutionResult(
            outcome="completed",
            eligible=True,
            rules_applied=["pld.build_decision"],
            consumed_variables=["rci", "offered_amount", "installment_amount"],
            alerts_added=alerts,
            produced_effects=["decision_ready"],
        )


def build_pld_product_definition() -> ProductDefinition:
    workflow_code = "standard"
    product_code = "PLD"
    return ProductDefinition(
        product_code=product_code,
        name="Prestamo de Libre Disponibilidad",
        workflows=[
            WorkflowDefinition(
                workflow_code=workflow_code,
                product_code=product_code,
                name="PLD standard workflow",
                description="Base PLD workflow registered on the generic decision engine.",
                pipeline_version="pld.standard.pipeline.v1",
                rule_pack_version="pld.standard.rules.v1",
                variables=[
                    VariableDefinition(variable_key="campaign_code", variable_kind="input", data_type="string", required=True),
                    VariableDefinition(variable_key="customer_type", variable_kind="input", data_type="string"),
                    VariableDefinition(variable_key="profile_code", variable_kind="input", data_type="string"),
                    VariableDefinition(variable_key="sunedu_flag", variable_kind="input", data_type="string"),
                    VariableDefinition(variable_key="employment_status", variable_kind="input", data_type="string"),
                    VariableDefinition(variable_key="validated_income", variable_kind="input", data_type="number"),
                    VariableDefinition(variable_key="reported_debt", variable_kind="input", data_type="number"),
                    VariableDefinition(variable_key="initial_offered_amount", variable_kind="input", data_type="number"),
                    VariableDefinition(variable_key="existing_consumption_balance", variable_kind="input", data_type="number"),
                    VariableDefinition(variable_key="campaign_rate", variable_kind="input", data_type="number"),
                    VariableDefinition(variable_key="campaign_term_months", variable_kind="input", data_type="integer"),
                    VariableDefinition(variable_key="segment_code", variable_kind="derived", data_type="string"),
                    VariableDefinition(variable_key="reviewed_income", variable_kind="metric", data_type="number"),
                    VariableDefinition(variable_key="rci", variable_kind="metric", data_type="number"),
                    VariableDefinition(variable_key="offered_amount", variable_kind="metric", data_type="number"),
                    VariableDefinition(variable_key="installment_amount", variable_kind="metric", data_type="number"),
                    VariableDefinition(variable_key="rate", variable_kind="metric", data_type="number"),
                    VariableDefinition(variable_key="term_months", variable_kind="metric", data_type="integer"),
                ],
                rules=[
                    RuleDefinition(
                        rule_code="pld.collect_context",
                        rule_type="derivation",
                        product_code=product_code,
                        workflow_code=workflow_code,
                        consumes_variables=["campaign_code", "customer_type", "validated_income"],
                        version="1",
                        priority=10,
                    ),
                    RuleDefinition(
                        rule_code="pld.check_eligibility",
                        rule_type="eligibility",
                        product_code=product_code,
                        workflow_code=workflow_code,
                        consumes_variables=["customer_type", "employment_status", "sunedu_flag"],
                        produces_variable="segment_code",
                        version="1",
                        priority=20,
                    ),
                    RuleDefinition(
                        rule_code="pld.calculate_metrics",
                        rule_type="metric",
                        product_code=product_code,
                        workflow_code=workflow_code,
                        consumes_variables=["validated_income", "reported_debt", "segment_code"],
                        produces_variable="rci",
                        version="1",
                        priority=30,
                    ),
                    RuleDefinition(
                        rule_code="pld.build_decision",
                        rule_type="decision",
                        product_code=product_code,
                        workflow_code=workflow_code,
                        consumes_variables=["rci", "offered_amount", "installment_amount"],
                        produces_effect="decision_ready",
                        version="1",
                        priority=40,
                    ),
                ],
            )
        ],
    )


def build_pld_strategy(workflow_code: str = "standard") -> PipelineStrategy:
    if workflow_code != "standard":
        raise ValueError(f"Unsupported PLD workflow '{workflow_code}'")
    return PipelineStrategy(
        strategy_key="pld.standard",
        product_code="PLD",
        start_node_key="collect_context",
        applied_versions=AppliedVersions(
            rule_set_version="pld.standard.rules.v1",
            parameter_version="pld.standard.parameters.v1",
            pipeline_version="pld.standard.pipeline.v1",
        ),
        nodes=[
            PipelineNodeDefinition(
                node_key="collect_context",
                node_type="context",
                next_node_map={"collected": "check_eligibility"},
            ),
            PipelineNodeDefinition(
                node_key="check_eligibility",
                node_type="eligibility",
                next_node_map={"eligible": "calculate_metrics"},
            ),
            PipelineNodeDefinition(
                node_key="calculate_metrics",
                node_type="metrics",
                next_node_map={"calculated": "build_decision"},
            ),
            PipelineNodeDefinition(
                node_key="build_decision",
                node_type="decision",
                next_node_map={},
            ),
        ],
    )


def build_pld_nodes() -> list[DecisionNode]:
    return [
        CollectContextNode(),
        CheckEligibilityNode(),
        CalculateMetricsNode(),
        BuildDecisionNode(),
    ]


def compile_pld_runtime(workflow_code: str = "standard") -> ProductRuntime:
    return compile_product_runtime(
        product_definition=build_pld_product_definition(),
        workflow_code=workflow_code,
        strategy=build_pld_strategy(workflow_code),
        normalizer=normalize_evaluation_request,
        nodes=build_pld_nodes(),
    )
