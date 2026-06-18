export type ServiceWorkspaceNavItem = {
  key: string;
  label: string;
  section: string;
  item?: string;
  ariaLabel?: string;
};

export type ServiceWorkspaceNavGroup = {
  key: string;
  label: string;
  items: ServiceWorkspaceNavItem[];
};

export type ServiceWorkspaceDefinition = {
  defaultSection: string;
  defaultItem?: string;
  groups: ServiceWorkspaceNavGroup[];
};
