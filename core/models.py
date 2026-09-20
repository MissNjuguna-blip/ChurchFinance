from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.models import Expense, AuditLog
from core.audit import create_audit_log
from finances.serializer import ExpenseSerializer

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Automatically assign the request user to 'recorded_by'
        expense = serializer.save(recorded_by=self.request.user)

        create_audit_log(
            user=self.request.user,
            action=AuditLog.Action.CREATE,
            instance=expense,
            description=(
                f"Recorded expense of {expense.amount} "
                f"for '{expense.description}'"
            )
        )

    def perform_update(self, serializer):
        expense = serializer.save()

        create_audit_log(
            user=self.request.user,
            action=AuditLog.Action.UPDATE,
            instance=expense,
            description=(
                f"Updated expense #{expense.id} ('{expense.description}') "
                f"to amount: {expense.amount}"
            )
        )

    def perform_destroy(self, instance):
        expense_id = instance.id
        amount = instance.amount
        description = instance.description

        create_audit_log(
            user=self.request.user,
            action=AuditLog.Action.DELETE,
            instance=instance,
            description=(
                f"Deleted expense #{expense_id} "
                f"of {amount} ('{description}')"
            )
        )

        instance.delete()
