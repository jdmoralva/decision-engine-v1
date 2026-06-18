export type ProductCode = string;

export type ServiceKey = "CreditApplications" | "DecisionEngine" | "DataModel";

export type PlatformProductAction = {
  key: string;
  label: string;
};

export type PlatformProduct = {
  productCode: ProductCode;
  name: string;
  environmentLabel: string;
  environmentTone: "production" | "staging";
  quickActions: PlatformProductAction[];
  menuActions: PlatformProductAction[];
  source: "seed" | "backend";
};

export type PlatformService = {
  serviceKey: ServiceKey;
  routeSegment: string;
  displayName: string;
  description: string;
  statusLabel: string;
  iconKey: string;
  visibilityRoles: string[];
  supportsOpen: boolean;
};
