from rest_framework.permissions import BasePermission


class IsDonor(BasePermission):
    message = "Доступ разрешён только для доноров"

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "donor"
        )


class IsOrganization(BasePermission):
    message = "Доступ разрешён только для организаций"

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "org"
        )