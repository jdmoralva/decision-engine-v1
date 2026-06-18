export type GovernedStatus = "draft" | "active" | "retired";

const STATUS_LABELS: Record<GovernedStatus, string> = {
  draft: "Borrador",
  active: "Aprobado",
  retired: "Retirado",
};

export function getStatusLabel(status: GovernedStatus | string): string {
  if (status in STATUS_LABELS) {
    return STATUS_LABELS[status as GovernedStatus];
  }

  return status;
}
