# Checklist: Motor Administrable Requirements Review

**Purpose**: Validar la calidad de los requisitos del motor administrable antes de planificar cambios sobre productos, workflows, reglas, variables y permisos.
**Created**: 2026-06-11
**Feature**: [spec.md](../spec.md)

## Requirement Completeness

- [x] CHK001 - Are the required attributes for a product definition explicitly specified beyond its existence as an entity? [Gap, Spec §Key Entities, Spec §FR-022]
- [x] CHK002 - Are the required attributes for a workflow definition documented, including how it is distinguished within a product? [Completeness, Spec §Key Entities, Spec §FR-023]
- [x] CHK003 - Are the minimum required attributes for a rule documented beyond lifecycle state alone? [Gap, Spec §Key Entities, Spec §FR-031, Spec §FR-032]
- [x] CHK004 - Are the required attributes for a variable definition specified, including identity, business meaning, and allowed source configuration? [Completeness, Spec §Key Entities, Spec §FR-027, Spec §FR-029]
- [x] CHK005 - Are permission requirements defined for which roles may create, activate, retire, and version products, workflows, rules, and variables? [Gap, Spec §FR-026, Spec §FR-034, Spec §FR-036]

## Requirement Clarity

- [x] CHK006 - Is "without requiring code changes as a normal operating mechanism" specific enough to distinguish permitted administration from exceptional TI intervention? [Clarity, Spec §FR-022]
- [x] CHK007 - Is the lifecycle `draft -> active -> retired` defined with entry and exit criteria for each state? [Clarity, Spec §FR-024, Spec §FR-032]
- [x] CHK008 - Is "select which variables a workflow uses" precise enough to determine whether selection includes ordering, mandatory flags, or merely inclusion? [Ambiguity, Spec §FR-028]
- [x] CHK009 - Is "allowed source" for variables defined clearly enough to determine whether source choice is fixed at design time or resolved per evaluation? [Clarity, Spec §FR-029, Spec §Assumptions]
- [x] CHK010 - Is "new version" defined clearly enough to distinguish version creation from edit, clone, or replacement? [Ambiguity, Spec §FR-035, Spec §Key Entities]

## Requirement Consistency

- [x] CHK011 - Do lifecycle requirements for products, workflows, and rules align consistently, or are there hidden differences in governance expectations? [Consistency, Spec §FR-024, Spec §FR-032]
- [x] CHK012 - Are the assumptions about business/risk autonomy consistent with the authorization requirements for administrative actions? [Consistency, Spec §Assumptions, Spec §FR-036]
- [x] CHK013 - Do traceability requirements for products, workflows, and rules use consistent audit expectations across all administrative entities? [Consistency, Spec §FR-026, Spec §FR-034, Spec §SC-007, Spec §SC-008]
- [x] CHK014 - Are the statements about active-only operational use consistent between products, workflows, rules, and workflow version immutability? [Consistency, Spec §FR-025, Spec §FR-033, Spec §FR-035, Spec §Edge Cases]

## Acceptance Criteria Quality

- [x] CHK015 - Can the autonomy goal for business and risk teams be objectively verified from the current success criteria? [Measurability, Spec §Summary, Spec §Assumptions, Spec §Success Criteria]
- [x] CHK016 - Are the success criteria sufficient to measure administrative correctness for variable sourcing and workflow versioning? [Gap, Spec §SC-007, Spec §SC-008, Spec §SC-009]
- [x] CHK017 - Do the success criteria distinguish configuration quality from runtime evaluation outcomes clearly enough for reviewers? [Clarity, Spec §Success Criteria, Spec §FR-022 to §FR-035]

## Scenario Coverage

- [x] CHK018 - Are requirements defined for the full administrative journey from creating a product to activating its first workflow and rules? [Coverage, Gap]
- [x] CHK019 - Are requirements defined for alternate administrative scenarios such as adding a new workflow to an existing product? [Coverage, Spec §FR-023, Spec §FR-031]
- [x] CHK020 - Are requirements defined for exception scenarios where activation should be blocked because configuration is incomplete or invalid? [Gap, Spec §FR-024, Spec §FR-032]
- [x] CHK021 - Are requirements defined for recovery scenarios, such as replacing an active workflow version after an incorrect configuration is detected? [Coverage, Gap, Spec §FR-035]

## Edge Case Coverage

- [x] CHK022 - Does the spec define what happens when a product has no active workflows? [Edge Case, Gap]
- [x] CHK023 - Does the spec define whether multiple workflows of the same product may be active simultaneously? [Gap, Spec §FR-023, Spec §FR-025]
- [x] CHK024 - Does the spec define how conflicting or duplicate variable definitions within a product are prevented or resolved? [Edge Case, Gap, Spec §FR-027]
- [x] CHK025 - Does the spec define what happens when a rule references a variable that is later retired or source-restricted? [Coverage, Gap, Spec §FR-029, Spec §FR-032]

## Non-Functional Requirements

- [x] CHK026 - Are authorization requirements specified deeply enough for administrative segregation of duties between business, risk, and other privileged roles? [Non-Functional, Spec §FR-036, Spec §Assumptions]
- [x] CHK027 - Are auditability requirements specified deeply enough to define what administrative events must be recorded and retained? [Non-Functional, Spec §FR-026, Spec §FR-034, Spec §SC-007]
- [x] CHK028 - Are reproducibility requirements specified for how historical evaluations remain attributable to the exact workflow and rule versions used? [Non-Functional, Spec §FR-011, Spec §FR-035, Spec §SC-009]

## Dependencies & Assumptions

- [x] CHK029 - Are dependencies on campaign data sources specified well enough to define administrative responsibilities when a variable depends on external campaign data? [Dependency, Spec §FR-029, Spec §Assumptions]
- [x] CHK030 - Is the assumption that business and risk teams can operate the motor without routine TI intervention supported by explicit governance boundaries? [Assumption, Spec §Assumptions, Spec §FR-022]

## Ambiguities & Conflicts

- [x] CHK031 - Is it clear whether variable administration itself follows a lifecycle comparable to products, workflows, and rules, or is that currently unspecified? [Ambiguity, Gap, Spec §FR-027 to §FR-030]
- [x] CHK032 - Is it clear whether retiring a product implicitly retires its workflows and rules, or could contradictory states remain possible? [Conflict, Gap, Spec §FR-024, Spec §FR-032]
