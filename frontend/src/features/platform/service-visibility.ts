import type { PlatformService } from "./catalog-types";
import { platformServices } from "./platform-seed-data";

export const ENGINE_MANAGER_ROLES = ["admin", "admin_negocio", "admin_riesgos"] as const;

export function canManageEngine(roles: string[]): boolean {
  return roles.some((role) => ENGINE_MANAGER_ROLES.includes(role as (typeof ENGINE_MANAGER_ROLES)[number]));
}

export function isServiceVisibleToRoles(service: PlatformService, roles: string[]): boolean {
  return roles.some((role) => service.visibilityRoles.includes(role));
}

export function getVisibleServicesForRoles(roles: string[]): PlatformService[] {
  return platformServices.filter((service) => isServiceVisibleToRoles(service, roles));
}

export function findVisibleServiceForRoles(
  roles: string[],
  serviceIdentifier: string,
): PlatformService | null {
  const normalizedIdentifier = serviceIdentifier.trim().toLowerCase();

  return (
    getVisibleServicesForRoles(roles).find(
      (service) =>
        service.routeSegment.toLowerCase() === normalizedIdentifier ||
        service.serviceKey.toLowerCase() === normalizedIdentifier,
    ) ?? null
  );
}
