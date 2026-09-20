from decimal import Decimal
from datetime import datetime

from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncMonth
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from core.models import Member, Contribution, Expense


User = get_user_model()


# =========================================================
# REGISTER
# =========================================================

@api_view(["POST"])
@permission_classes([AllowAny])
@transaction.atomic
def register(request):

    first_name = request.data.get("first_name")
    last_name = request.data.get("last_name")
    password = request.data.get("password")
    phone_number = request.data.get("phone_number")

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not first_name:
        return Response(
            {
                "error": "First name is required."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if not last_name:
        return Response(
            {
                "error": "Last name is required."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if not password:
        return Response(
            {
                "error": "Password is required."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if not phone_number:
        return Response(
            {
                "error": "Phone number is required."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # -----------------------------------------------------
    # CHECK EXISTING PHONE NUMBER
    # -----------------------------------------------------

    if User.objects.filter(
        phone_number=phone_number
    ).exists():

        return Response(
            {
                "error": "A user with this phone number already exists."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # -----------------------------------------------------
    # CREATE USER
    # -----------------------------------------------------

    user = User.objects.create_user(
        phone_number=phone_number,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_staff=True,
        is_active=True
    )

    return Response(
        {
            "message": "Admin registered successfully.",

            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone_number": user.phone_number,
                "is_staff": user.is_staff,
                "is_active": user.is_active,
            }
        },
        status=status.HTTP_201_CREATED
    )


# =========================================================
# LOGIN
# =========================================================

@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):

    phone_number = request.data.get("phone_number")
    password = request.data.get("password")

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not phone_number:
        return Response(
            {
                "error": "Phone number is required."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if not password:
        return Response(
            {
                "error": "Password is required."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # -----------------------------------------------------
    # AUTHENTICATE
    # -----------------------------------------------------

    user = authenticate(
        request=request,
        username=phone_number,
        password=password
    )

    if user is None:
        return Response(
            {
                "error": "Invalid phone number or password."
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    # -----------------------------------------------------
    # CHECK ACTIVE STATUS
    # -----------------------------------------------------

    if not user.is_active:
        return Response(
            {
                "error": "This account is inactive."
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # -----------------------------------------------------
    # CREATE JWT TOKENS
    # -----------------------------------------------------

    refresh = RefreshToken.for_user(user)

    access_token = refresh.access_token

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return Response(
        {
            "message": "Login successful.",

            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone_number": user.phone_number,
                "is_staff": user.is_staff,
                "is_active": user.is_active,
            },

            "refresh": str(refresh),

            "access_token": str(access_token),
        },

        status=status.HTTP_200_OK
    )


# =========================================================
# LOGOUT
# =========================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):

    # -----------------------------------------------------
    # GET REFRESH TOKEN
    # -----------------------------------------------------

    refresh_token = request.data.get("refresh")

    if not refresh_token:
        return Response(
            {
                "error": "Refresh token is required."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # -----------------------------------------------------
    # BLACKLIST REFRESH TOKEN
    # -----------------------------------------------------

    try:

        token = RefreshToken(refresh_token)

        token.blacklist()

        return Response(
            {
                "message": "Successfully logged out."
            },
            status=status.HTTP_205_RESET_CONTENT
        )

    except TokenError:

        return Response(
            {
                "error": "Invalid or expired refresh token."
            },
            status=status.HTTP_400_BAD_REQUEST
        )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_dashboard(request):

    current_user = request.user

    
    date_string = request.query_params.get("date")

    if date_string:

        try:
            selected_date = datetime.strptime(
                date_string,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            return Response(
                {
                    "error": (
                        "Invalid date format. "
                        "Use YYYY-MM-DD."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    else:

        selected_date = timezone.localdate()

    # =====================================================
    # TOTAL MEMBERS
    # =====================================================

    total_members = Member.objects.count()

    # =====================================================
    # ALL-TIME CONTRIBUTIONS
    # =====================================================

    contribution_stats = Contribution.objects.aggregate(
        total=Sum("amount"),
        count=Count("id"),
        average=Avg("amount")
    )

    total_contributions = (
        contribution_stats["total"]
        or Decimal("0.00")
    )

    contribution_count = (
        contribution_stats["count"]
        or 0
    )

    average_contribution = (
        contribution_stats["average"]
        or Decimal("0.00")
    )

    # =====================================================
    # ALL-TIME EXPENSES
    # =====================================================

    expense_stats = (
        Expense.objects
        .filter(
            status=Expense.Status.PAID
        )
        .aggregate(
            total=Sum("amount"),
            count=Count("id"),
            average=Avg("amount")
        )
    )

    total_expenses = (
        expense_stats["total"]
        or Decimal("0.00")
    )

    expense_count = (
        expense_stats["count"]
        or 0
    )

    average_expense = (
        expense_stats["average"]
        or Decimal("0.00")
    )

    # =====================================================
    # ALL-TIME CURRENT BALANCE
    # =====================================================

    current_balance = (
        total_contributions
        - total_expenses
    )

    # =====================================================
    # SELECTED DAY CONTRIBUTIONS
    # =====================================================

    daily_contribution_stats = (
        Contribution.objects
        .filter(
            contribution_date=selected_date
        )
        .aggregate(
            total=Sum("amount"),
            count=Count("id"),
            average=Avg("amount")
        )
    )

    daily_contributions = (
        daily_contribution_stats["total"]
        or Decimal("0.00")
    )

    daily_contribution_count = (
        daily_contribution_stats["count"]
        or 0
    )

    daily_average_contribution = (
        daily_contribution_stats["average"]
        or Decimal("0.00")
    )

    # =====================================================
    # SELECTED DAY EXPENSES
    # =====================================================

    daily_expense_stats = (
        Expense.objects
        .filter(
            expense_date=selected_date,
            status=Expense.Status.PAID
        )
        .aggregate(
            total=Sum("amount"),
            count=Count("id"),
            average=Avg("amount")
        )
    )

    daily_expenses = (
        daily_expense_stats["total"]
        or Decimal("0.00")
    )

    daily_expense_count = (
        daily_expense_stats["count"]
        or 0
    )

    daily_average_expense = (
        daily_expense_stats["average"]
        or Decimal("0.00")
    )

    # =====================================================
    # SELECTED DAY BALANCE
    # =====================================================

    daily_balance = (
        daily_contributions
        - daily_expenses
    )

    # =====================================================
    # RECENT CONTRIBUTIONS
    # =====================================================

    recent_contributions = (
        Contribution.objects
        .select_related(
            "member",
            "contribution_type",
            "recorded_by"
        )
        .order_by(
            "-contribution_date",
            "-created_at"
        )[:10]
    )

    recent_contributions_data = []

    for contribution in recent_contributions:

        member_name = None

        if contribution.member:

            member_name = (
                f"{contribution.member.first_name} "
                f"{contribution.member.last_name}"
            ).strip()

        recorded_by = None

        if contribution.recorded_by:

            recorded_by = {
                "id": contribution.recorded_by.id,

                "name": (
                    f"{contribution.recorded_by.first_name} "
                    f"{contribution.recorded_by.last_name}"
                ).strip(),

                "phone_number": (
                    contribution.recorded_by.phone_number
                ),
            }

        recent_contributions_data.append({

            "id": contribution.id,

            "member_id": (
                contribution.member.id
                if contribution.member
                else None
            ),

            "member_name": member_name,

            "contribution_type": (
                contribution.contribution_type.name
            ),

            "amount": str(
                contribution.amount
            ),

            "contribution_date": (
                contribution.contribution_date.isoformat()
            ),

            "payment_method": (
                contribution.payment_method
            ),

            "recorded_by": recorded_by,
        })

    # =====================================================
    # RECENT EXPENSES
    # =====================================================

    recent_expenses = (
        Expense.objects
        .select_related("recorded_by")
        .order_by(
            "-expense_date",
            "-created_at"
        )[:10]
    )

    recent_expenses_data = []

    for expense in recent_expenses:

        recorded_by = None

        if expense.recorded_by:

            recorded_by = {
                "id": expense.recorded_by.id,

                "name": (
                    f"{expense.recorded_by.first_name} "
                    f"{expense.recorded_by.last_name}"
                ).strip(),

                "phone_number": (
                    expense.recorded_by.phone_number
                ),
            }

        recent_expenses_data.append({

            "id": expense.id,

            "description": expense.description,

            "amount": str(
                expense.amount
            ),

            "expense_date": (
                expense.expense_date.isoformat()
            ),

            "payment_method": (
                expense.payment_method
            ),

            "status": expense.status,

            "reference": expense.reference,

            "recorded_by": recorded_by,
        })

    # =====================================================
    # RECENT MEMBERS
    # =====================================================

    recent_members = (
        Member.objects
        .order_by("-created_at")[:10]
    )

    recent_members_data = []

    for member in recent_members:

        full_name = (
            f"{member.first_name} "
            f"{member.last_name}"
        ).strip()

        recent_members_data.append({

            "id": member.id,

            "full_name": full_name,

            "first_name": member.first_name,

            "last_name": member.last_name,

            "created_at": (
                member.created_at.isoformat()
            ),

            "updated_at": (
                member.updated_at.isoformat()
            ),
        })

    # =====================================================
    # MONTHLY CONTRIBUTIONS
    # =====================================================

    monthly_contributions = (
        Contribution.objects
        .annotate(
            month=TruncMonth(
                "contribution_date"
            )
        )
        .values("month")
        .annotate(
            total=Sum("amount"),
            count=Count("id")
        )
        .order_by("month")
    )

    monthly_contribution_data = []

    for item in monthly_contributions:

        monthly_contribution_data.append({

            "month": item["month"].strftime(
                "%Y-%m"
            ),

            "total": str(
                item["total"]
                or Decimal("0.00")
            ),

            "count": item["count"],
        })

    # =====================================================
    # MONTHLY EXPENSES
    # =====================================================

    monthly_expenses = (
        Expense.objects
        .filter(
            status=Expense.Status.PAID
        )
        .annotate(
            month=TruncMonth(
                "expense_date"
            )
        )
        .values("month")
        .annotate(
            total=Sum("amount"),
            count=Count("id")
        )
        .order_by("month")
    )

    monthly_expense_data = []

    for item in monthly_expenses:

        monthly_expense_data.append({

            "month": item["month"].strftime(
                "%Y-%m"
            ),

            "total": str(
                item["total"]
                or Decimal("0.00")
            ),

            "count": item["count"],
        })

    # =====================================================
    # RESPONSE
    # =====================================================

    return Response(

        {

            # =================================================
            # USER
            # =================================================

            "user": {

                "id": current_user.id,

                "first_name": (
                    current_user.first_name
                ),

                "last_name": (
                    current_user.last_name
                ),

                "phone_number": (
                    current_user.phone_number
                ),

                "is_staff": (
                    current_user.is_staff
                ),

                "is_active": (
                    current_user.is_active
                ),
            },

            # =================================================
            # DASHBOARD SUMMARY
            #
            # These are ALL-TIME totals.
            # =================================================

            "summary": {

                "total_members":
                    total_members,

                "total_contributions":
                    str(total_contributions),

                "contribution_count":
                    contribution_count,

                "average_contribution":
                    str(average_contribution),

                "total_expenses":
                    str(total_expenses),

                "expense_count":
                    expense_count,

                "average_expense":
                    str(average_expense),

                "current_balance":
                    str(current_balance),
            },

            # =================================================
            # DAILY SUMMARY
            #
            # These are for the selected date.
            # =================================================

            "daily_summary": {

                "date":
                    selected_date.isoformat(),

                "contributions":
                    str(daily_contributions),

                "contribution_count":
                    daily_contribution_count,

                "average_contribution":
                    str(daily_average_contribution),

                "expenses":
                    str(daily_expenses),

                "expense_count":
                    daily_expense_count,

                "average_expense":
                    str(daily_average_expense),

                "balance":
                    str(daily_balance),
            },

            # =================================================
            # RECENT DATA
            # =================================================

            "recent_contributions":
                recent_contributions_data,

            "recent_expenses":
                recent_expenses_data,

            "recent_members":
                recent_members_data,

            # =================================================
            # CHART DATA
            # =================================================

            "monthly_contributions":
                monthly_contribution_data,

            "monthly_expenses":
                monthly_expense_data,
        },

        status=status.HTTP_200_OK
    )
